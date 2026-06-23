from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List


PREDEFINED_KEYS = {"host", "port", "label", "user", "env"}
VALID_NAME = re.compile(r"^[A-Za-z0-9_\-\u4e00-\u9fff]+$")


def safe_query_name(name: str) -> str:
    """新建/保存用：仅允许字母、数字、下划线、连字符与中文，避免路径穿越，也避免文件名带点造成歧义。"""
    stem = Path(str(name)).stem.strip()
    if not stem or not VALID_NAME.match(stem):
        raise ValueError("查询名称只能包含字母、数字、下划线、连字符或中文。")
    return stem


def clean_stem(name: str) -> str:
    """定位已存在的模板文件用：去掉路径与结尾的 .sql，保留中间的点和中文，并防止路径穿越。"""
    candidate = str(name).strip().replace("\\", "/").split("/")[-1]
    if candidate.lower().endswith(".sql"):
        candidate = candidate[:-4]
    candidate = candidate.strip()
    if not candidate or candidate in {".", ".."}:
        raise ValueError("无效的查询名称。")
    return candidate


class SqlLoader:
    def __init__(self, sql_dir: str):
        self.sql_dir = Path(sql_dir)
        self.sql_dir.mkdir(parents=True, exist_ok=True)

    def list_queries(self) -> List[Dict[str, str]]:
        queries = []
        for path in sorted(self.sql_dir.glob("*.sql")):
            sql = self._read(path)
            queries.append({"name": path.stem, "file": path.name, "md5": self.md5(sql), "has_meta": self.has_meta(path.stem)})
        return queries

    def get_query(self, name: str) -> Dict[str, str]:
        try:
            safe_name = clean_stem(name)
        except ValueError as exc:
            raise FileNotFoundError(name) from exc
        path = self.sql_dir / f"{safe_name}.sql"
        if not path.exists():
            raise FileNotFoundError(name)
        sql = self._read(path)
        return {"name": safe_name, "file": path.name, "sql": sql, "md5": self.md5(sql), "has_meta": self.has_meta(safe_name)}

    def has_meta(self, name: str) -> bool:
        try:
            safe_name = clean_stem(name)
        except ValueError:
            return False
        return (self.sql_dir / f"{safe_name}.meta.json").exists()

    def load_meta(self, name: str, value_count: int | None = None) -> List[str]:
        safe_name = clean_stem(name)
        path = self.sql_dir / f"{safe_name}.meta.json"
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                meta = json.load(fh)
            columns = meta.get("columns") or []
            return [str(column) for column in columns]
        count = value_count or 0
        return [f"col_{index}" for index in range(1, count + 1)]

    def meta_path(self, name: str) -> Path:
        return self.sql_dir / f"{clean_stem(name)}.meta.json"

    def save_query(self, name: str, sql: str, columns: List[str] | None = None) -> Dict[str, str]:
        """新增或更新一个 SQL 模板，columns 非空时写入列名映射。"""
        safe_name = safe_query_name(name)
        sql_text = (sql or "").strip()
        if not sql_text:
            raise ValueError("SQL 内容不能为空。")
        (self.sql_dir / f"{safe_name}.sql").write_text(sql_text + "\n", encoding="utf-8")
        cleaned = [str(col).strip() for col in (columns or []) if str(col).strip()]
        meta_path = self.meta_path(safe_name)
        if cleaned:
            with meta_path.open("w", encoding="utf-8") as fh:
                json.dump({"columns": cleaned}, fh, ensure_ascii=False, indent=2)
        elif meta_path.exists():
            meta_path.unlink()
        return self.get_query(safe_name)

    def delete_query(self, name: str) -> None:
        safe_name = clean_stem(name)
        for path in ((self.sql_dir / f"{safe_name}.sql"), self.meta_path(safe_name)):
            if path.exists():
                path.unlink()

    def render(self, sql: str, instance: Dict[str, Any], params: Dict[str, str]) -> str:
        # $${name} 来自 URL 查询参数，${host} 等来自当前实例配置。
        def replace_custom(match: re.Match[str]) -> str:
            key = match.group(1)
            return str(params.get(key, ""))

        def replace_predefined(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in PREDEFINED_KEYS:
                return match.group(0)
            return str(instance.get(key, ""))

        rendered = re.sub(r"\$\$\{([A-Za-z0-9_]+)\}", replace_custom, sql)
        return re.sub(r"\$\{([A-Za-z0-9_]+)\}", replace_predefined, rendered)

    @staticmethod
    def md5(sql: str) -> str:
        return hashlib.md5(sql.encode("utf-8")).hexdigest()

    @staticmethod
    def _read(path: Path) -> str:
        return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    loader = SqlLoader("./sql_templates")
    print(loader.render("SELECT '${host}', '$${keyword}' FROM DUAL", {"host": "127.0.0.1"}, {"keyword": "demo"}))

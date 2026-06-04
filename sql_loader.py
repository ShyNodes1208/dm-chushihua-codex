from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List


PREDEFINED_KEYS = {"host", "port", "label", "user", "env"}


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
        safe_name = Path(name).stem
        path = self.sql_dir / f"{safe_name}.sql"
        if not path.exists():
            raise FileNotFoundError(name)
        sql = self._read(path)
        return {"name": safe_name, "file": path.name, "sql": sql, "md5": self.md5(sql), "has_meta": self.has_meta(safe_name)}

    def has_meta(self, name: str) -> bool:
        return (self.sql_dir / f"{Path(name).stem}.meta.json").exists()

    def load_meta(self, name: str, value_count: int | None = None) -> List[str]:
        safe_name = Path(name).stem
        path = self.sql_dir / f"{safe_name}.meta.json"
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                meta = json.load(fh)
            columns = meta.get("columns") or []
            return [str(column) for column in columns]
        count = value_count or 0
        return [f"col_{index}" for index in range(1, count + 1)]

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

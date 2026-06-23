from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class CacheManager:
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def cache_path(self, query_name: str) -> Path:
        return self.cache_dir / f"{query_name}.json"

    def prev_path(self, query_name: str) -> Path:
        return self.cache_dir / f"{query_name}.prev.json"

    def read(self, query_name: str) -> Optional[Dict[str, Any]]:
        return self._read_path(self.cache_path(query_name))

    def read_prev(self, query_name: str) -> Optional[Dict[str, Any]]:
        return self._read_path(self.prev_path(query_name))

    def write(self, query_name: str, payload: Dict[str, Any]) -> None:
        """写入最新结果，同时把上一次结果保存为快照，供"对比上次"使用。"""
        current = self.read(query_name)
        if current is not None:
            self._write_path(self.prev_path(query_name), current)
        self._write_path(self.cache_path(query_name), payload)

    def delete(self, query_name: str) -> None:
        for path in (self.cache_path(query_name), self.prev_path(query_name)):
            if path.exists():
                path.unlink()

    def status(self, query_name: str, sql_md5: str) -> str:
        cache = self.read(query_name)
        if not cache:
            return "missing"
        if cache.get("sql_md5") != sql_md5:
            return "stale"
        return "valid"

    @staticmethod
    def _read_path(path: Path) -> Optional[Dict[str, Any]]:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    @staticmethod
    def _write_path(path: Path, payload: Dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    manager = CacheManager("./cache")
    manager.write("_selftest", {"sql_md5": "demo"})
    print(manager.status("_selftest", "demo"))

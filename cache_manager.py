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

    def read(self, query_name: str) -> Optional[Dict[str, Any]]:
        path = self.cache_path(query_name)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def write(self, query_name: str, payload: Dict[str, Any]) -> None:
        path = self.cache_path(query_name)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)

    def status(self, query_name: str, sql_md5: str) -> str:
        cache = self.read(query_name)
        if not cache:
            return "missing"
        if cache.get("sql_md5") != sql_md5:
            return "stale"
        return "valid"


if __name__ == "__main__":
    manager = CacheManager("./cache")
    manager.write("_selftest", {"sql_md5": "demo"})
    print(manager.status("_selftest", "demo"))

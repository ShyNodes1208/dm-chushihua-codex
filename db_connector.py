from __future__ import annotations

from typing import Any, Dict, List


def query_instance(instance: Dict[str, Any], sql: str) -> Dict[str, List[Any]]:
    try:
        import dmPython  # type: ignore
    except ImportError as exc:
        raise RuntimeError("dmPython is not installed. Install the Dameng Python driver first.") from exc

    conn = None
    cursor = None
    host = instance.get("host")
    port = int(instance.get("port", 5236))
    user = instance.get("user")
    try:
        connect_args = {
            "user": user,
            "password": instance.get("password"),
            "server": host,
            "port": port,
        }
        timeout = int(instance.get("connect_timeout", 3))
        try:
            conn = dmPython.connect(**connect_args, connect_timeout=timeout)
        except (TypeError, SystemError):
            conn = dmPython.connect(**connect_args)
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [item[0] for item in (cursor.description or [])]
        rows = [list(row) for row in cursor.fetchall()]
        return {"columns": columns, "rows": rows}
    except Exception as exc:
        raise RuntimeError(f"Connect/query failed: {user}@{host}:{port}; {type(exc).__name__}: {exc}") from exc
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    sample = {"host": "127.0.0.1", "port": 5236, "user": "SYSDBA", "password": "SYSDBA"}
    try:
        print(query_instance(sample, "SELECT 1 AS ID FROM DUAL"))
    except Exception as exc:
        print(f"Self test failed: {exc}")

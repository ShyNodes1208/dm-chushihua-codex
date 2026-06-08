from __future__ import annotations

import json
import os
import socket
import sys
import threading
import time
from pathlib import Path

from werkzeug.serving import make_server

# In script mode desktop_app.py lives in the project/app directory. In frozen
# mode the exe lives beside app/, so keep config/templates/sql files external.
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent / "app"
else:
    BASE_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(BASE_DIR))

from app import app  # noqa: E402


class FlaskThread(threading.Thread):
    def __init__(self, host: str, port: int) -> None:
        super().__init__(daemon=True)
        self.server = make_server(host, port, app)
        self.host = host
        self.port = self.server.server_port

    def run(self) -> None:
        self.server.serve_forever()

    def stop(self) -> None:
        self.server.shutdown()


def load_server_config() -> tuple[str, int]:
    config_path = BASE_DIR / "config.json"
    with config_path.open("r", encoding="utf-8-sig") as fh:
        config = json.load(fh)
    server = config.get("server", {})
    host = os.environ.get("DM_QUERY_HOST", server.get("host", "127.0.0.1"))
    port = int(os.environ.get("DM_QUERY_PORT", server.get("port", 5000)))
    return host, port


def wait_until_ready(host: str, port: int, timeout_seconds: float = 8.0) -> None:
    deadline = time.time() + timeout_seconds
    last_error: OSError | None = None
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return
        except OSError as exc:
            last_error = exc
            time.sleep(0.1)
    raise RuntimeError(f"Server did not start at {host}:{port}: {last_error}")


def main() -> None:
    try:
        import webview
    except ImportError as exc:
        raise SystemExit("Missing dependency: pywebview. Install it before starting desktop mode.") from exc

    host, port = load_server_config()
    server = FlaskThread(host, port)
    server.start()
    wait_until_ready(host, server.port)

    url = f"http://{host}:{server.port}"
    try:
        webview.create_window("达梦数据库信息查询", url, width=1280, height=820, min_size=(960, 640))
        webview.start()
    finally:
        server.stop()


if __name__ == "__main__":
    main()

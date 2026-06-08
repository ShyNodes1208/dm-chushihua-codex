import json
import os
import sys
from pathlib import Path

# Ensure the app directory is on sys.path (required for embeddable Python)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import app


if __name__ == "__main__":
    config_path = Path(__file__).parent / "config.json"
    with config_path.open("r", encoding="utf-8-sig") as fh:
        config = json.load(fh)
    server = config.get("server", {})
    host = os.environ.get("DM_QUERY_HOST", server.get("host", "127.0.0.1"))
    port = int(os.environ.get("DM_QUERY_PORT", server.get("port", 5000)))
    print(f"Server: http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)

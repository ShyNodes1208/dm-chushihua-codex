from __future__ import annotations

import os
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request, send_file

from cache_manager import CacheManager
from db_connector import query_instance
from excel_exporter import export_query_to_excel
from sql_loader import SqlLoader


BASE_DIR = Path(__file__).resolve().parent


def create_app() -> Flask:
    app = Flask(__name__)

    def runtime_context() -> tuple[Dict[str, Any], SqlLoader, CacheManager]:
        config = load_config()
        return config, SqlLoader(config["sql_dir"]), CacheManager(config["cache_dir"])

    @app.get("/")
    def index():
        config, _, _ = runtime_context()
        return render_template("index.html", page_size=config.get("page_size", 10))

    @app.get("/api/queries")
    def api_queries():
        config, sql_loader, cache_manager = runtime_context()
        queries = []
        for item in sql_loader.list_queries():
            cache = cache_manager.read(item["name"])
            status = cache_manager.status(item["name"], item["md5"])
            queries.append(
                {
                    "name": item["name"],
                    "file": item["file"],
                    "sql_md5": item["md5"],
                    "has_meta": item.get("has_meta", False),
                    "status": status,
                    "queried_at": cache.get("queried_at") if cache else None,
                }
            )
        return jsonify({"queries": queries, "page_size": config.get("page_size", 10)})

    @app.get("/api/query/<name>")
    def api_query(name: str):
        try:
            config, sql_loader, cache_manager = runtime_context()
            item = sql_loader.get_query(name)
            cache = cache_manager.read(name)
            if not cache:
                return jsonify({"error": "No cache yet. Refresh data first.", "status": "missing"}), 404
            payload = dict(cache)
            payload["status"] = cache_manager.status(name, item["md5"])
            payload["page_size"] = parse_positive_int(request.args.get("per_page"), config.get("page_size", 10))
            payload["search"] = request.args.get("search", "")
            return jsonify(payload)
        except FileNotFoundError:
            return jsonify({"error": "Query not found."}), 404
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.post("/api/query/<name>/refresh")
    def api_refresh(name: str):
        try:
            config, sql_loader, cache_manager = runtime_context()
            result = refresh_query(name, config, sql_loader, cache_manager, request.args.to_dict())
            return jsonify(result)
        except FileNotFoundError:
            return jsonify({"error": "Query not found."}), 404
        except Exception as exc:
            return jsonify({"error": str(exc), "trace": traceback.format_exc()}), 500

    @app.post("/api/refresh-all")
    def api_refresh_all():
        config, sql_loader, cache_manager = runtime_context()
        results = []
        for item in sql_loader.list_queries():
            try:
                results.append(refresh_query(item["name"], config, sql_loader, cache_manager, request.args.to_dict()))
            except Exception as exc:
                results.append({"query_name": item["name"], "error": str(exc)})
        return jsonify({"results": results})

    @app.get("/api/query/<name>/export")
    def api_export(name: str):
        try:
            _, sql_loader, cache_manager = runtime_context()
            item = sql_loader.get_query(name)
            cache = cache_manager.read(name)
            if not cache:
                return jsonify({"error": "No cache yet. Refresh data first."}), 404
            stream = export_query_to_excel(cache, search=request.args.get("search", ""))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{item['name']}_{timestamp}.xlsx"
            return send_file(
                stream,
                as_attachment=True,
                download_name=filename,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except FileNotFoundError:
            return jsonify({"error": "Query not found."}), 404
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return app


def load_config() -> Dict[str, Any]:
    import json

    config_path = BASE_DIR / "config.json"
    with config_path.open("r", encoding="utf-8") as fh:
        config = json.load(fh)
    config["sql_dir"] = str((BASE_DIR / config.get("sql_dir", "./sql_templates")).resolve())
    config["cache_dir"] = str((BASE_DIR / config.get("cache_dir", "./cache")).resolve())
    config.setdefault("page_size", 10)
    config.setdefault("instances", [])
    config.setdefault("defaults", {})
    if os.environ.get("DM_PASSWORD"):
        config["defaults"]["password"] = os.environ["DM_PASSWORD"]
    return config


def parse_positive_int(value: Any, default: Any) -> int:
    try:
        parsed = int(value if value not in (None, "") else default)
    except (TypeError, ValueError):
        parsed = int(default or 10)
    return max(1, parsed)


def merged_instance(defaults: Dict[str, Any], instance: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(defaults)
    merged.update(instance)
    merged.setdefault("label", merged.get("host", "unnamed"))
    merged.setdefault("env", "测试")
    return merged


def refresh_query(
    name: str,
    config: Dict[str, Any],
    sql_loader: SqlLoader,
    cache_manager: CacheManager,
    url_params: Dict[str, str] | None = None,
) -> Dict[str, Any]:
    query = sql_loader.get_query(name)
    column_labels = sql_loader.load_meta(name) if query.get("has_meta") else []
    rows = []
    columns = None
    url_params = url_params or {}
    instances = config.get("instances", [])

    def query_one(raw_instance: Dict[str, Any]) -> Dict[str, Any]:
        instance = merged_instance(config["defaults"], raw_instance)
        started = datetime.now()
        try:
            sql = sql_loader.render(query["sql"], instance, url_params)
            query_result = query_instance(instance, sql)
            data = flatten_meta_rows(query_result["rows"]) if query.get("has_meta") else query_result["rows"]
            elapsed = int((datetime.now() - started).total_seconds() * 1000)
            result = {
                "instance": instance["label"],
                "env": instance.get("env", ""),
                "host": instance["host"],
                "query_time_ms": elapsed,
                "data": data,
                "columns": query_result["columns"],
                "error": None,
            }
            if query.get("has_meta") and len(data) != len(column_labels):
                result["warning"] = f"Value count {len(data)} does not match column label count {len(column_labels)}."
            return result
        except Exception as exc:
            elapsed = int((datetime.now() - started).total_seconds() * 1000)
            return {
                "instance": instance.get("label", instance.get("host", "unnamed")),
                "env": instance.get("env", ""),
                "host": instance.get("host", ""),
                "query_time_ms": elapsed,
                "data": None,
                "columns": [],
                "error": str(exc),
            }

    max_workers = min(8, max(1, len(instances)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(query_one, item) for item in instances]
        for future in as_completed(futures):
            result = future.result()
            if columns is None and result.get("data") is not None:
                columns = result.get("columns") or []
            rows.append(result)

    instance_order = {}
    for index, raw_instance in enumerate(instances):
        instance = merged_instance(config["defaults"], raw_instance)
        instance_order[instance["label"]] = index
    rows.sort(key=lambda row: instance_order.get(row.get("instance"), 999999))

    payload = {
        "query_name": name,
        "sql_md5": query["md5"],
        "queried_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rows": rows,
    }
    if query.get("has_meta"):
        max_values = max((len(row.get("data") or []) for row in rows), default=0)
        payload["column_labels"] = column_labels or sql_loader.load_meta(name, max_values)
    else:
        payload["columns"] = columns or []
    cache_manager.write(name, payload)
    payload["status"] = "valid"
    return payload


def flatten_meta_rows(rows: list[Any]) -> list[Any]:
    values = []
    for row in rows:
        if isinstance(row, (list, tuple)):
            values.append(row[0] if row else None)
        else:
            values.append(row)
    return values


app = create_app()


if __name__ == "__main__":
    server_config = load_config().get("server", {})
    host = os.environ.get("DM_QUERY_HOST", server_config.get("host", "127.0.0.1"))
    port = int(os.environ.get("DM_QUERY_PORT", server_config.get("port", 5000)))
    print(f"Server: http://{host}:{port}")
    app.run(host=host, port=port, debug=True)

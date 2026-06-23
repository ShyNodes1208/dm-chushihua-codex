from __future__ import annotations

import json
import os
import secrets
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request, send_file, session

from cache_manager import CacheManager
from db_connector import query_instance, test_connection
from excel_exporter import export_all_to_excel, export_query_to_excel
from sql_loader import SqlLoader, clean_stem


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
LOCAL_CONFIG_PATH = BASE_DIR / "config.local.json"


def create_app() -> Flask:
    app = Flask(__name__)
    raw = merged_raw_config()
    app.secret_key = resolve_secret(raw.get("secret_key")) or os.environ.get("DM_SECRET_KEY") or secrets.token_hex(16)

    def runtime_context() -> tuple[Dict[str, Any], SqlLoader, CacheManager]:
        config = load_config()
        return config, SqlLoader(config["sql_dir"]), CacheManager(config["cache_dir"])

    def auth_enabled() -> bool:
        config = load_config()
        return bool(config.get("auth", {}).get("enabled")) and bool(config.get("auth", {}).get("password"))

    def login_required(view):
        @wraps(view)
        def wrapper(*args: Any, **kwargs: Any):
            if auth_enabled() and not session.get("authed"):
                return jsonify({"error": "未登录或登录已失效。", "auth_required": True}), 401
            return view(*args, **kwargs)

        return wrapper

    @app.get("/")
    def index():
        config = load_config()
        return render_template(
            "index.html",
            page_size=config.get("page_size", 10),
            auth_enabled=auth_enabled(),
        )

    @app.get("/api/session")
    def api_session():
        return jsonify({"auth_enabled": auth_enabled(), "authed": bool(session.get("authed"))})

    @app.post("/api/login")
    def api_login():
        config = load_config()
        password = config.get("auth", {}).get("password")
        provided = (request.get_json(silent=True) or {}).get("password", "")
        if not auth_enabled():
            session["authed"] = True
            return jsonify({"ok": True})
        if provided and secrets.compare_digest(str(provided), str(password)):
            session["authed"] = True
            return jsonify({"ok": True})
        return jsonify({"error": "口令不正确。"}), 401

    @app.post("/api/logout")
    def api_logout():
        session.pop("authed", None)
        return jsonify({"ok": True})

    @app.get("/api/queries")
    @login_required
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
        return jsonify(
            {
                "queries": queries,
                "page_size": config.get("page_size", 10),
                "cache_max_age_minutes": int(config.get("cache_max_age_minutes", 0) or 0),
            }
        )

    @app.get("/api/query/<name>")
    @login_required
    def api_query(name: str):
        try:
            config, sql_loader, cache_manager = runtime_context()
            item = sql_loader.get_query(name)
            cache = cache_manager.read(name)
            if not cache:
                return jsonify({"error": "No cache yet. Refresh data first.", "status": "missing"}), 404
            payload = dict(cache)
            payload["status"] = cache_manager.status(name, item["md5"])
            payload["cache_max_age_minutes"] = int(config.get("cache_max_age_minutes", 0) or 0)
            prev = cache_manager.read_prev(name)
            if prev:
                payload["previous"] = {"queried_at": prev.get("queried_at"), "rows": prev.get("rows", [])}
            return jsonify(payload)
        except FileNotFoundError:
            return jsonify({"error": "Query not found."}), 404
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": str(exc)}), 500

    @app.post("/api/query/<name>/refresh")
    @login_required
    def api_refresh(name: str):
        try:
            config, sql_loader, cache_manager = runtime_context()
            result = refresh_query(name, config, sql_loader, cache_manager, request.args.to_dict())
            return jsonify(result)
        except FileNotFoundError:
            return jsonify({"error": "Query not found."}), 404
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": str(exc), "trace": traceback.format_exc()}), 500

    @app.post("/api/refresh-all")
    @login_required
    def api_refresh_all():
        config, sql_loader, cache_manager = runtime_context()
        results = []
        for item in sql_loader.list_queries():
            try:
                results.append(refresh_query(item["name"], config, sql_loader, cache_manager, request.args.to_dict()))
            except Exception as exc:  # noqa: BLE001
                results.append({"query_name": item["name"], "error": str(exc)})
        return jsonify({"results": results})

    @app.post("/api/test-connections")
    @login_required
    def api_test_connections():
        config = load_config()
        instances = config.get("instances", [])
        defaults = config.get("defaults", {})
        results: List[Dict[str, Any]] = [None] * len(instances)  # type: ignore[list-item]
        max_workers = min(8, max(1, len(instances)))

        def probe(index: int, raw_instance: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
            instance = merged_instance(defaults, raw_instance)
            outcome = test_connection(instance)
            return index, {
                "idx": index,
                "instance": instance["label"],
                "env": instance.get("env", ""),
                "host": instance.get("host", ""),
                **outcome,
            }

        if instances:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(probe, idx, item) for idx, item in enumerate(instances)]
                for future in as_completed(futures):
                    index, outcome = future.result()
                    results[index] = outcome
        ok = sum(1 for item in results if item and item.get("ok"))
        return jsonify({"results": results, "ok": ok, "failed": len(results) - ok})

    @app.get("/api/query/<name>/export")
    @login_required
    def api_export(name: str):
        try:
            _, sql_loader, cache_manager = runtime_context()
            item = sql_loader.get_query(name)
            cache = cache_manager.read(name)
            if not cache:
                return jsonify({"error": "No cache yet. Refresh data first."}), 404
            stream = export_query_to_excel(
                cache,
                search=request.args.get("search", ""),
                visible_columns=parse_columns(request.args.get("columns")),
                env=request.args.get("env", ""),
                only_failed=request.args.get("only_failed", "") in ("1", "true", "yes"),
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{item['name']}_{timestamp}.xlsx"
            return send_excel(stream, filename)
        except FileNotFoundError:
            return jsonify({"error": "Query not found."}), 404
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": str(exc)}), 500

    @app.get("/api/export-all")
    @login_required
    def api_export_all():
        _, sql_loader, cache_manager = runtime_context()
        caches = []
        for item in sql_loader.list_queries():
            cache = cache_manager.read(item["name"])
            if cache:
                caches.append(cache)
        if not caches:
            return jsonify({"error": "暂无任何缓存，请先刷新数据。"}), 404
        stream = export_all_to_excel(
            caches,
            search=request.args.get("search", ""),
            env=request.args.get("env", ""),
            only_failed=request.args.get("only_failed", "") in ("1", "true", "yes"),
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_excel(stream, f"all_queries_{timestamp}.xlsx")

    @app.get("/api/config")
    @login_required
    def api_get_config():
        config = load_config()
        return jsonify(
            {
                "instances": [mask_secrets(item) for item in config.get("instances", [])],
                "defaults": mask_secrets(config.get("defaults", {})),
                "page_size": config.get("page_size", 10),
                "cache_max_age_minutes": int(config.get("cache_max_age_minutes", 0) or 0),
            }
        )

    @app.post("/api/instances")
    @login_required
    def api_save_instances():
        body = request.get_json(silent=True) or {}
        instances = body.get("instances")
        if not isinstance(instances, list):
            return jsonify({"error": "instances 必须是数组。"}), 400
        raw_config = load_raw_config()
        editable_keys = {"label", "host", "env", "port", "user", "password"}
        existing_by_key = {
            f"{(i or {}).get('label', '')}\u0001{(i or {}).get('host', '')}": (i or {})
            for i in raw_config.get("instances", [])
        }
        cleaned = []
        for index, item in enumerate(instances, start=1):
            label = str((item or {}).get("label", "")).strip()
            host = str((item or {}).get("host", "")).strip()
            if not label or not host:
                return jsonify({"error": f"第 {index} 行缺少实例名称或服务器 IP。"}), 400
            existing = existing_by_key.get(f"{label}\u0001{host}", {})
            # 保留旧实例上不在编辑表内的高级字段（如 connect_timeout）。
            entry = {key: value for key, value in existing.items() if key not in editable_keys}
            entry.update({"label": label, "host": host, "env": str((item or {}).get("env", "")).strip()})
            for optional in ("port", "user"):
                value = (item or {}).get(optional)
                if value not in (None, ""):
                    entry[optional] = value
            password = (item or {}).get("password")
            if password == "******":
                kept = existing.get("password")
                if kept not in (None, ""):
                    entry["password"] = kept
            elif password not in (None, ""):
                entry["password"] = password
            cleaned.append(entry)
        raw_config["instances"] = cleaned
        save_raw_config(raw_config)
        return jsonify({"ok": True, "count": len(cleaned)})

    @app.get("/api/sql/<name>")
    @login_required
    def api_get_sql(name: str):
        try:
            _, sql_loader, _ = runtime_context()
            item = sql_loader.get_query(name)
            return jsonify({"name": item["name"], "sql": item["sql"], "columns": sql_loader.load_meta(name) if item.get("has_meta") else []})
        except FileNotFoundError:
            return jsonify({"error": "Query not found."}), 404

    @app.post("/api/sql/<name>")
    @login_required
    def api_save_sql(name: str):
        body = request.get_json(silent=True) or {}
        try:
            _, sql_loader, _ = runtime_context()
            columns = body.get("columns")
            if isinstance(columns, str):
                columns = [line.strip() for line in columns.replace("\r", "\n").split("\n") if line.strip()]
            item = sql_loader.save_query(name, body.get("sql", ""), columns)
            return jsonify({"ok": True, "name": item["name"]})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.delete("/api/sql/<name>")
    @login_required
    def api_delete_sql(name: str):
        try:
            _, sql_loader, cache_manager = runtime_context()
            safe = clean_stem(name)
            sql_loader.delete_query(safe)
            cache_manager.delete(safe)
            return jsonify({"ok": True})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    return app


def load_raw_config() -> Dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def load_local_overrides() -> Dict[str, Any]:
    """读取仅存在于本机、不进 git 的 config.local.json，用于存放真实密码等敏感信息。"""
    if not LOCAL_CONFIG_PATH.exists():
        return {}
    try:
        with LOCAL_CONFIG_PATH.open("r", encoding="utf-8-sig") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def merged_raw_config() -> Dict[str, Any]:
    """config.json 为基础，config.local.json（本机私有）逐键覆盖，dict 做浅合并。"""
    config = load_raw_config()
    for key, value in load_local_overrides().items():
        if isinstance(value, dict) and isinstance(config.get(key), dict):
            config[key] = {**config[key], **value}
        else:
            config[key] = value
    return config


def save_raw_config(config: Dict[str, Any]) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def resolve_secret(value: Any) -> Any:
    """支持 "env:VAR_NAME" 形式，从环境变量读取，避免明文写在配置里。"""
    if isinstance(value, str) and value.startswith("env:"):
        return os.environ.get(value[4:], "")
    return value


def mask_secrets(defaults: Dict[str, Any]) -> Dict[str, Any]:
    masked = dict(defaults)
    if masked.get("password"):
        masked["password"] = "******"
    return masked


def load_config() -> Dict[str, Any]:
    config = merged_raw_config()
    config["sql_dir"] = str((BASE_DIR / config.get("sql_dir", "./sql_templates")).resolve())
    config["cache_dir"] = str((BASE_DIR / config.get("cache_dir", "./cache")).resolve())
    config.setdefault("page_size", 10)
    config.setdefault("instances", [])
    config.setdefault("defaults", {})
    config.setdefault("auth", {})
    defaults = config["defaults"]
    if defaults.get("password"):
        defaults["password"] = resolve_secret(defaults["password"])
    if config.get("auth", {}).get("password"):
        config["auth"]["password"] = resolve_secret(config["auth"]["password"])
    if os.environ.get("DM_PASSWORD"):
        config["defaults"]["password"] = os.environ["DM_PASSWORD"]
    if os.environ.get("DM_AUTH_PASSWORD"):
        config["auth"]["enabled"] = True
        config["auth"]["password"] = os.environ["DM_AUTH_PASSWORD"]
    return config


def parse_columns(value: Any) -> List[str] | None:
    if not value:
        return None
    return [part for part in str(value).split("\u0001") if part != ""]


def send_excel(stream: Any, filename: str):
    return send_file(
        stream,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def merged_instance(defaults: Dict[str, Any], instance: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(defaults)
    merged.update(instance)
    if merged.get("password"):
        merged["password"] = resolve_secret(merged["password"])
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

    def query_one(index: int, raw_instance: Dict[str, Any]) -> Dict[str, Any]:
        instance = merged_instance(config["defaults"], raw_instance)
        started = datetime.now()
        try:
            sql = sql_loader.render(query["sql"], instance, url_params)
            query_result = query_instance(instance, sql)
            data = flatten_meta_rows(query_result["rows"]) if query.get("has_meta") else query_result["rows"]
            elapsed = int((datetime.now() - started).total_seconds() * 1000)
            result = {
                "idx": index,
                "instance": instance["label"],
                "env": instance.get("env", ""),
                "host": instance["host"],
                "query_time_ms": elapsed,
                "data": data,
                "columns": query_result["columns"],
                "error": None,
            }
            if query.get("has_meta") and len(data) != len(column_labels):
                result["warning"] = f"返回 {len(data)} 个值，但配置了 {len(column_labels)} 个列名，数据可能错位。"
            return result
        except Exception as exc:  # noqa: BLE001
            elapsed = int((datetime.now() - started).total_seconds() * 1000)
            return {
                "idx": index,
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
        futures = [executor.submit(query_one, index, item) for index, item in enumerate(instances)]
        for future in as_completed(futures):
            result = future.result()
            if columns is None and result.get("data") is not None:
                columns = result.get("columns") or []
            rows.append(result)

    rows.sort(key=lambda row: row.get("idx", 999999))

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
    debug = os.environ.get("DM_DEBUG", "").lower() in ("1", "true", "yes")
    print(f"Server: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

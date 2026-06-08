from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, List

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


def export_query_to_excel(cache: Dict[str, Any], search: str = "") -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = cache.get("query_name", "query")[:31]
    table = build_display_table(cache)
    rows = filter_rows(table["rows"], search)

    ws.append(table["headers"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="E9EEF7")

    for row in rows:
        ws.append(row)

    for index, _ in enumerate(table["headers"], start=1):
        column = get_column_letter(index)
        width = max(len(str(ws.cell(row=row, column=index).value or "")) for row in range(1, ws.max_row + 1))
        ws.column_dimensions[column].width = min(max(width + 2, 12), 42)

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream


def build_display_table(cache: Dict[str, Any]) -> Dict[str, List[List[Any]]]:
    if cache.get("column_labels"):
        return build_meta_table(cache)
    if cache.get("display_mode") == "key_value":
        return build_key_value_table(cache.get("rows", []))
    return build_flat_table(cache.get("rows", []))


def build_meta_table(cache: Dict[str, Any]) -> Dict[str, List[List[Any]]]:
    labels = cache.get("column_labels") or []
    headers = ["instance", "env"] + labels
    table_rows = []
    for item in cache.get("rows", []):
        data = list(item.get("data") or [])
        if item.get("error"):
            data = [item.get("error")] + [""] * max(0, len(labels) - 1)
        data = normalize_length(data, len(labels))
        table_rows.append([item.get("instance"), item.get("env", ""), *data])
    return {"headers": headers, "rows": table_rows}


def build_key_value_table(rows: List[Dict[str, Any]]) -> Dict[str, List[List[Any]]]:
    keys = []
    values_by_instance = {}
    errors = {}
    instance_keys = []
    instance_labels = []
    for index, item in enumerate(rows):
        instance_key = f"{index}:{item.get('instance', '')}"
        instance_keys.append(instance_key)
        instance_labels.append(item.get("instance"))
        values_by_instance[instance_key] = {}
        if item.get("error"):
            errors[instance_key] = item["error"]
        for data_row in item.get("data") or []:
            key = data_row[0]
            if key not in keys:
                keys.append(key)
            val = data_row[1] if len(data_row) > 1 else None
            if val is not None and val != "":
                values_by_instance[instance_key][key] = val
            elif key not in values_by_instance[instance_key]:
                values_by_instance[instance_key][key] = ""

    headers = ["item"] + instance_labels
    table_rows = []
    for key in keys:
        table_rows.append([key] + [values_by_instance.get(instance_key, {}).get(key, errors.get(instance_key, "")) for instance_key in instance_keys])
    if not keys and errors:
        table_rows.append(["error"] + [errors.get(instance_key, "") for instance_key in instance_keys])
    return {"headers": headers, "rows": table_rows}


def build_flat_table(rows: List[Dict[str, Any]]) -> Dict[str, List[List[Any]]]:
    base_columns: List[Any] = []
    for item in rows:
        if len(item.get("columns") or []) > len(base_columns):
            base_columns = item["columns"]
    if not base_columns:
        max_values = max((len(data_row) for item in rows for data_row in item.get("data") or []), default=0)
        if max_values:
            base_columns = [f"col_{index}" for index in range(1, max_values + 1)]
    headers = ["instance", "env"] + base_columns + ["error"]
    table_rows = []
    for item in rows:
        if item.get("error"):
            table_rows.append([item.get("instance"), item.get("env", "")] + [""] * len(base_columns) + [item.get("error")])
            continue
        data_rows = item.get("data") or []
        if not data_rows:
            table_rows.append([item.get("instance"), item.get("env", "")] + [""] * len(base_columns) + [""])
            continue
        for data_row in data_rows:
            table_rows.append([item.get("instance"), item.get("env", "")] + normalize_length(list(data_row), len(base_columns)) + [""])
    return {"headers": headers, "rows": table_rows}


def normalize_length(values: List[Any], length: int) -> List[Any]:
    if len(values) < length:
        return values + [""] * (length - len(values))
    return values[:length]


def filter_rows(rows: List[List[Any]], search: str) -> List[List[Any]]:
    keyword = (search or "").strip().lower()
    if not keyword:
        return rows
    return [row for row in rows if keyword in " ".join(str(cell).lower() for cell in row)]


if __name__ == "__main__":
    demo = {"query_name": "demo", "column_labels": ["version"], "rows": [{"instance": "DB-01", "env": "测试", "data": ["8"], "error": None}]}
    print(len(export_query_to_excel(demo).getvalue()))

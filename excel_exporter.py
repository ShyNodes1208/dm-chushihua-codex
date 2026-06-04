from __future__ import annotations

from io import BytesIO
from typing import Any, Dict, Iterable, List

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
    success_rows = [row for row in cache.get("rows", []) if row.get("data")]
    if is_key_value_result(success_rows):
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


def is_key_value_result(rows: Iterable[Dict[str, Any]]) -> bool:
    checked = False
    for row in rows:
        data = row.get("data") or []
        if not data:
            continue
        checked = True
        if any(not isinstance(item, (list, tuple)) or len(item) < 2 for item in data):
            return False
    return checked


def build_key_value_table(rows: List[Dict[str, Any]]) -> Dict[str, List[List[Any]]]:
    keys = []
    values_by_instance = {}
    errors = {}
    for item in rows:
        instance = item.get("instance")
        values_by_instance[instance] = {}
        if item.get("error"):
            errors[instance] = item["error"]
        for data_row in item.get("data") or []:
            key = data_row[0]
            if key not in keys:
                keys.append(key)
            val = data_row[1] if len(data_row) > 1 else None
            if val is not None and val != "":
                values_by_instance[instance][key] = val
            elif key not in values_by_instance[instance]:
                values_by_instance[instance][key] = ""

    headers = ["item"] + [item.get("instance") for item in rows]
    table_rows = []
    for key in keys:
        table_rows.append([key] + [values_by_instance.get(item.get("instance"), {}).get(key, errors.get(item.get("instance"), "")) for item in rows])
    if not keys and errors:
        table_rows.append(["error"] + [errors.get(item.get("instance"), "") for item in rows])
    return {"headers": headers, "rows": table_rows}


def build_flat_table(rows: List[Dict[str, Any]]) -> Dict[str, List[List[Any]]]:
    base_columns = []
    for item in rows:
        if item.get("columns"):
            base_columns = item["columns"]
            break
    headers = ["instance", "env"] + base_columns + ["error"]
    table_rows = []
    for item in rows:
        if item.get("error"):
            table_rows.append([item.get("instance"), item.get("env", "")] + [""] * len(base_columns) + [item.get("error")])
            continue
        for data_row in item.get("data") or []:
            table_rows.append([item.get("instance"), item.get("env", "")] + list(data_row) + [""])
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

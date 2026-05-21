"""Serialize DB driver values to JSON-safe structures (no silent data drop)."""

from __future__ import annotations

import json
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any


def json_safe(val: Any) -> Any:
    if val is None:
        return None
    if isinstance(val, (datetime, date, time)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, memoryview):
        return {"__bytes_b64_skipped__": True, "len": len(val)}
    if isinstance(val, (bytes, bytearray)):
        return {"__bytes_b64_skipped__": True, "len": len(val)}
    if isinstance(val, dict):
        return {str(k): json_safe(v) for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        return [json_safe(v) for v in val]
    return val


def row_to_dict(description: tuple, row: tuple) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for col, val in zip([d.name for d in description], row):
        if col in out:
            col = f"{col}__dup"
        out[col] = json_safe(val)
    return out


def dumps_row(row_dict: dict[str, Any]) -> str:
    return json.dumps(row_dict, ensure_ascii=False, sort_keys=True, default=str)

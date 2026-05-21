"""Append-only migration_events for rows that cannot be linked (no data loss)."""

from __future__ import annotations

import json
from typing import Any

from psycopg2.extras import Json

from migrations_cli.etl_arc import _migration_system_user_id

_MAX_DETAIL_JSON = 120_000


def _shrink_detail(detail: dict[str, Any]) -> dict[str, Any]:
    s = json.dumps(detail, default=str)
    if len(s) <= _MAX_DETAIL_JSON:
        return detail
    row = detail.get("row")
    if isinstance(row, dict):
        rj = json.dumps(row, default=str)
        keep = max(1000, _MAX_DETAIL_JSON - 2000)
        detail = {
            **{k: v for k, v in detail.items() if k != "row"},
            "row_truncated": True,
            "row_prefix": rj[:keep] + "...",
        }
    return detail


def log_import_orphan(
    r_cur: Any,
    *,
    batch_id: str,
    event_type: str,
    summary: str,
    detail: dict[str, Any],
    subject_id: int | None,
) -> None:
    d2 = _shrink_detail(detail)
    r_cur.execute(
        """
        INSERT INTO migration_events (
            batch_id, event_type, summary, detail, subject_id, created_by_user_id, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC')
        """,
        (
            batch_id,
            event_type,
            summary,
            Json(d2),
            subject_id,
            _migration_system_user_id(r_cur),
        ),
    )

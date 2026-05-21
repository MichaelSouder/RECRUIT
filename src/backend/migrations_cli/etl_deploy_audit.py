"""Deployment helpers: audit_logs for migration milestones (21 CFR Part 11 trail)."""

from __future__ import annotations

import json
import logging
from typing import Any

log = logging.getLogger("migrations_cli")


def insert_migration_audit_log(
    r_cur: Any,
    mig_uid: int,
    *,
    action: str,
    entity_type: str,
    entity_id: int,
    change_summary: str,
    additional_context: dict[str, Any] | None = None,
) -> None:
    """Append one ``audit_logs`` row attributed to the migration system user."""
    r_cur.execute(
        "SELECT email, COALESCE(full_name, '') FROM users WHERE id = %s",
        (mig_uid,),
    )
    row = r_cur.fetchone()
    if not row:
        raise RuntimeError(f"migration user id {mig_uid} missing from users")
    email, full_name = row[0], (row[1] or "").strip() or "Migration system"
    ctx = json.dumps(additional_context or {}, default=str)
    r_cur.execute(
        """
        INSERT INTO audit_logs (
            timestamp, user_id, user_email, user_full_name, action, entity_type, entity_id,
            change_summary, additional_context, created_at
        ) VALUES (
            NOW() AT TIME ZONE 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, NOW() AT TIME ZONE 'UTC'
        )
        """,
        (
            mig_uid,
            email,
            full_name,
            action,
            entity_type,
            entity_id,
            change_summary[:10000] if change_summary else "",
            ctx,
        ),
    )
    log.info("migration_audit.inserted %s", json.dumps({"action": action, "entity_type": entity_type}))

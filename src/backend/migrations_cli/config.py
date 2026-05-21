"""Load and validate environment for the migration CLI."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class MigrationConfig:
    database_url: str
    legacy_arc_url: Optional[str]
    legacy_dvbic_research_url: Optional[str]
    migration_batch_id: Optional[str]
    dry_run: bool


def _mask_database_url(url: str) -> str:
    if not url or "@" not in url:
        return url
    return re.sub(r":([^:@/]+)@", r":****@", url, count=1)


def load_config(*, dry_run: bool = False) -> MigrationConfig:
    db = os.environ.get("DATABASE_URL", "").strip()
    if not db:
        raise SystemExit(
            "DATABASE_URL is not set. Example:\n"
            "  export DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:15432/recruit_db"
        )
    return MigrationConfig(
        database_url=db,
        legacy_arc_url=os.environ.get("LEGACY_ARC_DATABASE_URL", "").strip() or None,
        legacy_dvbic_research_url=os.environ.get(
            "LEGACY_DVBIC_RESEARCH_DATABASE_URL", ""
        ).strip()
        or None,
        migration_batch_id=os.environ.get("MIGRATION_BATCH_ID", "").strip() or None,
        dry_run=dry_run,
    )


def masked_recruit_url(cfg: MigrationConfig) -> str:
    return _mask_database_url(cfg.database_url)

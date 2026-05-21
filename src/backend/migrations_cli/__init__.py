"""RECRUIT legacy data migration CLI (Phase B skeleton).

Run from `src/backend` with dependencies installed:

  export DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:15432/recruit_db
  export LEGACY_ARC_DATABASE_URL=postgresql://...@...:5432/arc   # optional
  python -m migrations_cli preflight
  python -m migrations_cli validate
  python -m migrations_cli legacy-stats

Environment:
  DATABASE_URL          — RECRUIT Postgres (required for most commands)
  LEGACY_ARC_DATABASE_URL — read-only legacy `arc` database (optional)
  MIGRATION_BATCH_ID    — required before any future write subcommands
"""

__version__ = "0.1.0"

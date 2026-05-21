"""Small DB helpers for the migration CLI (psycopg2, no SQLAlchemy app import cycle)."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator, Iterable, Optional

import psycopg2
import psycopg2.extensions


@contextmanager
def connect(url: str) -> Generator[psycopg2.extensions.connection, None, None]:
    conn = psycopg2.connect(url)
    try:
        yield conn
    finally:
        conn.close()


def run_scalar(url: str, sql: str, params: Optional[tuple | list] = None) -> Any:
    with connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone()
            return row[0] if row else None


def run_query(url: str, sql: str, params: Optional[tuple | list] = None) -> list[tuple]:
    with connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return list(cur.fetchall())

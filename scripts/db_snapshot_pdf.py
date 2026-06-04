#!/usr/bin/env python3
"""
Build a PDF snapshot of public tables in any PostgreSQL database.

Presets (set matching env vars):
  python scripts/db_snapshot_pdf.py --preset recruit
  python scripts/db_snapshot_pdf.py --preset arc
  python scripts/db_snapshot_pdf.py --preset dvbic-research
  python scripts/db_snapshot_pdf.py --preset all-legacy    # arc + dvbic (two PDFs)

Generic:
  python scripts/db_snapshot_pdf.py --database-url 'postgresql://...' -o out.pdf --title 'My DB'

Requires: pip install psycopg2-binary fpdf2
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import psycopg2
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
except ImportError as e:
    print("Missing dependency:", e, file=sys.stderr)
    print("Install with: pip install psycopg2-binary fpdf2", file=sys.stderr)
    sys.exit(1)


def _ascii_safe(s: str, max_len: int = 900) -> str:
    t = s if len(s) <= max_len else s[: max_len - 3] + "..."
    return t.encode("ascii", errors="replace").decode("ascii")


def _format_cell(col: str, val) -> str:
    if val is None:
        return "NULL"
    if col in ("hashed_password", "password"):
        return "[REDACTED]"
    if col == "ssn" and val:
        digits = re.sub(r"\D", "", str(val))
        if len(digits) >= 4:
            return "***-**-" + digits[-4:]
        return "[REDACTED]"
    s = repr(val)
    return _ascii_safe(s, 240)


class SnapshotPDF(FPDF):
    def __init__(self, banner_title: str) -> None:
        super().__init__(format="Letter", orientation="landscape")
        self._banner_title = banner_title
        self.set_auto_page_break(auto=True, margin=14)
        self.set_margins(12, 12, 12)

    def header(self) -> None:  # noqa: N802
        self.set_font("Helvetica", "B", 9)
        self.cell(0, 6, self._banner_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 8)
        self.cell(
            0,
            5,
            f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.ln(2)

    def footer(self) -> None:  # noqa: N802
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def write_snapshot_pdf(
    *,
    database_url: str,
    output: Path,
    banner_title: str,
    intro_lines: str,
    limit: int,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename
        """
    )
    tables = [r[0] for r in cur.fetchall()]

    pdf = SnapshotPDF(banner_title)
    pdf.add_page()
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(pdf.epw, 4, _ascii_safe(intro_lines))
    pdf.ln(2)

    for t in tables:
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{t}"')
            total = cur.fetchone()[0]
            cur.execute(f'SELECT * FROM "{t}" LIMIT %s', (limit,))
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchall()
        except Exception as e:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, _ascii_safe(f"Table: {t}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(pdf.epw, 5, _ascii_safe(f"(skipped: {e})"))
            continue

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, _ascii_safe(f"Table: {t}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(
            0,
            5,
            _ascii_safe(f"Exact row count: {total}  |  Sample rows: {len(rows)}"),
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        pdf.ln(1)

        if not rows:
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(0, 5, "(no rows)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            continue

        for ri, row in enumerate(rows, 1):
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(0, 5, f"--- row {ri} ---", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Courier", "", 7)
            for c, v in zip(cols, row):
                line = f"  {c}: {_format_cell(c, v)}"
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(pdf.epw, 3.5, _ascii_safe(line))
            pdf.ln(1)

    cur.close()
    conn.close()
    pdf.output(str(output))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preset",
        choices=("recruit", "arc", "dvbic-research", "all-legacy"),
        default=None,
        help="Use env-backed URL and default output path / title.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output PDF path (required for generic mode; optional with --preset)",
    )
    parser.add_argument("--limit", type=int, default=10, help="Max rows per table (default: 10)")
    parser.add_argument("--database-url", default="", help="PostgreSQL URL (generic mode)")
    parser.add_argument(
        "--title",
        default="",
        help="Banner title on each page (generic mode)",
    )
    args = parser.parse_args()

    def run_one(url: str, out: Path, title: str, intro: str) -> None:
        write_snapshot_pdf(
            database_url=url,
            output=out,
            banner_title=title,
            intro_lines=intro,
            limit=args.limit,
        )
        print(f"Wrote {out.resolve()}")

    if args.preset == "recruit":
        url = (os.environ.get("DATABASE_URL") or "").strip()
        if not url:
            print("Set DATABASE_URL for preset recruit.", file=sys.stderr)
            return 1
        out = args.output or (Path("output") / "recruit-db-snapshot.pdf")
        intro = (
            "Source: DATABASE_URL (password omitted from banner text). "
            "Samples are arbitrary row order per table. "
            "hashed_password / password / ssn columns redacted or masked."
        )
        run_one(url, out, "RECRUIT database table snapshot", intro)
        return 0

    if args.preset == "arc":
        url = (os.environ.get("LEGACY_ARC_DATABASE_URL") or "").strip()
        if not url:
            print("Set LEGACY_ARC_DATABASE_URL for preset arc.", file=sys.stderr)
            return 1
        out = args.output or (Path("output") / "arc-db-snapshot.pdf")
        intro = (
            "Legacy database: arc (public schema). "
            "Connection URL from LEGACY_ARC_DATABASE_URL (password not printed). "
            "Compare with RECRUIT snapshot PDFs. "
            "hashed_password / password / ssn redacted or masked where column names match."
        )
        run_one(url, out, "arc - legacy PostgreSQL snapshot", intro)
        return 0

    if args.preset == "dvbic-research":
        url = (os.environ.get("LEGACY_DVBIC_RESEARCH_DATABASE_URL") or "").strip()
        if not url:
            print("Set LEGACY_DVBIC_RESEARCH_DATABASE_URL for preset dvbic-research.", file=sys.stderr)
            return 1
        out = args.output or (Path("output") / "dvbic-research-db-snapshot.pdf")
        intro = (
            "Legacy database: dvbic_research (public schema). "
            "URL from LEGACY_DVBIC_RESEARCH_DATABASE_URL (password not printed). "
            "Many tables - PDF may be long. "
            "hashed_password / password / ssn redacted or masked where column names match."
        )
        run_one(url, out, "dvbic_research - legacy PostgreSQL snapshot", intro)
        return 0

    if args.preset == "all-legacy":
        rc = 0
        url_arc = (os.environ.get("LEGACY_ARC_DATABASE_URL") or "").strip()
        url_dvb = (os.environ.get("LEGACY_DVBIC_RESEARCH_DATABASE_URL") or "").strip()
        if not url_arc:
            print("LEGACY_ARC_DATABASE_URL is not set.", file=sys.stderr)
            rc = 1
        else:
            run_one(
                url_arc,
                Path("output") / "arc-db-snapshot.pdf",
                "arc - legacy PostgreSQL snapshot",
                "Legacy arc DB. URL from LEGACY_ARC_DATABASE_URL. Redactions: password/ssn-like columns.",
            )
        if not url_dvb:
            print("LEGACY_DVBIC_RESEARCH_DATABASE_URL is not set.", file=sys.stderr)
            rc = 1
        else:
            run_one(
                url_dvb,
                Path("output") / "dvbic-research-db-snapshot.pdf",
                "dvbic_research - legacy PostgreSQL snapshot",
                "Legacy dvbic_research DB. URL from LEGACY_DVBIC_RESEARCH_DATABASE_URL. Many tables.",
            )
        return rc

    db_url = (args.database_url or "").strip()
    title = (args.title or "").strip()
    if not args.preset:
        if not db_url or not args.output or not title:
            print(
                "Generic mode requires --database-url, -o/--output, and --title, "
                "or use --preset recruit|arc|dvbic-research|all-legacy.",
                file=sys.stderr,
            )
            return 1
        intro = (
            "Custom snapshot. Row order arbitrary per table. "
            "hashed_password / password / ssn redacted or masked."
        )
        run_one(db_url, args.output, title, intro)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

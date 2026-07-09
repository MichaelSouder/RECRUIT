# RECRUIT production cutover dump (split for Git)

## Current cutover (default): `recruit_prod_cutover_20260709T1422Z`

7 parts, ~25–27 MB each:

- `recruit_prod_cutover_20260709T1422Z.part0.gz` … `part6.gz`
- `recruit_prod_cutover_20260709T1422Z.dump.sha256`

Full **`.dump`** (~192 MB) is gitignored (`data/backups/*.dump`); reassemble locally.

This supersedes the `20260521T1455Z` cutover below — row counts are
identical except `user_study` (120 vs 118), and 3 users' password hashes
changed on 2026-06-04. Restoring the older dump would silently roll back
those users' current passwords. `data/migration_verify_baseline.json` has
been refreshed to match this cutover.

## Prior cutover (kept for history): `recruit_prod_cutover_20260521T1455Z`

Same 7-parts-gzipped layout, still present under this directory. Use
`--base recruit_prod_cutover_20260521T1455Z` (or `DUMP_BASE=...`) with the
scripts below if you specifically need that snapshot instead of the current
default.

## Other files in this directory

- `assemble_recruit_dump.sh` (wrapper for `scripts/migration/assemble-recruit-dump.sh`)
- `../migration_verify_baseline.json` (expected row counts / alembic head for verification)

## Requirements (bash only)

- `gzip`, `shasum` or `sha256sum`
- `podman` or `docker` (restore into container)
- `psql` and `jq` (verify)
- `pg_restore` inside the Postgres container (or on host pointing at published port)

## Podman: assemble + restore + verify

From repo root after `git pull`:

```bash
chmod +x scripts/migration/*.sh data/backups/assemble_recruit_dump.sh

# Optional: Postgres published on host :5432
export DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:5432/recruit_db'

export PODMAN_CONTAINER=postgres   # your container name: podman ps
export PGDATABASE=recruit_db
export PGPASSWORD=postgres

./scripts/migration/prod-restore-podman.sh
```

Or step by step:

```bash
./scripts/migration/assemble-recruit-dump.sh
./scripts/migration/prod-restore-podman.sh --container postgres --db recruit_db
./scripts/migration/migration-verify.sh
```

If Postgres is only reachable via Podman (no host port):

```bash
unset DATABASE_URL
export PODMAN_CONTAINER=postgres
export PGDATABASE=recruit_db
./scripts/migration/migration-verify.sh
```

## Host-only restore (published port)

```bash
./data/backups/assemble_recruit_dump.sh
export DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:5432/recruit_db'
pg_restore --dbname="$DATABASE_URL" --no-owner --no-acl --verbose \
  data/backups/recruit_prod_cutover_20260709T1422Z.dump
./scripts/migration/migration-verify.sh
```

## Refresh baseline (source DB before a new dump)

```bash
export DATABASE_URL='postgresql://…/recruit_db'
./scripts/migration/migration-verify-baseline.sh
```

## Creating a new cutover dump (e.g. for a future deploy)

```bash
# From the source Postgres (adjust container/port to your source DB):
docker exec <source_postgres_container> pg_dump -U postgres -d recruit_db \
  -Fc --no-owner --no-privileges -f /tmp/recruit_db_production.dump
docker cp <source_postgres_container>:/tmp/recruit_db_production.dump /tmp/

BASE="recruit_prod_cutover_$(date -u +%Y%m%dT%H%MZ)"
SIZE=$(stat -f%z /tmp/recruit_db_production.dump 2>/dev/null || stat -c%s /tmp/recruit_db_production.dump)
BYTES_PER_PART=$(( (SIZE + 6) / 7 ))   # 7 parts
split -b "$BYTES_PER_PART" /tmp/recruit_db_production.dump "/tmp/${BASE}.part"
i=0; for f in /tmp/${BASE}.part*; do mv "$f" "/tmp/${BASE}.part${i}"; gzip -9 "/tmp/${BASE}.part${i}"; i=$((i+1)); done
shasum -a 256 /tmp/recruit_db_production.dump | awk -v b="$BASE" '{print $1"  "b".dump"}' > "data/backups/${BASE}.dump.sha256"
mv /tmp/${BASE}.part*.gz data/backups/

# Then update DEFAULT_DUMP_BASE in scripts/migration/_common.sh to $BASE,
# refresh data/migration_verify_baseline.json (see above), and update this README.
```

Python `migrations_cli` remains available but is **not** required for cutover.

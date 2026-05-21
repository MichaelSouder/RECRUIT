# RECRUIT production cutover dump (split for Git)

## Files in Git (7 parts, ~24–26 MB each)

- `recruit_prod_cutover_20260521T1455Z.part0.gz` … `part6.gz`
- `recruit_prod_cutover_20260521T1455Z.dump.sha256`
- `assemble_recruit_dump.sh` (wrapper)
- `../migration_verify_baseline.json`

Full **`.dump`** (~192 MB) is gitignored; reassemble locally.

## Requirements (bash only)

- `gzip`, `shasum` or `sha256sum`
- `podman` (restore into container)
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
  data/backups/recruit_prod_cutover_20260521T1455Z.dump
./scripts/migration/migration-verify.sh
```

## Refresh baseline (source DB before a new dump)

```bash
export DATABASE_URL='postgresql://…/recruit_db'
./scripts/migration/migration-verify-baseline.sh
```

Python `migrations_cli` remains available but is **not** required for cutover.

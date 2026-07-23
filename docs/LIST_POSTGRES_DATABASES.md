# Listing local Postgres databases and tables

Quick way to see every database on a local Postgres server, and every table
(with row counts and sizes) inside each one. Handy for sanity-checking which
of this repo's several local Postgres instances you're actually pointed at.

## Which Postgres are you running?

This repo can have more than one local Postgres instance depending on how
you started the stack:

| Compose file | Container | Image | Host port | Data |
| --- | --- | --- | --- | --- |
| `docker-compose.yml` | `recruit_postgres` | `postgres:15` | `25432` | Fresh, empty dev volume |
| `docker-compose.postgres-snapshot.yml` | `recruit_postgres_snapshot` | `postgres:13` | `15432` | Restored migrated data (see `scripts/restore-postgres-from-data-parts.sh`) |

`src/backend/app/config.py`'s default `DATABASE_URL` points at the **snapshot**
instance (`localhost:15432/recruit_db`), and that's what
`docker-compose.use-host-snapshot-db.yml` wires the backend to as well. The
plain `docker-compose.yml` Postgres (`25432`) is a separate, initially-empty
database used for the default all-in-Docker dev stack.

## Usage

```bash
# Auto-detect: local psql + default snapshot DB (localhost:15432), falling
# back to `docker exec` / `podman exec` into a running postgres container.
./scripts/list-postgres-databases.sh

# Only show tables for one database
./scripts/list-postgres-databases.sh -d recruit_db

# Point at a specific server/port explicitly (needs a local psql client)
./scripts/list-postgres-databases.sh -u postgresql://postgres:postgres@localhost:25432/postgres

# Force container-exec mode against a specific container name
./scripts/list-postgres-databases.sh -c recruit_postgres
```

Run `./scripts/list-postgres-databases.sh -h` for the full flag list.

### Connection resolution

1. `-u/--url`, or the `DATABASE_URL` env var — requires a local `psql` client.
2. A local `psql` client with no URL given — defaults to the snapshot DB
   (`postgresql://postgres:postgres@localhost:15432/recruit_db`).
3. No local `psql` client — falls back to `docker exec` / `podman exec` into
   a running container, trying `recruit_postgres_snapshot` then
   `recruit_postgres` (override with `-c/--container` or `PG_CONTAINER`).

If you don't have a local `psql` client and neither container is running,
the script fails with a pointer to start one, e.g.:

```bash
docker compose -f docker-compose.postgres-snapshot.yml up -d
```

### Sample output

```
[INFO]  Connecting via psql to postgresql://postgres:***@localhost:15432/recruit_db

[INFO]  Databases on this server:
 database  |  size
-----------+---------
 recruit_db | 42 MB

[ OK ]  Tables in database 'recruit_db':
 schema |     table      | est_rows | total_size
--------+----------------+----------+------------
 public | studies        |       12 | 96 kB
 public | subjects       |     1204 | 512 kB
 public | assessments    |     3310 | 1.2 MB
 public | session_notes  |      880 | 320 kB
 ...
```

`est_rows` comes from Postgres's live-tuple statistics
(`pg_stat_user_tables.n_live_tup`) — an estimate, not an exact `COUNT(*)`, but
fast even on large tables.

## Doing it by hand

If you'd rather run the queries yourself:

```bash
# List databases
psql "$DATABASE_URL" -c "\l+"

# List tables (all schemas) in the currently-connected database
psql "$DATABASE_URL" -c "\dt+ *.*"

# Or, without a local psql client, via a running container:
docker exec -it recruit_postgres_snapshot psql -U postgres -c "\l"
docker exec -it recruit_postgres_snapshot psql -U postgres -d recruit_db -c "\dt+ *.*"
```

## Troubleshooting

- **No `psql` on macOS**: `brew install libpq && brew link --force libpq`
  (Homebrew keeps `libpq` unlinked by default to avoid clashing with a full
  Postgres install). Alternatively, just let the script fall back to
  container-exec mode — no local client needed.
- **Script can't find a container**: confirm one is actually running with
  `docker ps` / `podman ps`, and that its name matches
  `recruit_postgres_snapshot` or `recruit_postgres` (or pass `-c <name>`).
- **Wrong data / empty tables**: you're probably pointed at the fresh
  `docker-compose.yml` Postgres (port `25432`) instead of the migrated
  snapshot (port `15432`). Pass `-u ...` or set `DATABASE_URL` explicitly.

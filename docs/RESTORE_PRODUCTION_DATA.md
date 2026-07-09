# Moving production data to a deployed server

`scripts/fix-missing-tables.sh` only creates empty table structures and (if
needed) a single seeded admin user — it never copies real application data
anywhere. If the deployed server needs the actual production data (subjects,
studies, session notes, assessments, users), that's a separate, explicit
step described here.

**This data is clinical research data (likely PII/PHI). Never commit a dump
file to git, upload it to a third-party service, or send it over an
unencrypted channel.**

## 1. Confirm which local database actually has the data

Don't assume — different local Postgres containers can look similar. Check
what the backend container you care about is actually pointed at:

```bash
docker inspect <backend_container> --format '{{range .Config.Env}}{{println .}}{{end}}' | grep DATABASE_URL
```

Then compare row counts across candidates before trusting one:

```bash
docker exec <postgres_container> psql -U postgres -d recruit_db -t -c "
  select 'users', count(*) from users
  union all select 'subjects', count(*) from subjects
  union all select 'studies', count(*) from studies
  union all select 'session_notes', count(*) from session_notes
  union all select 'assessments', count(*) from assessments;
"
```

## 2. Dump it

```bash
docker exec <postgres_container> pg_dump -U postgres -d recruit_db \
  -Fc --no-owner --no-privileges -f /tmp/recruit_db_production.dump
docker cp <postgres_container>:/tmp/recruit_db_production.dump ./recruit_db_production.dump
docker exec <postgres_container> rm -f /tmp/recruit_db_production.dump
```

`-Fc` (custom format) works with `pg_restore` regardless of minor version
differences between source and target Postgres, and lets you `--clean` on
restore (see below) so it's safe to run against a target DB that already has
some schema/seed data in it.

## 3. Transfer the dump to the server

Use whatever secure/air-gapped transfer method you already use for the
container image bundles (see `docs/AIRGAP_DEPLOY.md`) — e.g. an encrypted
USB/SFTP transfer to the secure host. Do not email it, put it in Slack, or
commit it to the repo.

## 4. Restore it on the server

```bash
git pull   # to get scripts/restore-production-dump.sh if not already present
./scripts/restore-production-dump.sh /path/to/recruit_db_production.dump
```

The script:
1. Auto-detects `docker` or `podman`.
2. Finds the running Postgres container (`postgres` — the name used by
   `airgap-stack-up.sh` — or `recruit_postgres` — the name used by the
   compose files; pass a name explicitly as the second argument otherwise).
3. Prompts for confirmation, since it uses `pg_restore --clean --if-exists`,
   which **drops and recreates** the application tables in that database
   before loading the dump — this intentionally overwrites whatever was
   there (e.g. an empty schema or a seeded admin user from
   `fix-missing-tables.sh`) with the real data from the dump.
4. Prints row counts afterward so you can confirm they match the source.

No backend restart is required afterward — it opens a new DB connection per
request. Log in with a real account from the restored data.

## Notes

- `--no-owner --no-privileges` on both dump and restore avoids failures if
  the Postgres role names differ slightly between source and target (both
  default to `postgres` in this project's compose/airgap setups, but the
  flags make the restore robust regardless).
- This was validated against a disposable throwaway Postgres container
  before being used against anything real — row counts matched exactly
  (37 users, 55,829 subjects, 52 studies, 4,354 session notes, 390,503
  assessments in the case that motivated this doc).

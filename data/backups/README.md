# RECRUIT production cutover dump (split for Git)

## Files to commit (7 parts, ~24–26 MB each)

- `recruit_prod_cutover_20260521T1455Z.part0.gz` … `part6.gz`
- `recruit_prod_cutover_20260521T1455Z.dump.sha256` (checksum of full dump)
- `assemble_recruit_dump.sh`
- `../migration_verify_baseline.json` (parent `data/` — prod verify after restore)

The full **`recruit_prod_cutover_20260521T1455Z.dump`** (~192 MB) is local-only; do not commit unless using Git LFS.

## Reassemble on prod (or any host)

```bash
cd data/backups
chmod +x assemble_recruit_dump.sh
./assemble_recruit_dump.sh
pg_restore --dbname="$PROD_DATABASE_URL" --no-owner --no-acl --verbose \
  recruit_prod_cutover_20260521T1455Z.dump
```

## Verify after restore

```bash
cd src/backend
export DATABASE_URL='postgresql://…/recruit_db'
python -m migrations_cli migration-verify
python -m migrations_cli deploy-check
```

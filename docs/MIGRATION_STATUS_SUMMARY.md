# Migration Status Summary

> **See [CURRENT_STATUS.md](./CURRENT_STATUS.md) for the up-to-date picture (2026).** Below is the December 2024 Rails-focused summary.

**Quick Reference** | See [MIGRATION_STATUS.md](./MIGRATION_STATUS.md) for full details

## Status: Migration Scripts NOT Implemented

### Finding
After comprehensive review, **migration scripts for converting data from the old Rails schema to the new FastAPI/SQLAlchemy schema do NOT exist**.

## What Exists

1. **Migration Strategy Document** (`plans/04-migration-strategy.md`)
   - Contains planning and templates
   - No actual working scripts

2. **Schema Migration Scripts** (`src/backend/scripts/`)
   - Only scripts for adding columns to NEW schema
   - NOT for migrating from old schema

## What's Missing

### Critical Gaps

1. **No Data Export Scripts**
   - No scripts to export data from old Rails database
   - Need: `export_rails_data.py` and related scripts

2. **No Data Import Scripts**
   - No scripts to import data into new database
   - Need: `import_to_new_db.py` and related scripts

3. **No Data Transformation Scripts**
   - No scripts to transform old format to new format
   - Need: Field mapping, enum conversion, assessment consolidation

4. **No Validation Scripts**
   - No scripts to validate migration completeness
   - Need: Record count comparison, data integrity checks

## Schema Differences

### Old Schema (Rails)
- **148 tables** total
- Individual assessment tables: `moca`, `dass21`, `nihcog`, `pssqi`, etc.
- `admin_users` table (Devise-based)
- Integer enums for sex, race, status
- String `created_by` (username)

### New Schema (FastAPI)
- **~7 core tables** + junction tables
- Unified `assessments` table with JSON data field
- `users` table (JWT-based)
- String enums for sex, race, status
- Integer `created_by` (user ID foreign key)

## Key Migration Challenges

1. **Assessment Consolidation**: 50+ individual assessment tables → 1 unified table
2. **Password Migration**: Devise format → bcrypt format (may need password reset)
3. **Enum Conversion**: Integer IDs → String values
4. **Reference Conversion**: String usernames → Integer user IDs
5. **Data Volume**: 148 tables, potentially large datasets

## Required Scripts

### Priority 1: Core Migration
- `export_rails_data.py` - Export from old database
- `transform_data.py` - Transform data formats
- `import_to_new_db.py` - Import to new database
- `validate_migration.py` - Validate migration

### Priority 2: Assessment Migration
- `consolidate_assessments.py` - Consolidate assessment tables
- `map_assessment_fields.py` - Map fields to JSON format

## Implementation Estimate

**Time Required**: 4-6 weeks
- Week 1: Export scripts
- Week 2: Transformation scripts
- Week 3: Import scripts
- Week 4: Validation scripts
- Week 5-6: Testing and refinement

## Next Steps

1. Create `src/backend/scripts/migrate/` directory
2. Implement export scripts starting with core tables
3. Implement transformation scripts with field mappings
4. Implement import scripts with error handling
5. Implement validation scripts
6. Test on development database
7. Document migration process

## Recommendation

**Immediate Action**: Begin implementing migration scripts following the strategy in `plans/04-migration-strategy.md`. Start with export scripts for core tables (users, subjects, studies) and work incrementally.

---

**Status**: Migration scripts need to be implemented  
**Last Updated**: December 2024


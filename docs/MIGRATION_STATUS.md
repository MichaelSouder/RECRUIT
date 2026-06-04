# Migration Status: Old Rails Schema to New Schema

> **2026 update:** For **current** status (Postgres `arc` / `dvbic_*` snapshot path, Alembic, Phase A discovery, migration plan), see **[CURRENT_STATUS.md](./CURRENT_STATUS.md)**. This file remains a **Rails / `old/`** audit from December 2024.

**Date**: December 2024  
**Status**: Migration Scripts NOT Implemented

## Executive Summary

After comprehensive review, **migration scripts for converting data from the old Rails schema to the new FastAPI/SQLAlchemy schema do NOT exist**. The project contains:

1. **Migration Strategy Document** (`plans/04-migration-strategy.md`) - Contains templates and planning, but no actual scripts
2. **Schema Migration Scripts** - Only scripts for adding columns to the NEW schema (not for migrating from old)
3. **No Data Export Scripts** - No scripts to export data from the old Rails database
4. **No Data Import Scripts** - No scripts to import data into the new database
5. **No Validation Scripts** - No scripts to validate the migration

## Current State

### What Exists

#### 1. Migration Strategy Document
**Location**: `plans/04-migration-strategy.md`

**Content**: 
- Comprehensive migration strategy and planning
- Template code examples for export/import scripts
- Validation script templates
- Migration phases and procedures

**Status**: Planning document only - templates are not implemented

#### 2. Schema Migration Scripts (New Schema Only)
**Location**: `src/backend/scripts/`

**Existing Scripts**:
- `add_assessment_time_to_assessments.py` - Adds column to NEW schema
- `add_enrollment_status_to_subjects.py` - Adds column to NEW schema
- `add_ethnicity_to_subjects.py` - Adds column to NEW schema
- `add_location_phone_to_users.py` - Adds column to NEW schema
- `add_pi_to_studies.py` - Adds column to NEW schema
- `add_piv_certificate_id_to_users.py` - Adds column to NEW schema
- `create_audit_logs_table.py` - Creates table in NEW schema
- `seed_mock_data.py` - Seeds NEW schema with test data

**Purpose**: These scripts modify the NEW schema structure, not migrate data from the OLD schema.

### What's Missing

#### 1. Data Export Scripts
**Required**: Scripts to export data from the old Rails database

**Missing Scripts**:
- `export_rails_data.py` - Export all tables from Rails database
- `export_subjects.py` - Export subjects table
- `export_studies.py` - Export studies table
- `export_assessments.py` - Export all assessment tables (moca, dass21, nihcog, etc.)
- `export_session_notes.py` - Export session notes
- `export_users.py` - Export admin_users and convert to users

#### 2. Data Import Scripts
**Required**: Scripts to import data into the new database

**Missing Scripts**:
- `import_to_new_db.py` - Main import script
- `import_subjects.py` - Import subjects with data transformation
- `import_studies.py` - Import studies with data transformation
- `import_assessments.py` - Import and consolidate assessment tables
- `import_session_notes.py` - Import session notes
- `import_users.py` - Import and convert admin_users to users

#### 3. Data Transformation Scripts
**Required**: Scripts to transform data from old format to new format

**Missing Scripts**:
- `transform_subjects.py` - Transform subject data (enum conversions, field mappings)
- `transform_studies.py` - Transform study data
- `transform_assessments.py` - Consolidate multiple assessment tables into unified format
- `transform_users.py` - Convert admin_users to users format

#### 4. Validation Scripts
**Required**: Scripts to validate migration completeness and accuracy

**Missing Scripts**:
- `validate_migration.py` - Compare old and new databases
- `validate_record_counts.py` - Verify record counts match
- `validate_data_integrity.py` - Verify data values match
- `validate_relationships.py` - Verify relationships preserved

## Schema Comparison

### Old Schema (Rails)
**Location**: `old/db/schema.rb`

**Key Tables**:
- `subjects` - Subject/patient data
- `studies` - Research studies
- `admin_users` - User accounts (Devise-based)
- Individual assessment tables:
  - `moca` - MoCA assessments
  - `dass21` - DASS-21 assessments
  - `nihcog` - NIH Toolbox assessments
  - `pssqi` - PSSQI assessments
  - `vision_acuity` - Vision assessments
  - `balance_board` - Balance assessments
  - And many more specialized assessment tables
- `session_note` or similar - Session notes (need to verify exact table name)

**Total Tables**: 148 tables in old schema

### New Schema (FastAPI/SQLAlchemy)
**Location**: `src/backend/app/models/`

**Key Tables**:
- `subjects` - Subject/patient data (unified structure)
- `studies` - Research studies (unified structure)
- `users` - User accounts (JWT-based, replaces admin_users)
- `assessments` - Unified assessment table (replaces all individual assessment tables)
- `assessment_types` - Dynamic assessment type definitions
- `session_notes` - Session notes (unified structure)
- `audit_logs` - Audit trail

**Total Tables**: ~7 core tables + junction tables

## Key Schema Differences

### 1. Subjects Table

**Old Schema** (from Rails):
- Uses integer IDs for sex, race (references lookup tables)
- May have different field names
- Uses `created_by` as string (username)
- May have additional fields not in new schema

**New Schema**:
- Uses string values for sex ('male', 'female')
- Uses string values for race and ethnicity
- Uses `created_by` as integer (user ID foreign key)
- Has `enrollment_status` field
- Has `ethnicity` field

**Migration Required**: 
- Convert enum integers to strings
- Map field names
- Convert `created_by` from username to user ID
- Handle missing fields

### 2. Studies Table

**Old Schema**:
- Uses integer for status (references lookup table)
- Uses string for `investigator` (name)
- Uses string for `created_by` (username)
- May have `irb_number` field

**New Schema**:
- Uses string for status ('active', 'completed', 'paused')
- Uses `principal_investigator_id` (foreign key to users)
- Uses integer for `created_by` (user ID)

**Migration Required**:
- Convert status enum
- Map investigator name to user ID
- Convert created_by format

### 3. Assessments

**Old Schema**:
- Multiple separate tables: `moca`, `dass21`, `nihcog`, `pssqi`, `vision_acuity`, `balance_board`, etc.
- Each table has specific fields for that assessment type
- Uses `visit_num` field
- Uses `date` field
- Uses `created_by` as string

**New Schema**:
- Single unified `assessments` table
- Uses `assessment_type` to differentiate
- Uses `data` JSON field for assessment-specific data
- Uses `assessment_date` and `assessment_time`
- Uses `created_by` as integer (user ID)

**Migration Required**:
- Consolidate all assessment tables into one
- Map assessment-specific fields to JSON `data` field
- Convert `visit_num` handling
- Convert `created_by` format
- Map assessment type names

### 4. Users

**Old Schema**:
- `admin_users` table (Devise-based)
- Uses `encrypted_password` (Devise format)
- Has `reset_password_token`, `remember_created_at` (Devise fields)
- No role field (uses is_superuser boolean)

**New Schema**:
- `users` table (JWT-based)
- Uses `hashed_password` (bcrypt format)
- Has `role` field ('admin', 'researcher', 'viewer')
- Has `location`, `phone`, `piv_certificate_id` fields
- No Devise-specific fields

**Migration Required**:
- Convert password hashing format (may need to reset passwords)
- Map is_superuser to role field
- Add new fields (location, phone, piv_certificate_id) - may be NULL
- Remove Devise-specific fields

### 5. Session Notes

**Old Schema**:
- Need to verify exact table name and structure
- May be `session_note` or `sessionnotes` or similar

**New Schema**:
- `session_notes` table
- Standardized structure

**Migration Required**:
- Map table name
- Map field names
- Convert created_by format

## Required Migration Scripts

### Priority 1: Core Data Migration

#### 1. Export Rails Data
**File**: `src/backend/scripts/migrate/export_rails_data.py`

**Functionality**:
- Connect to old Rails PostgreSQL database
- Export all core tables to JSON/CSV
- Handle large datasets with pagination
- Preserve relationships
- Export in dependency order (users first, then subjects, then assessments)

**Tables to Export**:
1. `admin_users` → `users`
2. `subjects` → `subjects`
3. `studies` → `studies`
4. All assessment tables → `assessments`
5. Session notes table → `session_notes`
6. Junction tables for relationships

#### 2. Transform Data
**File**: `src/backend/scripts/migrate/transform_data.py`

**Functionality**:
- Transform data formats (enums, dates, etc.)
- Map field names
- Consolidate assessment tables
- Convert user references
- Handle missing/null data

**Key Transformations**:
- Sex: integer → string ('male', 'female')
- Race: integer → string
- Status: integer → string
- Assessment tables → unified format
- Password: Devise → bcrypt (or reset)
- created_by: string → integer (user ID)

#### 3. Import to New Database
**File**: `src/backend/scripts/migrate/import_to_new_db.py`

**Functionality**:
- Import transformed data into new database
- Maintain referential integrity
- Handle errors gracefully
- Log all operations
- Support rollback

#### 4. Validate Migration
**File**: `src/backend/scripts/migrate/validate_migration.py`

**Functionality**:
- Compare record counts
- Validate data integrity
- Check relationships
- Verify timestamps
- Generate validation report

### Priority 2: Assessment Consolidation

The old schema has many individual assessment tables that need to be consolidated:

**Old Assessment Tables** (partial list):
- `moca`
- `dass21`
- `nihcog`
- `pssqi`
- `vision_acuity`
- `balance_board`
- `bai` (Beck Anxiety Inventory)
- `bssi` (Beck Scale for Suicide Ideation)
- `hit6` (Headache Impact Test)
- `mpai` (Mayo-Portland Adaptability Inventory)
- And many more...

**New Structure**:
- Single `assessments` table
- `assessment_type` field identifies type
- `data` JSON field contains assessment-specific fields

**Migration Strategy**:
1. Export each assessment table
2. Transform to unified format
3. Set `assessment_type` based on source table
4. Move assessment-specific fields to `data` JSON
5. Import into unified `assessments` table

## Implementation Recommendations

### Phase 1: Create Export Scripts (Week 1)
1. Create `src/backend/scripts/migrate/` directory
2. Implement `export_rails_data.py`
3. Test export on development database
4. Verify data completeness

### Phase 2: Create Transformation Scripts (Week 2)
1. Implement `transform_data.py`
2. Create field mapping configurations
3. Handle enum conversions
4. Test transformations

### Phase 3: Create Import Scripts (Week 3)
1. Implement `import_to_new_db.py`
2. Add error handling and logging
3. Test import process
4. Verify data integrity

### Phase 4: Create Validation Scripts (Week 4)
1. Implement `validate_migration.py`
2. Add comprehensive validation checks
3. Generate validation reports
4. Test validation process

### Phase 5: Test Migration (Week 5-6)
1. Run full migration on test database
2. Validate all data
3. Test application functionality
4. Fix any issues
5. Document process

## Critical Considerations

### 1. Password Migration
**Issue**: Devise and bcrypt use different hashing algorithms
**Options**:
- Reset all passwords (users must set new passwords)
- Implement dual authentication during transition
- Convert hashes if possible (complex)

**Recommendation**: Reset passwords and require users to set new passwords on first login

### 2. Assessment Data Consolidation
**Issue**: Many assessment tables with different structures
**Challenge**: Mapping all fields to JSON format
**Solution**: 
- Create mapping configuration for each assessment type
- Preserve all data in JSON format
- Document field mappings

### 3. Data Volume
**Issue**: 148 tables in old schema, potentially large datasets
**Considerations**:
- Use batch processing
- Implement progress tracking
- Handle timeouts
- Support resume capability

### 4. Referential Integrity
**Issue**: Converting string references to integer foreign keys
**Challenge**: Mapping usernames to user IDs, subject names to IDs
**Solution**:
- Create mapping dictionaries during export
- Use mappings during import
- Validate all foreign keys

### 5. Timestamps
**Issue**: Preserving created_at and updated_at
**Solution**: 
- Export timestamps as-is
- Import preserving original timestamps
- Validate timestamp preservation

## Next Steps

### Immediate Actions Required

1. **Create Migration Scripts Directory**
   ```bash
   mkdir -p src/backend/scripts/migrate
   ```

2. **Implement Export Script**
   - Start with core tables (users, subjects, studies)
   - Add assessment tables incrementally
   - Test on development database

3. **Implement Transformation Script**
   - Create field mapping configuration
   - Handle enum conversions
   - Test transformations

4. **Implement Import Script**
   - Import in correct order (respect foreign keys)
   - Add error handling
   - Implement rollback capability

5. **Implement Validation Script**
   - Compare record counts
   - Validate data integrity
   - Generate reports

### Documentation Needed

1. **Field Mapping Document** - Document all field mappings between old and new schemas
2. **Assessment Type Mapping** - Document how each old assessment table maps to new structure
3. **Migration Runbook** - Step-by-step guide for executing migration
4. **Rollback Procedures** - How to revert migration if needed
5. **Data Validation Checklist** - What to check after migration

## Conclusion

**Status**: Migration scripts do NOT exist. Only planning documents and templates are available.

**Critical Gap**: No actual working scripts to migrate data from the old Rails schema to the new FastAPI/SQLAlchemy schema.

**Recommendation**: Implement migration scripts following the strategy outlined in `plans/04-migration-strategy.md`, starting with export scripts and working through transformation, import, and validation.

**Estimated Effort**: 4-6 weeks to implement and test complete migration solution.

---

**Last Updated**: December 2024  
**Next Review**: After migration scripts are implemented


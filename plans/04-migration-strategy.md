# RECRUIT Platform Migration Strategy

## Overview

This document outlines the comprehensive strategy for migrating from the existing Rails application to the new Python/React platform, ensuring zero data loss and minimal downtime.

## Migration Principles

1. **Data Integrity First**: All data must be preserved accurately
2. **Zero Downtime**: Minimize service interruption
3. **Rollback Capability**: Ability to revert if issues arise
4. **Validation**: Comprehensive data validation at each step
5. **Documentation**: Complete documentation of migration process

## Pre-Migration Analysis

### Current Database Analysis

#### Database Schema Review
- [ ] Document all tables and relationships
- [ ] Identify foreign key constraints
- [ ] Document indexes and their purposes
- [ ] Review data types and constraints
- [ ] Identify custom functions/triggers
- [ ] Document views if any

#### Data Volume Assessment
- [ ] Count records per table
- [ ] Calculate total database size
- [ ] Identify largest tables
- [ ] Estimate migration time
- [ ] Identify data quality issues

#### Data Quality Audit
- [ ] Identify NULL values in required fields
- [ ] Find orphaned records
- [ ] Check for duplicate records
- [ ] Validate foreign key integrity
- [ ] Review data format consistency

### Application Feature Audit

#### Feature Inventory
- [ ] List all ActiveAdmin resources
- [ ] Document all user workflows
- [ ] Identify custom business logic
- [ ] Document validation rules
- [ ] List all reports/exports
- [ ] Document permissions/roles

#### API Endpoint Mapping
- [ ] Map Rails routes to new API endpoints
- [ ] Document request/response formats
- [ ] Identify authentication requirements
- [ ] Document rate limiting needs

## Migration Phases

### Phase 1: Preparation (Weeks 1-2)

#### Database Schema Migration

**Step 1.1: Create New Schema**
- Design new PostgreSQL schema
- Create migration scripts using Alembic
- Set up database in development environment
- Review and optimize schema design

**Step 1.2: Schema Validation**
- Compare old and new schemas
- Verify all fields are mapped
- Check data type compatibility
- Validate constraints

#### Data Mapping Documentation

**Create Mapping Documents:**
- Table-to-table mapping
- Field-to-field mapping
- Data transformation rules
- Enum/value mappings
- Relationship mappings

**Example Mapping:**
```yaml
subjects:
  old_table: subjects
  new_table: subjects
  fields:
    id: id (integer, primary key)
    first_name: first_name (string)
    last_name: last_name (string)
    date_of_birth: date_of_birth (date)
    ssn: ssn (string, encrypted)
    sex: sex (enum: 0=male, 1=female)
    created_at: created_at (timestamp)
    updated_at: updated_at (timestamp)
```

### Phase 2: Development Environment Migration (Weeks 3-4)

#### Data Export Scripts

**Create Export Scripts:**
```python
# scripts/export_rails_data.py
# Export data from Rails database to JSON/CSV
```

**Export Strategy:**
1. Export table by table
2. Include relationships
3. Preserve timestamps
4. Handle binary data
5. Compress large exports

#### Data Import Scripts

**Create Import Scripts:**
```python
# scripts/import_to_new_db.py
# Import data into new database with validation
```

**Import Features:**
- Data validation
- Error logging
- Progress tracking
- Rollback capability
- Duplicate detection

#### Validation Scripts

**Create Validation Scripts:**
```python
# scripts/validate_migration.py
# Compare old and new databases
```

**Validation Checks:**
- Record counts match
- Data values match
- Relationships preserved
- Timestamps preserved
- No data loss

### Phase 3: Test Migration (Weeks 5-6)

#### Test Environment Setup
- Set up staging database
- Copy production data snapshot
- Run full migration
- Validate results

#### Test Scenarios
1. **Data Integrity Tests**
   - All records migrated
   - No data corruption
   - Relationships intact

2. **Functional Tests**
   - All features work
   - API endpoints functional
   - UI displays correctly

3. **Performance Tests**
   - Query performance
   - API response times
   - Page load times

#### Issue Resolution
- Document all issues
- Fix migration scripts
- Update validation rules
- Re-run migration

### Phase 4: Parallel Running (Weeks 7-8)

#### Dual-Write Strategy
- Write to both old and new systems
- Validate writes match
- Monitor for discrepancies

#### Read Comparison
- Compare query results
- Validate data consistency
- Document differences

#### Gradual Cutover
- Start with read-only features
- Move to write operations
- Monitor closely

### Phase 5: Production Migration (Week 9)

#### Pre-Migration Checklist

**Backup:**
- [ ] Full database backup
- [ ] Application code backup
- [ ] Configuration backup
- [ ] Verify backup integrity

**Communication:**
- [ ] Notify stakeholders
- [ ] Schedule maintenance window
- [ ] Prepare rollback plan
- [ ] Set up monitoring

**Environment:**
- [ ] Production database ready
- [ ] Application deployed
- [ ] Monitoring active
- [ ] Support team ready

#### Migration Execution

**Step 5.1: Final Data Export**
```bash
# Export from production Rails database
python scripts/export_production_data.py
```

**Step 5.2: Data Import**
```bash
# Import to new production database
python scripts/import_production_data.py --validate
```

**Step 5.3: Validation**
```bash
# Validate migration
python scripts/validate_production_migration.py
```

**Step 5.4: Application Deployment**
- Deploy new application
- Update DNS/routing
- Monitor for issues

**Step 5.5: Smoke Tests**
- Test critical workflows
- Verify data access
- Check performance
- Validate security

#### Rollback Plan

**If Issues Detected:**
1. Immediately revert DNS/routing
2. Restore old application
3. Investigate issues
4. Fix and re-attempt

**Rollback Checklist:**
- [ ] DNS/routing reverted
- [ ] Old application active
- [ ] Data integrity verified
- [ ] Issues documented

### Phase 6: Post-Migration (Weeks 10-11)

#### Monitoring
- Monitor application performance
- Watch for errors
- Track user feedback
- Monitor database performance

#### Data Verification
- Ongoing data validation
- Compare critical metrics
- Verify user workflows
- Check report accuracy

#### Optimization
- Performance tuning
- Query optimization
- Index optimization
- Cache tuning

#### Documentation
- Document migration process
- Record issues and solutions
- Update runbooks
- Create knowledge base

## Data Migration Scripts

### Export Script Template

```python
# scripts/export_rails_data.py
import psycopg2
import json
import csv
from datetime import datetime

def export_table(connection, table_name, output_file):
    """Export a table to JSON"""
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    data = [dict(zip(columns, row)) for row in rows]
    
    with open(output_file, 'w') as f:
        json.dump(data, f, default=str, indent=2)
    
    print(f"Exported {len(data)} records from {table_name}")

def main():
    # Connect to Rails database
    conn = psycopg2.connect(
        host="localhost",
        database="recruit_rails",
        user="postgres",
        password="password"
    )
    
    tables = ['subjects', 'studies', 'demographics', ...]
    
    for table in tables:
        export_table(conn, table, f"exports/{table}.json")
    
    conn.close()

if __name__ == "__main__":
    main()
```

### Import Script Template

```python
# scripts/import_to_new_db.py
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Subject, Study, ...

def import_table(session, table_name, data_file, model_class):
    """Import data from JSON to database"""
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    imported = 0
    errors = []
    
    for record in data:
        try:
            # Transform data if needed
            transformed = transform_record(record)
            
            # Create model instance
            instance = model_class(**transformed)
            session.add(instance)
            
            imported += 1
        except Exception as e:
            errors.append({
                'record': record,
                'error': str(e)
            })
    
    session.commit()
    print(f"Imported {imported} records to {table_name}")
    if errors:
        print(f"Errors: {len(errors)}")
        with open(f"errors/{table_name}_errors.json", 'w') as f:
            json.dump(errors, f, indent=2)

def transform_record(record):
    """Transform record from old format to new format"""
    # Example: Convert sex enum
    if 'sex' in record:
        record['sex'] = 'male' if record['sex'] == 0 else 'female'
    
    # Example: Handle date formats
    if 'date_of_birth' in record:
        # Convert to proper date format
        pass
    
    return record

def main():
    engine = create_engine("postgresql://user:pass@localhost/recruit_new")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    tables = [
        ('subjects', 'exports/subjects.json', Subject),
        ('studies', 'exports/studies.json', Study),
        # ...
    ]
    
    for table_name, data_file, model_class in tables:
        import_table(session, table_name, data_file, model_class)
    
    session.close()

if __name__ == "__main__":
    main()
```

### Validation Script Template

```python
# scripts/validate_migration.py
import psycopg2
from sqlalchemy import create_engine, text

def validate_table_counts(old_conn, new_conn, table_name):
    """Compare record counts between old and new databases"""
    old_cursor = old_conn.cursor()
    old_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    old_count = old_cursor.fetchone()[0]
    
    new_engine = create_engine(new_conn)
    with new_engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        new_count = result.scalar()
    
    if old_count == new_count:
        print(f"✓ {table_name}: {old_count} records match")
        return True
    else:
        print(f"✗ {table_name}: {old_count} != {new_count}")
        return False

def validate_sample_data(old_conn, new_conn, table_name, sample_size=10):
    """Compare sample records between databases"""
    # Implementation for comparing actual data values
    pass

def main():
    old_conn = psycopg2.connect(
        host="localhost",
        database="recruit_rails",
        user="postgres",
        password="password"
    )
    
    new_conn = "postgresql://user:pass@localhost/recruit_new"
    
    tables = ['subjects', 'studies', ...]
    
    all_valid = True
    for table in tables:
        if not validate_table_counts(old_conn, new_conn, table):
            all_valid = False
    
    if all_valid:
        print("\n✓ All validations passed!")
    else:
        print("\n✗ Some validations failed!")
    
    old_conn.close()

if __name__ == "__main__":
    main()
```

## Assessment-Specific Migration

### Assessment Data Transformation

Many assessments may need special handling:

```python
# scripts/transform_assessments.py

def transform_nihcog(old_record):
    """Transform NIH Cog assessment"""
    return {
        'subject_id': old_record['subject_id'],
        'assessment_date': old_record['date'],
        'scores': {
            'total_score': old_record['total'],
            # Map individual sub-scores
        },
        'raw_data': old_record  # Preserve original
    }

def transform_pssqi(old_record):
    """Transform PSSQI sleep assessment"""
    # Handle PSSQI-specific transformations
    pass
```

## Testing Strategy

### Unit Tests
- Test data transformation functions
- Test import/export scripts
- Test validation logic

### Integration Tests
- Test full migration on sample data
- Test rollback procedures
- Test data integrity

### User Acceptance Testing
- Test all user workflows
- Verify data accuracy
- Check performance
- Validate reports

## Risk Mitigation

### Data Loss Prevention
- Multiple backups
- Validation at each step
- Transaction-based imports
- Rollback capability

### Performance Issues
- Batch processing
- Index optimization
- Connection pooling
- Progress monitoring

### Downtime Minimization
- Parallel running period
- Gradual cutover
- Maintenance window planning
- Quick rollback capability

## Success Metrics

### Migration Success Criteria
- [ ] 100% of records migrated
- [ ] Zero data loss
- [ ] All validations pass
- [ ] Performance meets or exceeds old system
- [ ] All features functional
- [ ] User acceptance achieved

### Performance Benchmarks
- API response time < 200ms (p95)
- Page load time < 2s
- Database query time < 100ms (p95)
- Zero critical errors

## Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|-----------------|
| Preparation | 2 weeks | Schema design, mapping docs |
| Development | 2 weeks | Export/import scripts |
| Test Migration | 2 weeks | Validated test migration |
| Parallel Running | 2 weeks | Dual-write validation |
| Production Migration | 1 week | Production cutover |
| Post-Migration | 2 weeks | Monitoring, optimization |

**Total: 11 weeks**

---

*Document Version: 1.0*  
*Last Updated: [Current Date]*



"""
Migration script to add assessment_time column to assessments table
Run this script to update existing databases.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.database import engine

def migrate():
    """Add assessment_time column to assessments table"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'assessments' not in existing_tables:
            print("✗ assessments table does not exist")
            return
        
        with engine.connect() as conn:
            if engine.url.drivername == 'sqlite':
                # SQLite
                result = conn.execute(text("PRAGMA table_info(assessments)"))
                columns = [row[1] for row in result]
                
                if 'assessment_time' not in columns:
                    conn.execute(text("ALTER TABLE assessments ADD COLUMN assessment_time TIME"))
                    conn.commit()
                    print("✓ Added assessment_time column to assessments table (SQLite)")
                else:
                    print("✓ Column assessment_time already exists")
            else:
                # PostgreSQL
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='assessments' AND column_name='assessment_time'
                """))
                if result.fetchone() is None:
                    conn.execute(text("""
                        ALTER TABLE assessments 
                        ADD COLUMN assessment_time TIME
                    """))
                    conn.commit()
                    print("✓ Added assessment_time column to assessments table (PostgreSQL)")
                else:
                    print("✓ Column assessment_time already exists")
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    migrate()



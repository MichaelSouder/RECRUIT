"""
Migration script to add ethnicity column to subjects table
Run this script to update existing databases.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.database import engine

def migrate():
    """Add ethnicity column to subjects table"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'subjects' not in existing_tables:
            print("✗ subjects table does not exist")
            return
        
        with engine.connect() as conn:
            if engine.url.drivername == 'sqlite':
                # SQLite
                result = conn.execute(text("PRAGMA table_info(subjects)"))
                columns = [row[1] for row in result]
                
                if 'ethnicity' not in columns:
                    conn.execute(text("ALTER TABLE subjects ADD COLUMN ethnicity VARCHAR"))
                    conn.commit()
                    print("✓ Added ethnicity column to subjects table (SQLite)")
                else:
                    print("✓ Column ethnicity already exists")
            else:
                # PostgreSQL
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='subjects' AND column_name='ethnicity'
                """))
                if result.fetchone() is None:
                    conn.execute(text("""
                        ALTER TABLE subjects 
                        ADD COLUMN ethnicity VARCHAR
                    """))
                    conn.commit()
                    print("✓ Added ethnicity column to subjects table (PostgreSQL)")
                else:
                    print("✓ Column ethnicity already exists")
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    migrate()






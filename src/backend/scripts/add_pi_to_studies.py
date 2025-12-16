"""
Migration script to add principal_investigator_id column to studies table
Run this script to update existing databases.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine

def migrate():
    """Add principal_investigator_id column to studies table"""
    try:
        with engine.connect() as conn:
            # Check if column already exists
            if engine.url.drivername == 'sqlite':
                # SQLite
                result = conn.execute(text("PRAGMA table_info(studies)"))
                columns = [row[1] for row in result]
                if 'principal_investigator_id' not in columns:
                    conn.execute(text("ALTER TABLE studies ADD COLUMN principal_investigator_id INTEGER"))
                    conn.commit()
                    print("✓ Added principal_investigator_id column to studies table (SQLite)")
                else:
                    print("✓ Column principal_investigator_id already exists")
            else:
                # PostgreSQL
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='studies' AND column_name='principal_investigator_id'
                """))
                if result.fetchone() is None:
                    conn.execute(text("""
                        ALTER TABLE studies 
                        ADD COLUMN principal_investigator_id INTEGER 
                        REFERENCES users(id)
                    """))
                    conn.commit()
                    print("✓ Added principal_investigator_id column to studies table (PostgreSQL)")
                else:
                    print("✓ Column principal_investigator_id already exists")
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()






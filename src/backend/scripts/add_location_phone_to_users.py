"""
Migration script to add location and phone columns to users table
Run this script to update existing databases.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.database import engine

def migrate():
    """Add location and phone columns to users table"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'users' not in existing_tables:
            print("✗ users table does not exist")
            return
        
        with engine.connect() as conn:
            if engine.url.drivername == 'sqlite':
                # SQLite
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                
                if 'location' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN location VARCHAR"))
                    conn.commit()
                    print("✓ Added location column to users table (SQLite)")
                else:
                    print("✓ Column location already exists")
                
                if 'phone' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR"))
                    conn.commit()
                    print("✓ Added phone column to users table (SQLite)")
                else:
                    print("✓ Column phone already exists")
            else:
                # PostgreSQL
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name IN ('location', 'phone')
                """))
                existing_columns = [row[0] for row in result]
                
                if 'location' not in existing_columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN location VARCHAR"))
                    conn.commit()
                    print("✓ Added location column to users table (PostgreSQL)")
                else:
                    print("✓ Column location already exists")
                
                if 'phone' not in existing_columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR"))
                    conn.commit()
                    print("✓ Added phone column to users table (PostgreSQL)")
                else:
                    print("✓ Column phone already exists")
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    migrate()






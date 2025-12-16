import sys
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine

def migrate():
    """Add piv_certificate_id column to users table"""
    try:
        with engine.connect() as conn:
            # Check if column already exists
            if engine.url.drivername == 'sqlite':
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                if 'piv_certificate_id' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN piv_certificate_id VARCHAR(255)"))
                    conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_piv_certificate_id ON users(piv_certificate_id)"))
                    conn.commit()
                    print("✓ Added piv_certificate_id column to users table (SQLite)")
                else:
                    print("✓ Column piv_certificate_id already exists")
            else: # PostgreSQL
                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='users' AND column_name='piv_certificate_id'
                """))
                if result.fetchone() is None:
                    conn.execute(text("ALTER TABLE users ADD COLUMN piv_certificate_id VARCHAR(255)"))
                    conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_piv_certificate_id ON users(piv_certificate_id)"))
                    conn.commit()
                    print("✓ Added piv_certificate_id column to users table (PostgreSQL)")
                else:
                    print("✓ Column piv_certificate_id already exists")
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()


"""
Migration script to create audit_logs table for FDA-compliant audit trail
Run this script to create the audit logs table in existing databases.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.database import engine, Base
from app.models.audit_log import AuditLog

def migrate():
    """Create audit_logs table if it doesn't exist"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if 'audit_logs' in existing_tables:
            print("✓ audit_logs table already exists")
            return
        
        with engine.connect() as conn:
            if engine.url.drivername == 'sqlite':
                # SQLite
                conn.execute(text("""
                    CREATE TABLE audit_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        user_id INTEGER NOT NULL,
                        user_email VARCHAR(255) NOT NULL,
                        user_full_name VARCHAR(255),
                        action VARCHAR(50) NOT NULL,
                        entity_type VARCHAR(100) NOT NULL,
                        entity_id INTEGER NOT NULL,
                        entity_name VARCHAR(255),
                        field_name VARCHAR(100),
                        old_value TEXT,
                        new_value TEXT,
                        change_summary TEXT,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        session_id VARCHAR(255),
                        additional_context TEXT,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create indexes
                conn.execute(text("CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp)"))
                conn.execute(text("CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id)"))
                conn.execute(text("CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id)"))
                conn.execute(text("CREATE INDEX idx_audit_logs_action ON audit_logs(action)"))
                
                conn.commit()
                print("✓ Created audit_logs table with indexes (SQLite)")
            else:
                # PostgreSQL
                conn.execute(text("""
                    CREATE TABLE audit_logs (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        user_id INTEGER NOT NULL,
                        user_email VARCHAR(255) NOT NULL,
                        user_full_name VARCHAR(255),
                        action VARCHAR(50) NOT NULL,
                        entity_type VARCHAR(100) NOT NULL,
                        entity_id INTEGER NOT NULL,
                        entity_name VARCHAR(255),
                        field_name VARCHAR(100),
                        old_value TEXT,
                        new_value TEXT,
                        change_summary TEXT,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        session_id VARCHAR(255),
                        additional_context TEXT,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create indexes
                conn.execute(text("CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp)"))
                conn.execute(text("CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id)"))
                conn.execute(text("CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id)"))
                conn.execute(text("CREATE INDEX idx_audit_logs_action ON audit_logs(action)"))
                
                conn.commit()
                print("✓ Created audit_logs table with indexes (PostgreSQL)")
        
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    migrate()






#!/usr/bin/env python3
"""Test script to check backend setup and identify issues"""

import sys
import os

print("=" * 60)
print("RECRUIT Backend Setup Test")
print("=" * 60)

# Check Python version
print(f"\n✓ Python version: {sys.version}")

# Check if we're in the right directory
if not os.path.exists("app"):
    print("\n✗ Error: 'app' directory not found. Please run from src/backend/")
    sys.exit(1)
print("\n✓ Found app directory")

# Try importing modules
print("\nTesting imports...")
try:
    from app.config import settings
    print("✓ Config imported")
except Exception as e:
    print(f"✗ Config import failed: {e}")
    sys.exit(1)

try:
    from app.database import Base, engine, get_db
    print("✓ Database module imported")
except Exception as e:
    print(f"✗ Database import failed: {e}")
    sys.exit(1)

try:
    from app.models import User, Subject, Study
    print("✓ Models imported")
except Exception as e:
    print(f"✗ Models import failed: {e}")
    sys.exit(1)

try:
    from app.core.security import verify_password, get_password_hash
    print("✓ Security module imported")
except Exception as e:
    print(f"✗ Security import failed: {e}")
    sys.exit(1)

try:
    from app.api.v1 import auth, subjects, studies
    print("✓ API routers imported")
except Exception as e:
    print(f"✗ API routers import failed: {e}")
    sys.exit(1)

try:
    from app.main import app
    print("✓ Main app imported")
except Exception as e:
    print(f"✗ Main app import failed: {e}")
    sys.exit(1)

# Check database connection
print("\nTesting database connection...")
try:
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✓ Database connection successful")
except Exception as e:
    print(f"⚠ Database connection failed: {e}")
    print("  This is expected if PostgreSQL is not running.")
    print("  Start PostgreSQL or run: docker-compose up -d")

# Check if tables exist
print("\nChecking database tables...")
try:
    from app.database import Base
    from app.models import User, Subject, Study
    
    # Try to query tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print(f"✓ Found {len(tables)} tables in database")
        for table in tables:
            print(f"  - {table}")
    else:
        print("⚠ No tables found. Run: python -c \"from app.database import Base, engine; Base.metadata.create_all(bind=engine)\"")
except Exception as e:
    print(f"⚠ Could not check tables: {e}")

print("\n" + "=" * 60)
print("Setup test complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Install dependencies: pip install -r requirements-dev.txt")
print("2. Start PostgreSQL (or run: docker-compose up -d)")
print("3. Create tables: python -c \"from app.database import Base, engine; Base.metadata.create_all(bind=engine)\"")
print("4. Seed data: python scripts/seed_mock_data.py")
print("5. Run server: uvicorn app.main:app --reload")



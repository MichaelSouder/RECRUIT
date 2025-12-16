#!/bin/bash
# Database initialization script for Docker
# This script initializes the database tables and optionally seeds data

set -e

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -U postgres; do
  sleep 1
done

echo "PostgreSQL is ready!"

echo "Creating database tables..."
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

echo "Running migration scripts..."
# Add assessment_time column if it doesn't exist
python scripts/add_assessment_time_to_assessments.py || echo "Migration may have already run"

echo "Database initialization complete!"

# Optionally seed data (uncomment to enable)
# echo "Seeding mock data..."
# python scripts/seed_mock_data.py


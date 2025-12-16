# Database initialization script for Docker (Windows PowerShell)
# This script initializes the database tables and optionally seeds data

Write-Host "Waiting for PostgreSQL to be ready..."
do {
    Start-Sleep -Seconds 1
    $result = docker exec recruit_postgres pg_isready -U postgres 2>&1
} while ($LASTEXITCODE -ne 0)

Write-Host "PostgreSQL is ready!"

Write-Host "Creating database tables..."
docker exec recruit_backend python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

Write-Host "Running migration scripts..."
docker exec recruit_backend python scripts/add_assessment_time_to_assessments.py

Write-Host "Database initialization complete!"

# Optionally seed data (uncomment to enable)
# Write-Host "Seeding mock data..."
# docker exec recruit_backend python scripts/seed_mock_data.py


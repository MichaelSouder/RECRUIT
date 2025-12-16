# Docker setup script for Windows PowerShell
# This script helps set up and manage the Docker environment

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

Write-Host "RECRUIT Docker Setup Script" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is installed
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue) -and 
    -not (docker compose version 2>&1)) {
    Write-Host "Error: Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

function Start-Services {
    Write-Host "Starting Docker services..." -ForegroundColor Green
    docker-compose up -d
    Write-Host "Waiting for services to be healthy..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    Write-Host "Services started!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access the application at:" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost" -ForegroundColor White
    Write-Host "  Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
}

function Stop-Services {
    Write-Host "Stopping Docker services..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "Services stopped!" -ForegroundColor Green
}

function Restart-Services {
    Stop-Services
    Start-Services
}

function Rebuild-Services {
    Write-Host "Rebuilding Docker images..." -ForegroundColor Yellow
    docker-compose build --no-cache
    Write-Host "Images rebuilt!" -ForegroundColor Green
}

function View-Logs {
    param([string]$Service = "")
    if ($Service) {
        docker-compose logs -f $Service
    } else {
        docker-compose logs -f
    }
}

function Initialize-Database {
    Write-Host "Initializing database..." -ForegroundColor Yellow
    docker exec recruit_backend python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
    Write-Host "Database initialized!" -ForegroundColor Green
}

function Seed-Data {
    Write-Host "Seeding mock data..." -ForegroundColor Yellow
    docker exec recruit_backend python scripts/seed_mock_data.py
    Write-Host "Data seeded!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now log in with:" -ForegroundColor Cyan
    Write-Host "  Admin: admin@recruit.test / admin123" -ForegroundColor White
    Write-Host "  User: user1@recruit.test / password123" -ForegroundColor White
}

function Show-Status {
    docker-compose ps
}

function Clean-Resources {
    Write-Host "Cleaning up Docker resources..." -ForegroundColor Yellow
    docker-compose down -v
    docker system prune -f
    Write-Host "Cleanup complete!" -ForegroundColor Green
}

# Main command handler
switch ($Command.ToLower()) {
    "start" {
        Start-Services
    }
    "stop" {
        Stop-Services
    }
    "restart" {
        Restart-Services
    }
    "rebuild" {
        Rebuild-Services
    }
    "logs" {
        $service = $args[0]
        View-Logs -Service $service
    }
    "init-db" {
        Initialize-Database
    }
    "seed" {
        Seed-Data
    }
    "status" {
        Show-Status
    }
    "clean" {
        Clean-Resources
    }
    default {
        Write-Host "Usage: .\docker-setup.ps1 {start|stop|restart|rebuild|logs|init-db|seed|status|clean}" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Cyan
        Write-Host "  start      - Start all services" -ForegroundColor White
        Write-Host "  stop       - Stop all services" -ForegroundColor White
        Write-Host "  restart    - Restart all services" -ForegroundColor White
        Write-Host "  rebuild    - Rebuild all images" -ForegroundColor White
        Write-Host "  logs       - View logs (optionally specify service name)" -ForegroundColor White
        Write-Host "  init-db    - Initialize database" -ForegroundColor White
        Write-Host "  seed       - Seed mock data" -ForegroundColor White
        Write-Host "  status     - Show service status" -ForegroundColor White
        Write-Host "  clean      - Remove all containers and volumes" -ForegroundColor White
    }
}


#!/bin/bash
# Docker setup script for Linux/macOS
# This script helps set up and manage the Docker environment

set -e

echo "RECRUIT Docker Setup Script"
echo "============================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to check if containers are running
check_containers() {
    if docker-compose ps | grep -q "Up"; then
        return 0
    else
        return 1
    fi
}

# Function to start services
start_services() {
    echo "Starting Docker services..."
    docker-compose up -d
    echo "Waiting for services to be healthy..."
    sleep 10
    echo "Services started!"
    echo ""
    echo "Access the application at:"
    echo "  Frontend: http://localhost"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
}

# Function to stop services
stop_services() {
    echo "Stopping Docker services..."
    docker-compose down
    echo "Services stopped!"
}

# Function to rebuild services
rebuild_services() {
    echo "Rebuilding Docker images..."
    docker-compose build --no-cache
    echo "Images rebuilt!"
}

# Function to view logs
view_logs() {
    if [ -z "$1" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$1"
    fi
}

# Function to initialize database
init_database() {
    echo "Initializing database..."
    docker exec recruit_backend python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
    echo "Database initialized!"
}

# Function to seed data
seed_data() {
    echo "Seeding mock data..."
    docker exec recruit_backend python scripts/seed_mock_data.py
    echo "Data seeded!"
    echo ""
    echo "You can now log in with:"
    echo "  Admin: admin@recruit.test / admin123"
    echo "  User: user1@recruit.test / password123"
}

# Main menu
case "${1:-}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        start_services
        ;;
    rebuild)
        rebuild_services
        ;;
    logs)
        view_logs "$2"
        ;;
    init-db)
        init_database
        ;;
    seed)
        seed_data
        ;;
    status)
        docker-compose ps
        ;;
    clean)
        echo "Cleaning up Docker resources..."
        docker-compose down -v
        docker system prune -f
        echo "Cleanup complete!"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|rebuild|logs|init-db|seed|status|clean}"
        echo ""
        echo "Commands:"
        echo "  start      - Start all services"
        echo "  stop       - Stop all services"
        echo "  restart    - Restart all services"
        echo "  rebuild    - Rebuild all images"
        echo "  logs       - View logs (optionally specify service name)"
        echo "  init-db    - Initialize database"
        echo "  seed       - Seed mock data"
        echo "  status     - Show service status"
        echo "  clean      - Remove all containers and volumes"
        exit 1
        ;;
esac


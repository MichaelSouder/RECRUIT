# Docker Setup Guide

This guide explains how to build and run the RECRUIT platform using Docker and Docker Compose. The setup is designed to work on both Linux and Windows.

## Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher
- At least 4GB of available RAM
- At least 10GB of free disk space

## Quick Start

### Start All Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- Backend API (port 8000)
- Frontend web application (port 80)

### Access the Application

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### Stop All Services

```bash
docker-compose down
```

To remove volumes (deletes all data):

```bash
docker-compose down -v
```

## Building Images

### Build All Images

```bash
docker-compose build
```

### Build Specific Service

```bash
docker-compose build backend
docker-compose build frontend
```

### Rebuild Without Cache

```bash
docker-compose build --no-cache
```

## Development Mode

For development with hot reload:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This will:
- Mount source code as volumes for live updates
- Enable hot reload for both backend and frontend
- Run frontend on port 5173 (Vite dev server)

## Service Details

### Backend Service

- **Container Name**: `recruit_backend`
- **Port**: 8000
- **Health Check**: http://localhost:8000/health
- **Database**: Automatically initializes on first startup
- **Environment Variables**: See docker-compose.yml

### Frontend Service

- **Container Name**: `recruit_frontend`
- **Port**: 80 (production) or 5173 (development)
- **Health Check**: http://localhost/health
- **Build**: Multi-stage build with Nginx for production

### PostgreSQL Service

- **Container Name**: `recruit_postgres`
- **Port**: 5432
- **Database**: `recruit_db`
- **User**: `postgres`
- **Password**: `postgres`
- **Data Persistence**: Volume `postgres_data`

### Redis Service

- **Container Name**: `recruit_redis`
- **Port**: 6379
- **Data Persistence**: In-memory (no volume)

## Environment Variables

### Backend Environment Variables

Create a `.env` file in the project root or set these in docker-compose.yml:

```env
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/recruit_db
REDIS_URL=redis://redis:6379/0
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:80
```

### Frontend Environment Variables

```env
VITE_API_URL=http://localhost:8000
```

## Database Initialization

The database is automatically initialized when the backend container starts for the first time. This includes:

1. Creating all tables
2. Running migration scripts
3. Setting up the schema

### Manual Database Initialization

If you need to manually initialize the database:

```bash
# Linux/macOS
docker exec recruit_backend python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Windows PowerShell
docker exec recruit_backend python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Seeding Mock Data

To populate the database with sample data:

```bash
docker exec recruit_backend python scripts/seed_mock_data.py
```

After seeding, you can log in with:
- Admin: `admin@recruit.test` / `admin123`
- User: `user1@recruit.test` / `password123`

## Viewing Logs

### All Services

```bash
docker-compose logs -f
```

### Specific Service

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Last 100 Lines

```bash
docker-compose logs --tail=100 backend
```

## Executing Commands in Containers

### Backend Container

```bash
# Access Python shell
docker exec -it recruit_backend python

# Run migration script
docker exec recruit_backend python scripts/add_assessment_time_to_assessments.py

# Run tests
docker exec recruit_backend pytest
```

### Frontend Container

```bash
# Access shell
docker exec -it recruit_frontend sh

# Install new package (development)
docker exec recruit_frontend npm install <package-name>
```

### Database Container

```bash
# Access PostgreSQL
docker exec -it recruit_postgres psql -U postgres -d recruit_db

# Backup database
docker exec recruit_postgres pg_dump -U postgres recruit_db > backup.sql

# Restore database
docker exec -i recruit_postgres psql -U postgres recruit_db < backup.sql
```

## Troubleshooting

### Port Already in Use

If a port is already in use, you can change it in docker-compose.yml:

```yaml
ports:
  - "8001:8000"  # Change host port from 8000 to 8001
```

### Database Connection Issues

1. Check if PostgreSQL is healthy:
```bash
docker-compose ps
```

2. Check PostgreSQL logs:
```bash
docker-compose logs postgres
```

3. Verify connection from backend:
```bash
docker exec recruit_backend pg_isready -h postgres -U postgres
```

### Build Failures

1. Clear Docker cache:
```bash
docker system prune -a
```

2. Rebuild without cache:
```bash
docker-compose build --no-cache
```

### Permission Issues (Linux)

If you encounter permission issues with volumes:

```bash
sudo chown -R $USER:$USER ./src
```

### Windows-Specific Issues

1. **Line Endings**: Ensure Git is configured to handle line endings:
```bash
git config --global core.autocrlf true
```

2. **Volume Mounts**: On Windows, use forward slashes in paths or use WSL2.

3. **Path Separators**: Docker Compose handles path differences automatically, but ensure paths use forward slashes.

### Container Won't Start

1. Check container logs:
```bash
docker-compose logs <service-name>
```

2. Check container status:
```bash
docker-compose ps
```

3. Restart specific service:
```bash
docker-compose restart <service-name>
```

### Database Not Initializing

1. Check backend logs for errors:
```bash
docker-compose logs backend
```

2. Manually run initialization:
```bash
docker exec recruit_backend python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

## Production Deployment

For production deployment:

1. **Update Environment Variables**: Set proper SECRET_KEY and database credentials
2. **Remove Volume Mounts**: Comment out volume mounts in docker-compose.yml for production
3. **Use Production Images**: Build and tag images for your registry
4. **Enable SSL**: Use a reverse proxy (nginx/traefik) with SSL certificates
5. **Set Resource Limits**: Add resource limits to docker-compose.yml

Example production docker-compose.yml additions:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Networking

All services are connected via the `recruit_network` bridge network. Services can communicate using their service names:

- Backend → PostgreSQL: `postgres:5432`
- Backend → Redis: `redis:6379`
- Frontend → Backend: `backend:8000`

## Data Persistence

- **PostgreSQL Data**: Stored in Docker volume `postgres_data`
- **Application Code**: Mounted as volumes in development, copied in production
- **Redis Data**: In-memory only (no persistence)

To backup PostgreSQL data:

```bash
docker run --rm -v recruit_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

To restore:

```bash
docker run --rm -v recruit_postgres_data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/postgres_backup.tar.gz"
```

## Health Checks

All services include health checks:

- **PostgreSQL**: Checks if database is ready to accept connections
- **Redis**: Checks if Redis is responding to ping
- **Backend**: Checks HTTP health endpoint
- **Frontend**: Checks HTTP health endpoint

View health status:

```bash
docker-compose ps
```

## Cleanup

### Remove All Containers and Networks

```bash
docker-compose down
```

### Remove Containers, Networks, and Volumes

```bash
docker-compose down -v
```

### Remove Images

```bash
docker-compose down --rmi all
```

### Complete Cleanup (Use with Caution)

```bash
docker-compose down -v --rmi all
docker system prune -a
```

## Cross-Platform Compatibility

The Docker setup is designed to work on:

- **Linux**: Full support, native performance
- **Windows**: Full support via Docker Desktop
- **macOS**: Full support via Docker Desktop

### Windows-Specific Notes

- Use WSL2 for best performance
- Ensure Docker Desktop is running
- Path separators are handled automatically by Docker Compose
- Use forward slashes in paths when possible

### Linux-Specific Notes

- Ensure Docker daemon is running: `sudo systemctl start docker`
- Add user to docker group to avoid sudo: `sudo usermod -aG docker $USER`
- Log out and back in after adding to docker group

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://react.dev/learn/start-a-new-react-project#building-for-production)


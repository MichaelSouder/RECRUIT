# RECRUIT Platform

RECRUIT is a comprehensive clinical research data management platform designed for managing subjects, studies, assessments, and session notes in clinical research environments. The platform provides a modern, secure, and scalable solution for research teams to track and manage clinical trial data with full audit trail capabilities.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Setup](#database-setup)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Docker Setup](#docker-setup)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [License](#license)

## Overview

RECRUIT is a refactored clinical research platform built with modern web technologies. The system provides secure, role-based access to clinical research data with comprehensive audit logging for regulatory compliance. The platform supports multiple studies, subjects, various assessment types, and session notes management.

### Key Capabilities

- Subject and study management with secure access controls
- Dynamic assessment type system supporting multiple assessment formats
- Assessment calendar for scheduling and viewing assessments
- Session notes tracking
- Comprehensive audit trail for FDA compliance
- Role-based access control (Admin, Researcher, Viewer)
- RESTful API with interactive documentation
- Responsive web interface

## Features

### User Management
- User registration and authentication with JWT tokens
- Role-based access control (admin, researcher, viewer)
- User profile management
- Study assignment and access control

### Subject Management
- Create, read, update, and delete subjects
- Search and filter subjects by name
- Associate subjects with multiple studies
- Track subject demographics and enrollment status
- Paginated lists for large datasets

### Study Management
- Create and manage clinical studies
- Assign researchers to studies
- Track study status, dates, and principal investigators
- Study-specific data filtering

### Assessment Management
- Dynamic assessment type system
- Support for multiple assessment types (MoCA, NIH Toolbox, DASS-21, PSSQI, Vision, Balance, etc.)
- Custom field definitions per assessment type
- Assessment calendar view
- Assessment date and time tracking
- Assessment scoring and notes
- CSV export functionality

### Session Notes
- Create and manage session notes for subjects
- Link notes to specific sessions
- Search and filter capabilities

### Audit Trail
- Comprehensive audit logging for all data changes
- FDA-compliant audit trail
- Track user actions, IP addresses, and timestamps
- View audit logs through admin interface

### Security
- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Role-based authorization
- Secure API endpoints

## Architecture

The RECRUIT platform follows a modern, API-first architecture:

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ (with SQLite fallback for development)
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT tokens
- **API Style**: RESTful with OpenAPI/Swagger documentation

### Frontend
- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Build Tool**: Vite
- **Routing**: React Router
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Database**: PostgreSQL with SQLite fallback
- **Caching**: Redis (optional)

## Prerequisites

Before installing RECRUIT, ensure you have the following installed:

### Required
- Python 3.11 or higher
- Node.js 18 or higher (or pnpm)
- PostgreSQL 15 or higher (or SQLite for development)
- Git

### Optional
- Docker and Docker Compose (for containerized development)
- Redis 7+ (for caching, optional)

### System Requirements
- Minimum 4GB RAM
- 10GB free disk space
- Operating System: Linux, macOS, or Windows

## Installation

### Clone the Repository

```bash
git clone <repository-url>
cd RECRUIT
```

### Backend Setup

1. Navigate to the backend directory:
```bash
cd src/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements-dev.txt
```

5. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration (see Configuration section)
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd src/frontend
```

2. Install dependencies:
```bash
npm install
# or
pnpm install
```

3. Create environment file (optional):
```bash
# Create .env file with:
VITE_API_URL=http://localhost:8000
```

## Configuration

### Backend Configuration

Create a `.env` file in `src/backend/` with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/recruit_db
# Or for SQLite (development):
# DATABASE_URL=sqlite:///../recruit.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Environment
ENVIRONMENT=development
```

### Frontend Configuration

Create a `.env` file in `src/frontend/` (optional):

```env
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Development Mode

#### Start Backend

1. Navigate to backend directory:
```bash
cd src/backend
```

2. Activate virtual environment (if not already active):
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

3. Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

#### Start Frontend

1. Navigate to frontend directory:
```bash
cd src/frontend
```

2. Start the development server:
```bash
npm run dev
# or
pnpm dev
```

The application will be available at `http://localhost:5173`

### Production Mode

#### Backend

```bash
cd src/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd src/frontend
npm run build
npm run preview
```

## Database Setup

### Initial Database Creation

#### Using PostgreSQL

1. Create the database:
```bash
createdb recruit_db
# or using psql:
psql -c "CREATE DATABASE recruit_db;"
```

2. Initialize tables:
```bash
cd src/backend
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

#### Using SQLite (Development)

SQLite will be used automatically if PostgreSQL is not available. The database file will be created at `src/recruit.db`.

### Database Migrations

The platform includes migration scripts for adding new columns to existing databases:

#### Add Assessment Time Column

```bash
cd src/backend
python scripts/add_assessment_time_to_assessments.py
```

#### Other Migration Scripts

- `scripts/add_ethnicity_to_subjects.py` - Add ethnicity column
- `scripts/add_location_phone_to_users.py` - Add location and phone to users
- `scripts/add_pi_to_studies.py` - Add principal investigator to studies
- `scripts/add_piv_certificate_id_to_users.py` - Add PIV certificate ID
- `scripts/create_audit_logs_table.py` - Create audit logs table

### Seeding Mock Data

To populate the database with sample data for testing:

```bash
cd src/backend
python scripts/seed_mock_data.py
```

This will create:
- Test users (admin and regular users)
- Sample studies
- Sample subjects
- Sample assessments
- Sample session notes

### Test Credentials

After seeding mock data, you can log in with:

- **Admin User**: `admin@recruit.test` / `admin123`
- **Regular User**: `user1@recruit.test` / `password123`

## API Documentation

### Interactive Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and receive JWT token
- `POST /api/v1/auth/login-piv` - Login with PIV certificate
- `GET /api/v1/auth/me` - Get current user information

#### Subjects
- `GET /api/v1/subjects` - List subjects (paginated, searchable, filterable)
- `GET /api/v1/subjects/{id}` - Get subject by ID
- `POST /api/v1/subjects` - Create new subject
- `PUT /api/v1/subjects/{id}` - Update subject
- `DELETE /api/v1/subjects/{id}` - Delete subject

#### Studies
- `GET /api/v1/studies` - List studies (paginated)
- `GET /api/v1/studies/{id}` - Get study by ID
- `POST /api/v1/studies` - Create new study
- `PUT /api/v1/studies/{id}` - Update study
- `DELETE /api/v1/studies/{id}` - Delete study
- `GET /api/v1/studies/{id}/researchers` - Get researchers for a study
- `POST /api/v1/studies/{id}/researchers` - Assign researchers to study
- `DELETE /api/v1/studies/{id}/researchers/{user_id}` - Remove researcher from study

#### Assessments
- `GET /api/v1/assessments` - List assessments (paginated, filterable)
- `GET /api/v1/assessments/{id}` - Get assessment by ID
- `POST /api/v1/assessments` - Create new assessment
- `PUT /api/v1/assessments/{id}` - Update assessment
- `DELETE /api/v1/assessments/{id}` - Delete assessment

#### Assessment Types
- `GET /api/v1/assessment-types` - List assessment types
- `GET /api/v1/assessment-types/{id}` - Get assessment type by ID
- `POST /api/v1/assessment-types` - Create new assessment type
- `PUT /api/v1/assessment-types/{id}` - Update assessment type
- `DELETE /api/v1/assessment-types/{id}` - Delete assessment type

#### Session Notes
- `GET /api/v1/session-notes` - List session notes (paginated, filterable)
- `GET /api/v1/session-notes/{id}` - Get session note by ID
- `POST /api/v1/session-notes` - Create new session note
- `PUT /api/v1/session-notes/{id}` - Update session note
- `DELETE /api/v1/session-notes/{id}` - Delete session note

#### Admin
- `GET /api/v1/admin/users` - List all users (admin only)
- `GET /api/v1/admin/users/{id}` - Get user by ID (admin only)
- `PUT /api/v1/admin/users/{id}` - Update user (admin only)
- `DELETE /api/v1/admin/users/{id}` - Delete user (admin only)
- `GET /api/v1/admin/users/{id}/studies` - Get user's studies (admin only)
- `POST /api/v1/admin/users/{id}/studies` - Assign studies to user (admin only)

#### Audit Trail
- `GET /api/v1/audit/logs` - Get audit logs (paginated, filterable)
- `GET /api/v1/audit/logs/{id}` - Get audit log by ID

### Authentication

Most endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Development

### Backend Development

#### Code Formatting

```bash
cd src/backend
black .
ruff check .
```

#### Type Checking

```bash
cd src/backend
mypy app
```

#### Running Tests

```bash
cd src/backend
pytest
```

#### Creating Database Migrations

For schema changes, create migration scripts in `src/backend/scripts/` following the pattern of existing migration scripts.

### Frontend Development

#### Code Formatting

```bash
cd src/frontend
npm run format
```

#### Linting

```bash
cd src/frontend
npm run lint
```

#### Building for Production

```bash
cd src/frontend
npm run build
```

The built files will be in the `dist/` directory.

### Development Workflow

1. Create a feature branch from main
2. Make your changes
3. Run tests and linting
4. Commit with descriptive messages
5. Push and create a pull request

## Testing

### Backend Tests

```bash
cd src/backend
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd src/frontend
npm test
```

## Project Structure

```
RECRUIT/
├── src/
│   ├── backend/                 # FastAPI backend application
│   │   ├── app/
│   │   │   ├── api/             # API routes and endpoints
│   │   │   │   └── v1/         # API version 1
│   │   │   ├── models/         # SQLAlchemy models
│   │   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── services/       # Business logic services
│   │   │   ├── middleware/     # Custom middleware
│   │   │   ├── core/           # Core utilities (security, config)
│   │   │   ├── database.py     # Database configuration
│   │   │   └── main.py         # FastAPI application
│   │   ├── scripts/            # Utility and migration scripts
│   │   ├── requirements.txt    # Production dependencies
│   │   └── requirements-dev.txt # Development dependencies
│   │
│   └── frontend/                # React frontend application
│       ├── src/
│       │   ├── api/            # API client and endpoints
│       │   ├── components/     # React components
│       │   │   ├── ui/         # Base UI components
│       │   │   └── layout/     # Layout components
│       │   ├── pages/         # Page components
│       │   ├── router/        # Routing configuration
│       │   ├── store/          # State management (Zustand)
│       │   ├── types/          # TypeScript type definitions
│       │   └── utils/          # Utility functions
│       ├── package.json
│       └── vite.config.ts
│
├── docs/                        # Additional documentation
├── plans/                       # Planning documents
├── docker-compose.yml          # Docker Compose configuration
└── README.md                   # This file
```

## Docker Setup

### Using Docker Compose

The project includes a `docker-compose.yml` file for easy development setup:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Redis on port 6379

### Environment Variables for Docker

Update the `DATABASE_URL` in your backend `.env` file to:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recruit_db
```

### Stopping Docker Services

```bash
docker-compose down
```

To remove volumes (this will delete all data):

```bash
docker-compose down -v
```

## Troubleshooting

### Backend Issues

#### Database Connection Errors

- Verify PostgreSQL is running: `pg_isready`
- Check database credentials in `.env`
- Ensure database exists: `psql -l | grep recruit_db`
- For SQLite fallback, check file permissions on `src/recruit.db`

#### Import Errors

- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements-dev.txt`
- Check Python version: `python --version` (should be 3.11+)

#### Port Already in Use

- Change the port in the uvicorn command: `uvicorn app.main:app --port 8001`
- Or stop the process using port 8000

### Frontend Issues

#### Build Errors

- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)
- Clear build cache: `rm -rf dist`

#### API Connection Errors

- Verify backend is running on `http://localhost:8000`
- Check CORS configuration in backend
- Verify `VITE_API_URL` in frontend `.env`

#### Module Not Found Errors

- Run `npm install` to ensure all dependencies are installed
- Check `package.json` for correct dependency versions

### Database Issues

#### Migration Errors

- Ensure database is up to date
- Check migration script syntax
- Verify database connection

#### Data Not Persisting

- Check database connection string
- Verify database user has write permissions
- For SQLite, check file permissions

## Documentation

### Planning Documents

Comprehensive planning documents are available in the `plans/` directory:

- `01-refactoring-plan.md` - Main refactoring plan and roadmap
- `02-architecture-design.md` - System architecture and design
- `03-technology-stack.md` - Complete technology stack specification
- `04-migration-strategy.md` - Data migration strategy and procedures
- `05-project-structure.md` - Complete project structure definition

### Additional Documentation

- `docs/FDA_AUDIT_TRAIL_PLAN.md` - FDA audit trail compliance documentation
- `src/backend/README.md` - Backend-specific documentation
- `src/frontend/README.md` - Frontend-specific documentation

## License

[Add your license information here]

## Support

For issues, questions, or contributions, please refer to the project's issue tracker or contact the development team.

---

*Last Updated: 2024*

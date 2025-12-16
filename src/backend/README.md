# RECRUIT Backend API

FastAPI backend for the RECRUIT clinical research platform.

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis (optional, for caching)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Create database:
```bash
createdb recruit_db  # or use your PostgreSQL client
```

5. Initialize database:
```bash
# Create tables
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Seed mock data
python scripts/seed_mock_data.py
```

## Running

### Development
```bash
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000`

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Test Credentials

After seeding mock data:
- **Admin**: `admin@recruit.test` / `admin123`
- **User**: `user1@recruit.test` / `password123`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user info

### Subjects
- `GET /api/v1/subjects` - List subjects (paginated, searchable)
- `GET /api/v1/subjects/{id}` - Get subject by ID
- `POST /api/v1/subjects` - Create new subject
- `PUT /api/v1/subjects/{id}` - Update subject
- `DELETE /api/v1/subjects/{id}` - Delete subject

### Studies
- `GET /api/v1/studies` - List studies (paginated)
- `GET /api/v1/studies/{id}` - Get study by ID
- `POST /api/v1/studies` - Create new study
- `PUT /api/v1/studies/{id}` - Update study
- `DELETE /api/v1/studies/{id}` - Delete study

## Development

### Code Formatting
```bash
black .
ruff check .
```

### Type Checking
```bash
mypy app
```

### Running Tests
```bash
pytest
```



# RECRUIT Platform Architecture Design

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   React App  │  │  Tailwind UI │  │  State Mgmt  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/REST API
                            │
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  FastAPI     │  │  Auth/JWT    │  │  Rate Limit  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Services    │  │  Business    │  │  Validation  │      │
│  │  Layer       │  │  Logic       │  │  Layer       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │  Redis Cache │  │  File Store  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Technology Stack
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 15+
- **Cache**: Redis
- **Task Queue**: Celery with Redis broker
- **Authentication**: JWT tokens
- **API Documentation**: OpenAPI/Swagger (auto-generated)

### Project Structure

```
src/backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection & session
│   │
│   ├── api/                    # API routes
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── subjects.py     # Subject endpoints
│   │   │   ├── studies.py      # Study endpoints
│   │   │   ├── assessments/    # Assessment endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── cognitive.py
│   │   │   │   ├── psychological.py
│   │   │   │   └── ...
│   │   │   ├── sessions.py      # Session notes
│   │   │   └── admin.py        # Admin endpoints
│   │   └── dependencies.py     # Shared dependencies
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── subject.py
│   │   ├── study.py
│   │   ├── assessments/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── cognitive.py
│   │   │   ├── psychological.py
│   │   │   └── ...
│   │   └── session.py
│   │
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── subject.py
│   │   ├── study.py
│   │   └── assessments/
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── subject_service.py
│   │   ├── study_service.py
│   │   ├── assessment_service.py
│   │   └── session_service.py
│   │
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── subject_repository.py
│   │   ├── study_repository.py
│   │   └── assessment_repository.py
│   │
│   ├── core/                    # Core functionality
│   │   ├── security.py          # JWT, password hashing
│   │   ├── permissions.py       # Role-based access control
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── middleware.py        # Request middleware
│   │
│   ├── utils/                   # Utility functions
│   │   ├── validators.py
│   │   ├── scoring.py           # Assessment scoring algorithms
│   │   └── helpers.py
│   │
│   └── migrations/              # Alembic migrations
│       └── versions/
│
├── tests/                       # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── scripts/                     # Utility scripts
│   ├── migrate_data.py
│   └── seed_data.py
│
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── README.md
```

### Key Design Patterns

#### 1. Repository Pattern
- Abstracts data access logic
- Enables easy testing and database swapping
- Centralizes query logic

#### 2. Service Layer Pattern
- Contains business logic
- Coordinates between repositories
- Handles transactions

#### 3. Dependency Injection
- FastAPI's built-in DI system
- Improves testability
- Reduces coupling

#### 4. Schema Validation
- Pydantic models for request/response validation
- Automatic API documentation
- Type safety

## Frontend Architecture

### Technology Stack
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand or Redux Toolkit
- **Routing**: React Router v6
- **Forms**: React Hook Form
- **HTTP Client**: Axios
- **UI Components**: Headless UI or Radix UI
- **Charts**: Recharts or Chart.js

### Project Structure

```
src/frontend/
├── public/
│   └── ...
│
├── src/
│   ├── main.tsx                 # Application entry
│   ├── App.tsx                  # Root component
│   ├── index.css                # Global styles (Tailwind)
│   │
│   ├── api/                     # API client
│   │   ├── client.ts            # Axios instance
│   │   ├── endpoints.ts         # API endpoint definitions
│   │   └── types.ts             # API response types
│   │
│   ├── components/              # Reusable components
│   │   ├── ui/                  # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Table.tsx
│   │   │   └── ...
│   │   ├── forms/               # Form components
│   │   │   ├── SubjectForm.tsx
│   │   │   ├── AssessmentForm.tsx
│   │   │   └── ...
│   │   └── layout/              # Layout components
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Footer.tsx
│   │
│   ├── features/                # Feature-based modules
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── services/
│   │   ├── subjects/
│   │   │   ├── components/
│   │   │   │   ├── SubjectList.tsx
│   │   │   │   ├── SubjectForm.tsx
│   │   │   │   └── SubjectDetail.tsx
│   │   │   ├── hooks/
│   │   │   └── services/
│   │   ├── studies/
│   │   ├── assessments/
│   │   └── sessions/
│   │
│   ├── pages/                   # Page components
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Subjects.tsx
│   │   ├── Studies.tsx
│   │   └── ...
│   │
│   ├── hooks/                   # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useSubjects.ts
│   │   └── ...
│   │
│   ├── store/                   # State management
│   │   ├── authStore.ts
│   │   ├── subjectStore.ts
│   │   └── ...
│   │
│   ├── utils/                   # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   ├── types/                   # TypeScript types
│   │   ├── subject.ts
│   │   ├── study.ts
│   │   └── ...
│   │
│   └── router/                  # Routing configuration
│       └── index.tsx
│
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
├── package.json
└── README.md
```

### Component Architecture Principles

1. **Feature-Based Organization**: Group related components by feature
2. **Component Composition**: Build complex UIs from simple components
3. **Separation of Concerns**: UI, logic, and data fetching separated
4. **Reusability**: Shared components in `components/ui/`
5. **Type Safety**: Full TypeScript coverage

## Database Design

### Core Tables

#### Users & Authentication
- `users` - User accounts
- `roles` - Role definitions
- `user_roles` - User-role assignments
- `sessions` - Active user sessions

#### Core Entities
- `subjects` - Research participants
- `studies` - Research studies
- `subject_studies` - Many-to-many relationship

#### Assessments
- `assessments` - Base assessment table (polymorphic)
- `assessment_types` - Assessment type definitions
- Individual assessment tables (e.g., `nihcog_assessments`, `moca_assessments`)

#### Supporting
- `session_notes` - Clinical session documentation
- `audit_logs` - Audit trail
- `staff_trainings` - Training records
- `medical_reviews` - Medical review records

### Database Principles

1. **Normalization**: Proper 3NF normalization
2. **Indexing**: Strategic indexes on foreign keys and search fields
3. **Constraints**: Foreign keys, check constraints, unique constraints
4. **Soft Deletes**: `deleted_at` timestamp for important records
5. **Audit Fields**: `created_at`, `updated_at`, `created_by`, `updated_by`

## Security Architecture

### Authentication
- JWT-based authentication
- Refresh token rotation
- Password hashing with bcrypt
- Session management

### Authorization
- Role-Based Access Control (RBAC)
- Permission-based fine-grained access
- Resource-level permissions

### Data Security
- HTTPS/TLS encryption
- SQL injection prevention (ORM)
- XSS protection
- CSRF tokens
- Input validation and sanitization
- PII encryption for sensitive fields (SSN, etc.)

## API Design

### RESTful Principles
- Resource-based URLs
- HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Proper status codes
- Consistent response format

### API Versioning
- URL-based versioning: `/api/v1/...`
- Backward compatibility strategy

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "meta": {
    "pagination": { ... },
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Error Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": { ... }
  }
}
```

## Deployment Architecture

### Development
- Local development with Docker Compose
- Hot reload for both frontend and backend

### Staging
- Containerized deployment
- Automated testing
- Preview deployments

### Production
- Container orchestration (Docker/Kubernetes)
- Load balancing
- Database replication
- CDN for static assets
- Monitoring and logging

## Scalability Considerations

1. **Horizontal Scaling**: Stateless API design
2. **Caching Strategy**: Redis for frequently accessed data
3. **Database Optimization**: Query optimization, connection pooling
4. **CDN**: Static asset delivery
5. **Async Processing**: Celery for background tasks
6. **Database Sharding**: Future consideration for large datasets

---

*Document Version: 1.0*  
*Last Updated: [Current Date]*



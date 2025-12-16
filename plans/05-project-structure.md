# RECRUIT Platform Project Structure

## Overview

This document defines the complete project structure for the refactored RECRUIT platform, including both backend and frontend applications.

## Root Directory Structure

```
RECRUIT/
├── src/                          # New application source code
│   ├── backend/                  # Python FastAPI backend
│   └── frontend/                 # React TypeScript frontend
│
├── old/                          # Original Rails application (preserved)
│
├── plans/                        # Planning and documentation
│   ├── 01-refactoring-plan.md
│   ├── 02-architecture-design.md
│   ├── 03-technology-stack.md
│   ├── 04-migration-strategy.md
│   └── 05-project-structure.md
│
├── scripts/                      # Utility scripts
│   ├── migration/                # Data migration scripts
│   ├── deployment/               # Deployment scripts
│   └── setup/                    # Setup scripts
│
├── docs/                         # Additional documentation
│   ├── api/                      # API documentation
│   ├── deployment/               # Deployment guides
│   └── user-guides/              # User documentation
│
├── docker/                       # Docker configuration files
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── .github/                      # GitHub workflows
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── .gitignore
├── README.md
└── LICENSE
```

## Backend Structure (src/backend/)

```
src/backend/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration management
│   ├── database.py                # Database connection & session management
│   │
│   ├── api/                       # API routes
│   │   ├── __init__.py
│   │   ├── dependencies.py        # Shared dependencies (auth, db session)
│   │   │
│   │   └── v1/                    # API version 1
│   │       ├── __init__.py
│   │       ├── auth.py            # Authentication endpoints
│   │       ├── users.py           # User management
│   │       ├── subjects.py        # Subject endpoints
│   │       ├── studies.py         # Study endpoints
│   │       │
│   │       ├── assessments/       # Assessment endpoints
│   │       │   ├── __init__.py
│   │       │   ├── cognitive.py   # Cognitive assessments
│   │       │   │   ├── nihcog.py
│   │       │   │   ├── moca.py
│   │       │   │   └── ...
│   │       │   ├── psychological.py
│   │       │   │   ├── dass21.py
│   │       │   │   ├── bai.py
│   │       │   │   └── ...
│   │       │   ├── sleep.py
│   │       │   │   └── pssqi.py
│   │       │   └── vision.py
│   │       │
│   │       ├── sessions.py        # Session notes
│   │       ├── admin.py           # Admin endpoints
│   │       └── reports.py         # Reporting endpoints
│   │
│   ├── models/                    # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py                # Base model class
│   │   ├── user.py                # User model
│   │   ├── role.py                # Role model
│   │   ├── subject.py             # Subject model
│   │   ├── study.py               # Study model
│   │   │
│   │   ├── assessments/           # Assessment models
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # Base assessment model
│   │   │   ├── cognitive.py
│   │   │   │   ├── nihcog.py
│   │   │   │   ├── moca.py
│   │   │   │   └── ...
│   │   │   ├── psychological.py
│   │   │   ├── sleep.py
│   │   │   └── vision.py
│   │   │
│   │   ├── session.py             # Session note model
│   │   ├── audit.py               # Audit log model
│   │   └── training.py            # Staff training model
│   │
│   ├── schemas/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py                # User schemas
│   │   ├── subject.py             # Subject schemas
│   │   ├── study.py               # Study schemas
│   │   │
│   │   ├── assessments/           # Assessment schemas
│   │   │   ├── __init__.py
│   │   │   └── ...                # Assessment-specific schemas
│   │   │
│   │   ├── session.py
│   │   └── common.py              # Common schemas (pagination, etc.)
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Authentication logic
│   │   ├── user_service.py        # User management logic
│   │   ├── subject_service.py     # Subject business logic
│   │   ├── study_service.py       # Study business logic
│   │   ├── assessment_service.py  # Assessment business logic
│   │   ├── session_service.py     # Session note logic
│   │   └── scoring_service.py     # Assessment scoring algorithms
│   │
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py                # Base repository class
│   │   ├── user_repository.py
│   │   ├── subject_repository.py
│   │   ├── study_repository.py
│   │   ├── assessment_repository.py
│   │   └── session_repository.py
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py            # JWT, password hashing
│   │   ├── permissions.py         # RBAC, permissions
│   │   ├── exceptions.py          # Custom exceptions
│   │   ├── middleware.py          # Request middleware
│   │   └── constants.py           # Application constants
│   │
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   ├── validators.py          # Custom validators
│   │   ├── formatters.py          # Data formatters
│   │   ├── encryption.py          # Encryption utilities (for PII)
│   │   └── helpers.py             # General helpers
│   │
│   └── migrations/                # Alembic migrations
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
│           └── ...                # Migration files
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   │
│   ├── unit/                      # Unit tests
│   │   ├── services/
│   │   ├── repositories/
│   │   └── utils/
│   │
│   ├── integration/               # Integration tests
│   │   ├── api/
│   │   └── database/
│   │
│   └── e2e/                       # End-to-end tests
│       └── workflows/
│
├── scripts/                       # Backend-specific scripts
│   ├── migrate_data.py            # Data migration script
│   ├── seed_data.py               # Database seeding
│   └── export_data.py             # Data export utilities
│
├── alembic.ini                    # Alembic configuration
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                 # Project configuration
├── .env.example                   # Environment variables template
├── .gitignore
└── README.md
```

## Frontend Structure (src/frontend/)

```
src/frontend/
├── public/
│   ├── favicon.ico
│   ├── logo.svg
│   └── robots.txt
│
├── src/
│   ├── main.tsx                   # Application entry point
│   ├── App.tsx                    # Root component
│   ├── index.css                  # Global styles (includes Tailwind)
│   │
│   ├── api/                       # API client
│   │   ├── client.ts              # Axios instance configuration
│   │   ├── endpoints.ts           # API endpoint definitions
│   │   ├── interceptors.ts        # Request/response interceptors
│   │   └── types.ts               # API response types
│   │
│   ├── components/                # Reusable components
│   │   ├── ui/                    # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Spinner.tsx
│   │   │   ├── Alert.tsx
│   │   │   └── index.ts           # Barrel exports
│   │   │
│   │   ├── forms/                 # Form components
│   │   │   ├── FormField.tsx
│   │   │   ├── FormError.tsx
│   │   │   ├── DatePicker.tsx
│   │   │   └── ...
│   │   │
│   │   ├── layout/                # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Layout.tsx
│   │   │   └── Navigation.tsx
│   │   │
│   │   └── charts/                # Chart components
│   │       ├── LineChart.tsx
│   │       ├── BarChart.tsx
│   │       └── ...
│   │
│   ├── features/                  # Feature-based modules
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useAuth.ts
│   │   │   ├── services/
│   │   │   │   └── authService.ts
│   │   │   └── types.ts
│   │   │
│   │   ├── subjects/
│   │   │   ├── components/
│   │   │   │   ├── SubjectList.tsx
│   │   │   │   ├── SubjectForm.tsx
│   │   │   │   ├── SubjectDetail.tsx
│   │   │   │   ├── SubjectFilters.tsx
│   │   │   │   └── SubjectTable.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useSubjects.ts
│   │   │   │   └── useSubject.ts
│   │   │   ├── services/
│   │   │   │   └── subjectService.ts
│   │   │   └── types.ts
│   │   │
│   │   ├── studies/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   └── types.ts
│   │   │
│   │   ├── assessments/
│   │   │   ├── components/
│   │   │   │   ├── AssessmentList.tsx
│   │   │   │   ├── AssessmentForm.tsx
│   │   │   │   ├── AssessmentDetail.tsx
│   │   │   │   └── AssessmentScoring.tsx
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── cognitive/         # Cognitive assessment components
│   │   │   ├── psychological/      # Psychological assessment components
│   │   │   └── types.ts
│   │   │
│   │   └── sessions/
│   │       ├── components/
│   │       ├── hooks/
│   │       ├── services/
│   │       └── types.ts
│   │
│   ├── pages/                     # Page components
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Subjects/
│   │   │   ├── index.tsx          # Subjects list page
│   │   │   ├── [id].tsx           # Subject detail page
│   │   │   └── new.tsx            # New subject page
│   │   ├── Studies/
│   │   │   └── ...
│   │   ├── Assessments/
│   │   │   └── ...
│   │   └── Settings.tsx
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useApi.ts              # Generic API hook
│   │   ├── useDebounce.ts
│   │   ├── useLocalStorage.ts
│   │   └── ...
│   │
│   ├── store/                     # State management (Zustand)
│   │   ├── authStore.ts
│   │   ├── subjectStore.ts
│   │   ├── studyStore.ts
│   │   └── index.ts
│   │
│   ├── utils/                     # Utility functions
│   │   ├── formatters.ts          # Date, number formatters
│   │   ├── validators.ts          # Form validators
│   │   ├── constants.ts           # Application constants
│   │   └── helpers.ts             # General helpers
│   │
│   ├── types/                     # TypeScript type definitions
│   │   ├── subject.ts
│   │   ├── study.ts
│   │   ├── assessment.ts
│   │   ├── user.ts
│   │   └── api.ts
│   │
│   ├── router/                    # Routing configuration
│   │   ├── index.tsx              # Router setup
│   │   ├── routes.tsx             # Route definitions
│   │   └── guards.tsx             # Route guards
│   │
│   └── styles/                    # Additional styles
│       ├── tailwind.css           # Tailwind imports
│       └── custom.css             # Custom styles
│
├── tests/                         # Test files
│   ├── setup.ts
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── tailwind.config.js             # Tailwind configuration
├── postcss.config.js              # PostCSS configuration
├── tsconfig.json                  # TypeScript configuration
├── vite.config.ts                 # Vite configuration
├── vitest.config.ts               # Vitest configuration
├── .eslintrc.js                   # ESLint configuration
├── .prettierrc                    # Prettier configuration
├── package.json
├── .env.example
├── .gitignore
└── README.md
```

## Docker Structure

```
docker/
├── Dockerfile.backend             # Backend Dockerfile
├── Dockerfile.frontend            # Frontend Dockerfile
├── docker-compose.yml             # Development docker-compose
├── docker-compose.prod.yml        # Production docker-compose
└── nginx/
    └── nginx.conf                 # Nginx configuration
```

## Scripts Structure

```
scripts/
├── migration/
│   ├── export_rails_data.py      # Export from Rails DB
│   ├── import_to_new_db.py        # Import to new DB
│   ├── validate_migration.py     # Validate migration
│   └── transform_data.py          # Data transformation
│
├── deployment/
│   ├── deploy.sh                  # Deployment script
│   ├── rollback.sh                # Rollback script
│   └── health_check.sh            # Health check script
│
└── setup/
    ├── setup_dev.sh               # Development setup
    ├── setup_db.sh                # Database setup
    └── generate_secrets.sh        # Secret generation
```

## Documentation Structure

```
docs/
├── api/
│   ├── openapi.yaml               # OpenAPI specification
│   └── endpoints.md               # API endpoint documentation
│
├── deployment/
│   ├── development.md             # Development setup guide
│   ├── production.md              # Production deployment guide
│   └── docker.md                  # Docker usage guide
│
├── user-guides/
│   ├── getting-started.md
│   ├── subjects.md
│   ├── assessments.md
│   └── reports.md
│
└── architecture/
    └── diagrams/                  # Architecture diagrams
```

## Key Files and Their Purposes

### Backend Key Files

- `app/main.py`: FastAPI application initialization, middleware setup, route registration
- `app/config.py`: Environment-based configuration management
- `app/database.py`: Database connection, session management
- `app/core/security.py`: JWT token handling, password hashing
- `app/core/permissions.py`: Role-based access control

### Frontend Key Files

- `src/main.tsx`: React application entry, providers setup
- `src/App.tsx`: Root component, routing setup
- `src/api/client.ts`: Axios instance with interceptors
- `src/router/index.tsx`: React Router configuration
- `tailwind.config.js`: Tailwind CSS customization

## Naming Conventions

### Python (Backend)
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`

### TypeScript/React (Frontend)
- **Files**: `PascalCase.tsx` (components), `camelCase.ts` (utilities)
- **Components**: `PascalCase`
- **Functions/Variables**: `camelCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Types/Interfaces**: `PascalCase`

### Database
- **Tables**: `snake_case`, plural (e.g., `subjects`, `session_notes`)
- **Columns**: `snake_case`
- **Indexes**: `idx_<table>_<column>`

## File Organization Principles

1. **Feature-Based**: Group related code by feature/domain
2. **Separation of Concerns**: Clear separation between layers (API, Service, Repository)
3. **Reusability**: Shared components and utilities in common locations
4. **Scalability**: Structure supports growth and new features
5. **Testability**: Tests mirror source structure

## Getting Started

### Initial Setup

1. **Backend Setup**:
   ```bash
   cd src/backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements-dev.txt
   cp .env.example .env
   # Edit .env with your configuration
   alembic upgrade head
   ```

2. **Frontend Setup**:
   ```bash
   cd src/frontend
   npm install  # or pnpm install
   cp .env.example .env
   # Edit .env with your configuration
   npm run dev
   ```

3. **Docker Setup**:
   ```bash
   docker-compose up -d
   ```

---

*Document Version: 1.0*  
*Last Updated: [Current Date]*



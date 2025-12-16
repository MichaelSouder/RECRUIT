# RECRUIT Platform - Action Plan

Based on the comprehensive project review, this document outlines the immediate action items to improve code quality, security, and production readiness.

## Quick Wins (Can be done immediately)

### 1. Create Root .gitignore
**Status**: Completed  
**File**: `.gitignore` created at project root

### 2. Remove Build Artifacts from Repository
**Action Required**:
```bash
# Remove __pycache__ directories
find src/backend -type d -name __pycache__ -exec git rm -r --cached {} \;

# Remove venv if tracked
git rm -r --cached src/backend/venv/

# Remove database file
git rm --cached src/recruit.db

# Commit changes
git commit -m "Remove build artifacts and database file from repository"
```

### 3. Fix Default Secret Key
**File**: `src/backend/app/config.py`
**Change Required**:
```python
# Before
secret_key: str = "your-secret-key-here-change-in-production"

# After
secret_key: str  # Required, no default
```
**Additional**: Add validation to ensure SECRET_KEY is set and meets minimum requirements.

### 4. Remove Console.log Statements
**Files to Update**:
- `src/frontend/src/pages/StudyDetail.tsx` (lines 22, 38)
- `src/frontend/src/pages/Assessments.tsx` (lines 187, 253, 262, 330)
- Any other files with console.log

**Action**: Search and replace with proper logging or remove entirely.

### 5. Replace alert() with Proper Error Handling
**Files to Update**:
- `src/frontend/src/pages/AssessmentForm.tsx`
- `src/frontend/src/pages/Subjects.tsx`
- `src/frontend/src/pages/SessionNotes.tsx`
- `src/frontend/src/pages/Admin.tsx`
- Other files using `alert()`

**Recommendation**: Create a toast notification system or error modal component.

## High Priority Items (Next 1-2 Weeks)

### Week 1: Security and Code Quality

#### Day 1-2: Security Hardening
- [ ] Remove default secret key, require environment variable
- [ ] Add rate limiting to authentication endpoints
- [ ] Review and restrict CORS configuration
- [ ] Remove hardcoded passwords from seed data
- [ ] Add password policy validation

#### Day 3-4: Code Quality
- [ ] Remove all `any` types, create proper interfaces
- [ ] Remove console.log statements
- [ ] Replace alert() calls
- [ ] Add proper error handling utilities
- [ ] Standardize error messages

#### Day 5: Testing Setup
- [ ] Set up pytest for backend
- [ ] Set up React Testing Library for frontend
- [ ] Create test configuration files
- [ ] Write first set of unit tests (critical paths)

### Week 2: Testing and CI/CD

#### Day 1-3: Test Coverage
- [ ] Write tests for authentication endpoints
- [ ] Write tests for CRUD operations
- [ ] Write tests for critical frontend components
- [ ] Achieve 50%+ code coverage

#### Day 4-5: CI/CD Setup
- [ ] Create GitHub Actions workflow
- [ ] Add automated testing
- [ ] Add security scanning
- [ ] Add code quality checks (linting, type checking)

## Medium Priority Items (Next Month)

### Type Safety Improvements
1. Create proper TypeScript interfaces for all API calls
2. Replace all `any` types with specific types
3. Enable stricter TypeScript settings
4. Add runtime type validation where needed

### Error Handling
1. Create centralized error handling utility
2. Implement toast notification system
3. Add error boundaries at route level
4. Set up error logging service (e.g., Sentry)

### Documentation
1. Create CONTRIBUTING.md
2. Create SECURITY.md
3. Enhance API documentation
4. Add architecture diagrams

### Performance
1. Review database queries for optimization
2. Implement caching strategy
3. Add bundle size analysis
4. Optimize frontend bundle

## Implementation Guide

### Step 1: Security Fixes (Day 1)

#### Fix Secret Key
```python
# src/backend/app/config.py
class Settings(BaseSettings):
    secret_key: str  # Required, no default
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if not v or v == "your-secret-key-here-change-in-production":
            raise ValueError("SECRET_KEY must be set and cannot use default value")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
```

#### Add Rate Limiting
```python
# Install: pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/login")
@limiter.limit("5/minute")
def login(...):
    ...
```

### Step 2: Remove Console.log (Day 2)

Create a logging utility:
```typescript
// src/frontend/src/utils/logger.ts
const isDevelopment = import.meta.env.DEV;

export const logger = {
  debug: (...args: any[]) => {
    if (isDevelopment) console.debug(...args);
  },
  info: (...args: any[]) => {
    if (isDevelopment) console.info(...args);
  },
  warn: (...args: any[]) => {
    console.warn(...args);
  },
  error: (...args: any[]) => {
    console.error(...args);
    // Send to error tracking service
  },
};
```

Replace all `console.log` with `logger.debug()` or remove.

### Step 3: Replace alert() (Day 3)

Create toast notification component:
```typescript
// src/frontend/src/components/ui/Toast.tsx
// Use a library like react-hot-toast or create custom component
```

Replace all `alert()` calls with toast notifications.

### Step 4: Improve Type Safety (Week 1)

Create proper API types:
```typescript
// src/frontend/src/types/api.ts
export interface CreateSubjectRequest {
  first_name: string;
  last_name: string;
  // ... other fields
}

export interface UpdateSubjectRequest extends Partial<CreateSubjectRequest> {
  id: number;
}
```

Update endpoints:
```typescript
// src/frontend/src/api/endpoints.ts
create: (data: CreateSubjectRequest) => 
  apiClient.post('/api/v1/subjects', data),
```

### Step 5: Add Tests (Week 2)

Backend test example:
```python
# src/backend/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

Frontend test example:
```typescript
// src/frontend/src/pages/__tests__/Login.test.tsx
import { render, screen } from '@testing-library/react';
import { Login } from '../Login';

test('renders login form', () => {
  render(<Login />);
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
});
```

## Success Metrics

### Week 1 Goals
- [ ] Zero security vulnerabilities in critical paths
- [ ] Zero `any` types in new code
- [ ] Zero `console.log` in production code
- [ ] Zero `alert()` calls
- [ ] 100% of critical endpoints have tests

### Week 2 Goals
- [ ] 50%+ code coverage
- [ ] CI/CD pipeline running
- [ ] All security scans passing
- [ ] Type safety score > 90%

### Month 1 Goals
- [ ] 80%+ code coverage
- [ ] All critical issues resolved
- [ ] Documentation complete
- [ ] Performance benchmarks met

## Resources Needed

### Tools
- Testing frameworks (pytest, React Testing Library)
- CI/CD platform (GitHub Actions recommended)
- Error tracking (Sentry recommended)
- Security scanning (Snyk, Dependabot)
- Code quality (SonarQube, CodeClimate)

### Time Estimates
- Security fixes: 2-3 days
- Code quality improvements: 3-4 days
- Test setup and initial tests: 5-7 days
- CI/CD setup: 2-3 days
- Documentation: 2-3 days
- **Total**: ~3-4 weeks for high priority items

## Tracking Progress

Use this checklist to track completion:

### Critical (Week 1)
- [ ] Root .gitignore created
- [ ] Build artifacts removed from repo
- [ ] Secret key fixed
- [ ] Rate limiting added
- [ ] Console.log removed
- [ ] alert() replaced
- [ ] Type safety improved (50% reduction in `any`)

### High Priority (Week 2)
- [ ] Test suite setup
- [ ] 50%+ test coverage
- [ ] CI/CD pipeline
- [ ] Security scanning automated
- [ ] Error handling standardized

### Medium Priority (Month 1)
- [ ] 80%+ test coverage
- [ ] All `any` types removed
- [ ] Documentation complete
- [ ] Performance optimized
- [ ] Monitoring setup

---

**Last Updated**: December 2024  
**Next Review**: After Week 1 completion


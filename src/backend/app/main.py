import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.api.v1 import auth, subjects, studies, session_notes, assessments, assessment_types, admin, audit
from app.core.rate_limit import limiter
from app.middleware.audit_middleware import AuditMiddleware
from app.config import settings
from app.startup_seed import seed_initial_admin_if_configured

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    seed_initial_admin_if_configured()
    yield


# Interactive docs expose the full schema (endpoint names, model fields — including
# things like Subject.ssn) and aren't needed once a deployment calls itself production.
_docs_enabled = settings.environment != "production"

app = FastAPI(
    title="RECRUIT Platform API",
    description="Clinical research data management platform",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.debug,
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Log unhandled exceptions with request context before returning a generic 500 —
    previously these surfaced as a bare Starlette 500 with nothing recorded server-side."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# Rate limiting (per-IP, see app/core/rate_limit.py) — applied to /auth/login and
# /auth/login-piv to bound credential-guessing attempts.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit middleware (must be after CORS to access request headers)
app.add_middleware(AuditMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(subjects.router, prefix="/api/v1/subjects", tags=["Subjects"])
app.include_router(studies.router, prefix="/api/v1/studies", tags=["Studies"])
app.include_router(session_notes.router, prefix="/api/v1/session-notes", tags=["Session Notes"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["Assessments"])
app.include_router(assessment_types.router, prefix="/api/v1/assessment-types", tags=["Assessment Types"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit Trail"])


@app.get("/")
def root():
    return {
        "message": "RECRUIT Platform API",
        "version": "1.0.0",
        "docs": "/docs" if _docs_enabled else None,
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


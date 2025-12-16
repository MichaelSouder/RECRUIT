from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, subjects, studies, session_notes, assessments, assessment_types, admin, audit
from app.middleware.audit_middleware import AuditMiddleware
from app.config import settings

app = FastAPI(
    title="RECRUIT Platform API",
    description="Clinical research data management platform",
    version="1.0.0"
)

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
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


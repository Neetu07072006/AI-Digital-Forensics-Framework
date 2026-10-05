import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, test_database, Base

from app import models
from app import evidence_models
from app import custody_models
from app import artifact_models
from app import timeline_models
from app import analysis_models
from app import ai_models
from app import report_models
from app import auth_models
from app import audit_models

from app.routes import router
from app.evidence_routes import router as evidence_router
from app.artifact_routes import router as artifact_router
from app.timeline_routes import router as timeline_router
from app.analysis_routes import router as analysis_router
from app.ai_routes import router as ai_router
from app.report_routes import router as report_router
from app.auth_routes import router as auth_router
from app.audit_routes import router as audit_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Digital Forensics Framework",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS"
    ],
    allow_headers=[
        "Authorization",
        "Content-Type"
    ]
)

app.include_router(router)
app.include_router(evidence_router)
app.include_router(artifact_router)
app.include_router(timeline_router)
app.include_router(analysis_router)
app.include_router(ai_router)
app.include_router(report_router)
app.include_router(auth_router)
app.include_router(audit_router)

@app.get("/")
def root():
    return {
        "message": "AI Digital Forensics Framework API",
        "status": "running"
    }

@app.get("/api/health")
def health():
    return {
        "backend": "online",
        "database": test_database()
    }
"""
Main FastAPI application — Resume Updater & ATS Optimizer.

Startup sequence:
  1. Initialize database (create tables via SQLAlchemy)
  2. Create upload/export directories if they don't exist
  3. Mount all API routers under /api/v1

CORS is configured to allow the Next.js frontend (localhost:3000).
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from config import settings
from database import init_db
from api.routes import upload, ats, job_description, optimization, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown lifecycle events."""
    # --- Startup ---
    logger.info("Starting Resume Updater API...")

    # Ensure storage directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.EXPORT_DIR, exist_ok=True)

    # Initialize database tables
    await init_db()
    logger.info(f"Database ready at: {settings.DATABASE_URL}")
    logger.info("Resume Updater API is ready.")

    yield

    # --- Shutdown ---
    logger.info("Shutting down Resume Updater API.")


app = FastAPI(
    title="Resume Updater & ATS Optimizer",
    description="AI-powered resume tailoring and ATS optimization API.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ROUTERS ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(upload.router, prefix=API_PREFIX)
app.include_router(ats.router, prefix=API_PREFIX)
app.include_router(job_description.router, prefix=API_PREFIX)
app.include_router(optimization.router, prefix=API_PREFIX)
app.include_router(export.router, prefix=API_PREFIX)


# ── HEALTH CHECK ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe endpoint. Returns 200 when the API is ready."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/", tags=["Health"])
async def root():
    """Root redirect to API docs."""
    return {"message": "Resume Updater API", "docs": "/docs", "health": "/health"}


# ── GLOBAL ERROR HANDLER ──────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected errors."""
    logger.error(f"Unhandled error on {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again."},
    )

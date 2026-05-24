"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import prep, kb
from app.utils.logger import logger
from app.utils.config import config

app = FastAPI(
    title="Adaptive MCQ Preparation System",
    description="Generate adaptive MCQs from SLATEFALL dossier",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prep.router)
app.include_router(kb.router)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting Adaptive MCQ Preparation System")
    config.ensure_directories()
    logger.info(f"Using LLM provider: {config.LLM_PROVIDER}")
    logger.info(f"Database path: {config.DATABASE_PATH}")
    logger.info(f"PDF path: {config.PDF_PATH}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down Adaptive MCQ Preparation System")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Adaptive MCQ Preparation System",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

"""FastAPI main application entry point."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uuid
import time

from app.config import settings
from app.routes import analyze, forecast, trips

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Environment: {settings.environment}")
    
    # TODO: Initialize any async resources here (e.g., httpx client pool)
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")
    # TODO: Cleanup resources here


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Air quality and outdoor safety analysis API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request for tracing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log request
    start_time = time.time()
    logger.info(f"Request {request_id}: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response
    duration = time.time() - start_time
    logger.info(
        f"Request {request_id}: {response.status_code} "
        f"({duration:.3f}s)"
    )
    
    response.headers["X-Request-ID"] = request_id
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions globally."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Request {request_id}: Unhandled exception: {exc}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "request_id": request_id
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version,
        "environment": settings.environment
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.version,
        "docs": "/docs" if settings.debug else "disabled"
    }


# Include routers
# Note: analyze.router already has prefix="/api" defined, so don't add it again
app.include_router(analyze.router)

app.include_router(
    forecast.router,
    prefix=settings.api_prefix,
    tags=["Forecast"]
)

app.include_router(
    trips.router,
    prefix=settings.api_prefix,
    tags=["Trips"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

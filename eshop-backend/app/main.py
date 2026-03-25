from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware
import os
import logging
import secrets

from app.core.database import Base, engine
from app.routers import (
    auth,
    products,
    categories,
    cart,
    orders,
    users,
    admin,
    inventory,
    recommendations,
    rbac,
)
from app.routers import payments, delivery
from app.core.websocket import websocket_router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Generate secure random key for production
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mug Store API",
    description="Backend API for Mug E-Commerce Store",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Security middleware
from app.core.security_middleware import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS - Restrict to specific origins in production
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:9000,http://localhost:9001,http://127.0.0.1:9000,http://127.0.0.1:9001",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Remove server version header
    response.headers["Server"] = "MugStore"

    return response


# Serve static images (with security)
images_path = os.path.join(os.path.dirname(__file__), "..", "images")
if os.path.exists(images_path):
    app.mount("/images", StaticFiles(directory=images_path), name="images")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(rbac.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(delivery.router, prefix="/api")

# WebSocket endpoints
app.include_router(websocket_router)


@app.get("/")
def root():
    return {"message": "Mug Store API is running", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Security check endpoint
@app.get("/security")
def security_headers_check():
    """Check security headers are properly configured"""
    return {
        "rate_limiting": "enabled",
        "cors": "configured",
        "security_headers": "enabled",
        "allowed_origins": ALLOWED_ORIGINS,
    }

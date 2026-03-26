from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware
import os
import logging
import secrets

from app.core.data.database import Base, engine
from app.core.utils.metrics import setup_metrics
from app.routers.auth import auth
from app.routers.ecomm import products
from app.routers.ecomm import categories
from app.routers.ecomm import cart
from app.routers.ecomm import orders
from app.routers.auth import users
from app.routers.admin import admin
from app.routers.inventory import inventory
from app.routers.ecomm import recommendations
from app.routers.admin import rbac
from app.routers.inventory import forecasting
from app.routers.system import seed
from app.routers.inventory import inventory_ml
from app.routers.commerce import payments
from app.routers.commerce import delivery
from app.core.utils.websocket import websocket_router

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

setup_metrics(app)

# Security middleware
from app.core.security.security_middleware import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS - Restrict to specific origins in production
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:9000,http://localhost:9001,http://127.0.0.1:9000,http://127.0.0.1:9001",
).split(",")

# Admin email for alerts
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@mugstore.com")

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


# Image storage configuration
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"

if USE_S3:
    # S3 configuration for cloud storage
    S3_BUCKET = os.getenv("S3_BUCKET", "")
    S3_REGION = os.getenv("S3_REGION", "us-east-1")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "")
    S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "")  # For MinIO/other S3-compatible
    logger.info(f"Using S3 storage: {S3_BUCKET}")
else:
    # Local filesystem storage
    images_path = os.path.join(os.path.dirname(__file__), "..", "..", "storage", "images")
    if os.path.exists(images_path):
        app.mount("/images", StaticFiles(directory=images_path), name="images")
        logger.info(f"Using local storage: {images_path}")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Include routers - API v1 (current)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(cart.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(rbac.router, prefix="/api/v1")
app.include_router(forecasting.router, prefix="/api/v1")
app.include_router(seed.router, prefix="/api/v1")
app.include_router(inventory_ml.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(delivery.router, prefix="/api/v1")

# Include routers - Legacy (backward compatibility)
app.include_router(auth.router, prefix="/api", tags=["auth-legacy"])
app.include_router(products.router, prefix="/api", tags=["products-legacy"])
app.include_router(categories.router, prefix="/api", tags=["categories-legacy"])
app.include_router(cart.router, prefix="/api", tags=["cart-legacy"])
app.include_router(orders.router, prefix="/api", tags=["orders-legacy"])
app.include_router(users.router, prefix="/api", tags=["users-legacy"])
app.include_router(admin.router, prefix="/api", tags=["admin-legacy"])
app.include_router(inventory.router, prefix="/api", tags=["inventory-legacy"])
app.include_router(recommendations.router, prefix="/api", tags=["recommendations-legacy"])
app.include_router(rbac.router, prefix="/api", tags=["rbac-legacy"])
app.include_router(forecasting.router, prefix="/api", tags=["forecasting-legacy"])
app.include_router(seed.router, prefix="/api", tags=["seed-legacy"])
app.include_router(inventory_ml.router, prefix="/api", tags=["inventory-ml-legacy"])
app.include_router(payments.router, prefix="/api", tags=["payments-legacy"])
app.include_router(delivery.router, prefix="/api", tags=["delivery-legacy"])

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

import time
import logging
import os
from typing import Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


# Production rate limits (configurable via environment)
RATE_LIMIT_DEFAULT = int(os.getenv("RATE_LIMIT_DEFAULT", "100"))
RATE_LIMIT_AUTH = int(os.getenv("RATE_LIMIT_AUTH", "10"))
RATE_LIMIT_API = int(os.getenv("RATE_LIMIT_API", "200"))


class RateLimiter:
    """In-memory rate limiter"""

    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)

    def is_allowed(
        self, key: str, max_requests: int, window_seconds: int
    ) -> Tuple[bool, int]:
        """Check if request is allowed"""
        now = time.time()
        window_start = now - window_seconds

        # Clean old requests
        self._requests[key] = [t for t in self._requests[key] if t > window_start]

        if len(self._requests[key]) >= max_requests:
            return False, 0

        self._requests[key].append(now)
        remaining = max_requests - len(self._requests[key])
        return True, remaining

    def reset(self, key: str):
        """Reset rate limit for a key"""
        if key in self._requests:
            del self._requests[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


# Rate limit configurations (per minute)
RATE_LIMITS = {
    "default": (RATE_LIMIT_DEFAULT, 60),
    "auth": (RATE_LIMIT_AUTH, 60),
    "api": (RATE_LIMIT_API, 60),
    "write": (50, 60),
}


def get_rate_limit_key(request: Request, limit_type: str = "default") -> str:
    """Get rate limit key based on IP or user"""
    # Try to get user ID if authenticated
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"

    # Fall back to IP
    client_ip = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()

    return f"ip:{client_ip}:{limit_type}"


def check_rate_limit(request: Request, limit_type: str = "default") -> bool:
    """Check if request is within rate limit"""
    max_requests, window_seconds = RATE_LIMITS.get(limit_type, RATE_LIMITS["default"])
    key = get_rate_limit_key(request, limit_type)

    allowed, remaining = rate_limiter.is_allowed(key, max_requests, window_seconds)

    if not allowed:
        logger.warning(f"Rate limit exceeded for {key}")

    return allowed


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)

        limit_type = "default"
        if "/auth/login" in request.url.path:
            limit_type = "auth"
        elif request.method in ["POST", "PUT", "DELETE"]:
            limit_type = "write"

        if not check_rate_limit(request, limit_type):
            raise HTTPException(
                status_code=429, detail="Too many requests. Please try again later."
            )

        response = await call_next(request)
        return response

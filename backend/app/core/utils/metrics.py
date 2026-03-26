from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from time import time
import logging

logger = logging.getLogger(__name__)

request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

active_users = Gauge(
    'active_users',
    'Number of currently active users'
)

forecast_requests = Counter(
    'forecast_requests_total',
    'Total forecast requests',
    ['product_id']
)

auto_orders_created = Counter(
    'auto_orders_created_total',
    'Total auto-orders created'
)

inventory_alerts = Gauge(
    'inventory_alerts_active',
    'Number of active inventory alerts'
)

stock_levels = Gauge(
    'stock_level',
    'Current stock level',
    ['product_id']
)


class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time()

        await self.app(scope, receive, send)

        duration = time() - start_time
        method = request.method
        path = request.url.path
        
        status_code = 200
        if hasattr(request, '_route'):
            status_code = 200
        
        endpoint = path.split('/')[1] if '/' in path else path
        
        request_count.labels(
            method=method,
            endpoint=endpoint,
            status=status_code
        ).inc()

        request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)


def setup_metrics(app: FastAPI):
    @app.get("/metrics")
    async def metrics():
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    
    return app

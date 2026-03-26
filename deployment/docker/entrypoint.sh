#!/bin/bash
set -e

# Entrypoint script for Docker container
# Supports running tests or starting the application

echo "================================"
echo "Mugnificent E-Commerce Platform"
echo "================================"

case "${1:-app}" in
    test)
        echo "Running tests..."
        cd /app
        python -m pytest tests/ -v --tb=short
        ;;
    test-e2e)
        echo "Running E2E tests..."
        cd /app
        python -m pytest tests/test_e2e.py -v --tb=short
        ;;
    test-coverage)
        echo "Running tests with coverage..."
        cd /app
        python -m pytest tests/ -v --cov=app --cov-report=term-missing
        ;;
    shell)
        echo "Starting shell..."
        /bin/bash
        ;;
    app|"")
        echo "Starting application..."
        
        # Create database tables
        python -c "from app.core.data.database import Base, engine; Base.metadata.create_all(bind=engine)"
        
        # Start uvicorn in background
        uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        UVICORN_PID=$!
        
        # Wait for uvicorn to start
        sleep 3
        
        # Start nginx in foreground
        nginx -g 'daemon off;' &
        NGINX_PID=$!
        
        # Wait for either process to exit
        wait -n
        
        # If one exits, kill the other
        kill $UVICORN_PID $NGINX_PID 2>/dev/null || true
        ;;
    *)
        echo "Unknown command: $1"
        echo "Usage: $0 {app|test|test-e2e|test-coverage|shell}"
        exit 1
        ;;
esac

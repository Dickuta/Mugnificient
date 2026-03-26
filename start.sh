#!/bin/bash
# Start the application (development mode)

set -e

echo "🚀 Starting Mugnificent"
echo "======================="

cd "$(dirname "$0")"

echo "Building and starting services..."
docker compose -f deployment/docker/docker-compose.yml up -d --build

echo ""
echo "Waiting for services to be healthy..."
sleep 10

echo ""
echo "✅ Application is running!"
echo ""
echo "  Frontend:  http://localhost"
echo "  API:       http://localhost:8000"
echo "  API Docs:  http://localhost/docs"
echo "  Grafana:   http://localhost:3000 (admin/admin123)"
echo "  Prometheus: http://localhost:9090"
echo ""
echo "To seed test data:"
echo "  docker compose exec app python -m app.seed_data"

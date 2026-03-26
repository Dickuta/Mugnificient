#!/bin/bash
# Start the application

set -e

echo "🚀 Starting Mugnificent"
echo "======================="

cd "$(dirname "$0")/.."

docker compose -f deployment/docker/docker-compose.yml up -d --build

echo ""
echo "✅ Application is running!"
echo ""
echo "  Frontend:   http://localhost"
echo "  API:        http://localhost:8000"
echo "  API Docs:   http://localhost/docs"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana:    http://localhost:3000"

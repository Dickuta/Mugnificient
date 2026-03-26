#!/bin/bash
# Start staging environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAGING_DIR="$SCRIPT_DIR/../staging"

echo "Starting staging environment..."
echo ""

cd "$STAGING_DIR"

# Build and start services
docker compose up -d --build

echo ""
echo "Waiting for services to be healthy..."
sleep 10

echo ""
echo "Staging environment is ready!"
echo ""
echo "Services:"
echo "  - App:         http://localhost:8080"
echo "  - API Docs:    http://localhost:8080/docs"
echo "  - PostgreSQL:  localhost:5433"
echo "  - Redis:       localhost:6380"
echo "  - Prometheus:  http://localhost:9091"
echo "  - Grafana:     http://localhost:3001 (admin/staging123)"
echo ""
echo "To seed test data:"
echo "  docker compose exec app python -m app.seed_data"

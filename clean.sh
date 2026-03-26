#!/bin/bash
# Clean up all Docker containers, volumes, and temp files

set -e

echo "🧹 Cleaning Up"
echo "=============="

cd "$(dirname "$0")"

echo "Stopping and removing containers..."
docker compose -f deployment/docker/docker-compose.yml down -v 2>/dev/null || true
docker compose -f tests/docker-compose.test.yml down -v 2>/dev/null || true
docker compose -f tests/staging/docker-compose.yml down -v 2>/dev/null || true

echo "Removing unused Docker resources..."
docker system prune -f

echo "Cleaning test results..."
rm -rf tests/results/* 2>/dev/null || true
rm -rf tests/e2e/playwright/test-report/* 2>/dev/null || true
rm -rf tests/e2e/playwright/results/* 2>/dev/null || true

echo ""
echo "✅ Cleanup complete!"

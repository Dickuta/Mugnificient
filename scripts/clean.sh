#!/bin/bash
# Clean up all Docker resources

set -e

echo "🧹 Cleaning Up"
echo "=============="

cd "$(dirname "$0")/.."

docker compose -f deployment/docker/docker-compose.yml down -v 2>/dev/null || true
docker compose -f tests/docker-compose.test.yml down -v 2>/dev/null || true

docker system prune -f

rm -rf tests/results/* 2>/dev/null || true

echo "✅ Cleanup complete!"

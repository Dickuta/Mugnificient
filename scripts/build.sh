#!/bin/bash
# Build all Docker images

set -e

echo "🔨 Building Mugnificent"
echo "======================"

cd "$(dirname "$0")/.."

docker compose -f deployment/docker/docker-compose.yml build
docker compose -f tests/docker-compose.test.yml build

echo "✅ Build complete!"

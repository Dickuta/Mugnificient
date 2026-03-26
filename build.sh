#!/bin/bash
# Build all Docker images

set -e

echo "🔨 Building Mugnificent"
echo "======================"

cd "$(dirname "$0")"

echo "Building production image..."
docker compose -f deployment/docker/docker-compose.yml build

echo ""
echo "Building test image..."
docker compose -f tests/docker-compose.test.yml build

echo ""
echo "✅ Build complete!"
echo ""
echo "Run './start.sh' to start the application"
echo "Run './test.sh' to run tests"

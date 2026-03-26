#!/bin/bash
# Build all Docker images

echo "🔨 Building Mugnificent"
echo "======================"

cd "$(dirname "$0")/.."

# Build main application
echo "Building main application..."
if docker compose -f deployment/docker/docker-compose.yml build; then
    echo "✅ Main application build complete!"
else
    echo "❌ Main application build failed"
    exit 1
fi

echo ""
echo "Note: Test images can be built separately with:"
echo "  docker compose -f tests/docker-compose.test.yml build"

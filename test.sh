#!/bin/bash
# Run all tests (backend + frontend E2E)

set -e

echo "🧪 Running Full Test Suite"
echo "=========================="

cd "$(dirname "$0")/tests"

mkdir -p results

echo "Building and running all tests..."
docker compose -f docker-compose.test.yml --profile test --profile e2e up --build --abort-on-container-exit --exit-code-from test-runner

echo ""
echo "Cleaning up..."
docker compose -f docker-compose.test.yml down

echo "✅ All tests complete!"

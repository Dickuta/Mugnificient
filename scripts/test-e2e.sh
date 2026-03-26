#!/bin/bash
# Run E2E browser tests

set -e

echo "🎭 Running E2E Browser Tests"
echo "============================"

cd "$(dirname "$0")/.."

# Start services
docker compose -f tests/docker-compose.test.yml up -d postgres backend frontend
sleep 15

# Run Playwright tests
docker compose -f tests/docker-compose.test.yml --profile e2e run --rm playwright

# Cleanup
docker compose -f tests/docker-compose.test.yml down

echo "✅ E2E tests complete!"

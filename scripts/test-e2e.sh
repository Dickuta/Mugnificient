#!/bin/bash
# Run E2E browser tests

echo "🎭 Running E2E Browser Tests"
echo "============================"

cd "$(dirname "$0")/.."

# Check if test compose file exists
if [ ! -f "tests/docker-compose.test.yml" ]; then
    echo "❌ Test configuration not found"
    exit 1
fi

# Start services
echo "Starting test services..."
docker compose -f tests/docker-compose.test.yml up -d postgres backend
sleep 15

# Run Playwright tests
echo "Running Playwright tests..."
docker compose -f tests/docker-compose.test.yml --profile e2e run --rm playwright
TEST_EXIT_CODE=$?

# Cleanup
docker compose -f tests/docker-compose.test.yml down

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ E2E tests complete!"
else
    echo "❌ E2E tests failed with exit code: $TEST_EXIT_CODE"
    exit $TEST_EXIT_CODE
fi

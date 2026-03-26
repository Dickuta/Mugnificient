#!/bin/bash
# Run all tests using Docker Compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "Mugnificent E2E Test Suite"
echo "========================================"
echo ""

cd "$SCRIPT_DIR"

# Create results directory
mkdir -p results

echo "Building and running tests..."
echo ""

# Run tests with test-runner service
docker compose -f docker-compose.test.yml --profile test up --build --abort-on-container-exit --exit-code-from test-runner

EXIT_CODE=$?

echo ""
echo "========================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed (exit code: $EXIT_CODE)"
fi
echo "========================================"
echo ""
echo "Test results saved to: $SCRIPT_DIR/results/"

exit $EXIT_CODE

#!/bin/bash
# Run E2E tests (frontend + API) using Docker Compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "Mugnificent E2E Test Suite"
echo "========================================"
echo ""
echo "This will:"
echo "  1. Start the backend API"
echo "  2. Run API workflow tests"
echo "  3. Start the frontend"
echo "  4. Run Playwright browser tests"
echo ""

cd "$SCRIPT_DIR"

# Create results directory
mkdir -p results/e2e

echo "Step 1: Starting backend services..."
docker compose -f docker-compose.test.yml up -d postgres backend

echo ""
echo "Waiting for backend to be healthy..."
sleep 10

echo ""
echo "Step 2: Running API workflow tests..."
docker compose -f docker-compose.test.yml run --rm test-runner pytest tests/e2e/api/ -v --tb=short

API_EXIT=$?

echo ""
echo "Step 3: Starting frontend for browser tests..."
docker compose -f docker-compose.test.yml up -d frontend

echo ""
echo "Waiting for frontend to be ready..."
sleep 15

echo ""
echo "Step 4: Running Playwright browser tests..."
docker compose -f docker-compose.test.yml --profile e2e run --rm playwright

E2E_EXIT=$?

echo ""
echo "========================================"
echo "Test Results"
echo "========================================"
echo "API Tests: $([ $API_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "E2E Tests: $([ $E2E_EXIT -eq 0 ] && echo '✅ PASSED' || echo '❌ FAILED')"
echo "========================================"

# Cleanup
echo ""
echo "Cleaning up..."
docker compose -f docker-compose.test.yml down

EXIT_CODE=$((API_EXIT + E2E_EXIT))
exit $EXIT_CODE

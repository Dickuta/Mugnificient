#!/bin/bash
# Run all tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Running all tests..."

cd "$PROJECT_DIR"

# Run Python tests (excluding playwright)
pytest tests/ -v --ignore=tests/e2e/playwright "$@"

echo ""
echo "All tests completed!"

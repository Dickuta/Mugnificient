#!/bin/bash
# Run integration tests against staging environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Running integration tests..."
echo "Make sure staging environment is running:"
echo "  cd tests/staging && docker compose up -d"
echo ""

cd "$PROJECT_DIR"

# Run integration tests
pytest tests/integration/ -v "$@"

echo ""
echo "Integration tests completed!"

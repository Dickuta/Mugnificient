#!/bin/bash
# Run unit tests only

set -e

echo "🧪 Running Unit Tests"
echo "====================="

cd "$(dirname "$0")/.."

docker compose -f tests/docker-compose.test.yml --profile test run --rm test-runner pytest tests/unit/ -v --tb=short

echo "✅ Unit tests complete!"

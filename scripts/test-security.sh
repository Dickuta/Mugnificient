#!/bin/bash
# Run security tests only

set -e

echo "🔒 Running Security Tests"
echo "========================="

cd "$(dirname "$0")/.."

docker compose -f tests/docker-compose.test.yml --profile test run --rm test-runner pytest tests/unit/backend/test_security.py -v --tb=short

echo "✅ Security tests complete!"

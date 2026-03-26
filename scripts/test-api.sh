#!/bin/bash
# Run API tests only

set -e

echo "🧪 Running API Tests"
echo "===================="

cd "$(dirname "$0")/.."

mkdir -p tests/results

docker compose -f tests/docker-compose.test.yml --profile test up --build --abort-on-container-exit --exit-code-from test-runner

docker compose -f tests/docker-compose.test.yml down

echo "✅ API tests complete!"

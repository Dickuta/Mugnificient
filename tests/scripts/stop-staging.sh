#!/bin/bash
# Stop staging environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAGING_DIR="$SCRIPT_DIR/../staging"

echo "Stopping staging environment..."

cd "$STAGING_DIR"

docker compose down

echo ""
echo "Staging environment stopped."
echo "To remove data volumes: docker compose down -v"

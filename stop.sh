#!/bin/bash
# Stop the application

set -e

echo "🛑 Stopping Mugnificent"
echo "======================="

cd "$(dirname "$0")"

docker compose -f deployment/docker/docker-compose.yml down

echo ""
echo "✅ Application stopped."
echo ""
echo "To remove all data volumes: ./clean.sh"

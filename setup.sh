#!/bin/bash
# Initial setup - run this once after cloning

set -e

echo "🔧 Setting up Mugnificent"
echo "========================"

cd "$(dirname "$0")"

echo "Making scripts executable..."
chmod +x *.sh
chmod +x tests/*.sh
chmod +x tests/scripts/*.sh 2>/dev/null || true

echo ""
echo "Building Docker images..."
./build.sh

echo ""
echo "Seeding database with test data..."
docker compose -f deployment/docker/docker-compose.yml up -d postgres
sleep 5
docker compose -f deployment/docker/docker-compose.yml run --rm app python -m app.seed_data
docker compose -f deployment/docker/docker-compose.yml down

echo ""
echo "✅ Setup complete!"
echo ""
echo "Quick start:"
echo "  ./start.sh    - Start the application"
echo "  ./test.sh     - Run all tests"
echo "  ./stop.sh     - Stop the application"

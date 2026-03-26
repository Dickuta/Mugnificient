#!/bin/bash
# Initial setup after cloning

set -e

echo "🔧 Setting up Mugnificent"
echo "========================"

cd "$(dirname "$0")/.."

echo "Making scripts executable..."
chmod +x scripts/*.sh

echo ""
echo "Building Docker images..."
./scripts/build.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "Quick start:"
echo "  ./scripts/run.sh start    - Start the application"
echo "  ./scripts/run.sh test     - Run all tests"
echo "  ./scripts/run.sh stop     - Stop the application"

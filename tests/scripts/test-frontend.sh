#!/bin/bash
# Run frontend E2E tests with Playwright

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PLAYWRIGHT_DIR="$PROJECT_DIR/e2e/playwright"

echo "Running Playwright E2E tests..."
echo "Make sure staging environment is running:"
echo "  cd tests/staging && docker compose up -d"
echo ""

cd "$PLAYWRIGHT_DIR"

# Install Playwright if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Playwright..."
    npm install
    npx playwright install chromium
fi

# Run tests
npx playwright test "$@"

echo ""
echo "Playwright tests completed!"
echo "View report: open tests/e2e/playwright/test-report/index.html"

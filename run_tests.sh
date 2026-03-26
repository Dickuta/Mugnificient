#!/bin/bash
# Run E2E Tests for Mugnificent
# This script runs the end-to-end tests with simulated payments/logistics

set -e

cd "$(dirname "$0")/backend"

echo "=========================================="
echo "Mugnificent E2E Test Suite"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run tests
echo ""
echo "Running E2E tests..."
echo "=========================================="

pytest tests/test_e2e.py -v --tb=short

echo ""
echo "=========================================="
echo "E2E Tests Complete!"
echo "=========================================="

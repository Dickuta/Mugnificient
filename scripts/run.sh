#!/bin/bash
# Main entry point - shows available commands

set -e

cd "$(dirname "$0")/.."

if [ -z "$1" ]; then
    echo "============================================"
    echo "  Mugnificent E-Commerce Platform"
    echo "============================================"
    echo ""
    echo "Usage: ./scripts/run.sh <command>"
    echo ""
    echo "Application Commands:"
    echo "  start       - Start the application"
    echo "  stop        - Stop the application"
    echo "  restart     - Restart the application"
    echo "  build       - Build all Docker images"
    echo "  setup       - Initial setup after clone"
    echo "  clean       - Clean up containers and temp files"
    echo "  logs        - Show application logs"
    echo "  status      - Show running services"
    echo "  seed        - Seed database with test data"
    echo ""
    echo "Test Commands:"
    echo "  test        - Run all tests (API + E2E)"
    echo "  test-api    - Run API tests only"
    echo "  test-e2e    - Run E2E tests only"
    echo "  test-unit   - Run unit tests only"
    echo "  test-security - Run security tests only"
    echo ""
    exit 0
fi

case "$1" in
    start)
        ./scripts/start.sh
        ;;
    stop)
        ./scripts/stop.sh
        ;;
    restart)
        ./scripts/stop.sh
        sleep 2
        ./scripts/start.sh
        ;;
    build)
        ./scripts/build.sh
        ;;
    setup)
        ./scripts/setup.sh
        ;;
    clean)
        ./scripts/clean.sh
        ;;
    logs)
        docker compose -f deployment/docker/docker-compose.yml logs -f
        ;;
    status)
        docker compose -f deployment/docker/docker-compose.yml ps
        ;;
    seed)
        docker compose -f deployment/docker/docker-compose.yml up -d postgres
        sleep 5
        docker compose -f deployment/docker/docker-compose.yml run --rm app python -m app.seed_data
        echo "✅ Database seeded!"
        ;;
    test)
        ./scripts/test-all.sh
        ;;
    test-api)
        ./scripts/test-api.sh
        ;;
    test-e2e)
        ./scripts/test-e2e.sh
        ;;
    test-unit)
        ./scripts/test-unit.sh
        ;;
    test-security)
        ./scripts/test-security.sh
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run './scripts/run.sh' to see available commands"
        exit 1
        ;;
esac

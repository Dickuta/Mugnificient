#!/bin/bash
# Main entry point - shows available commands

set -e

cd "$(dirname "$0")"

if [ -z "$1" ]; then
    echo "============================================"
    echo "  Mugnificent E-Commerce Platform"
    echo "============================================"
    echo ""
    echo "Usage: ./run.sh <command>"
    echo ""
    echo "Commands:"
    echo "  start       - Start the application"
    echo "  stop        - Stop the application"
    echo "  restart     - Restart the application"
    echo "  test        - Run all tests"
    echo "  test-api    - Run API tests only"
    echo "  test-e2e    - Run E2E tests only"
    echo "  build       - Build all Docker images"
    echo "  setup       - Initial setup after clone"
    echo "  clean       - Clean up containers and temp files"
    echo "  logs        - Show application logs"
    echo "  status      - Show running services"
    echo "  seed        - Seed database with test data"
    echo ""
    exit 0
fi

case "$1" in
    start)
        ./start.sh
        ;;
    stop)
        ./stop.sh
        ;;
    restart)
        ./stop.sh
        sleep 2
        ./start.sh
        ;;
    test)
        ./test.sh
        ;;
    test-api)
        cd tests && docker compose -f docker-compose.test.yml --profile test up --build --abort-on-container-exit --exit-code-from test-runner
        ;;
    test-e2e)
        cd tests && ./run-e2e.sh
        ;;
    build)
        ./build.sh
        ;;
    setup)
        ./setup.sh
        ;;
    clean)
        ./clean.sh
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
    *)
        echo "Unknown command: $1"
        echo "Run './run.sh' to see available commands"
        exit 1
        ;;
esac

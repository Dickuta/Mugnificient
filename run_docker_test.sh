#!/bin/bash
# Test runner script for Mugnificent E-Commerce Platform
# Runs tests in a production-like Docker environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCKER_DIR="$PROJECT_DIR/deployment/docker"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Build the Docker images
build() {
    print_header "Building Docker images"
    cd "$DOCKER_DIR"
    docker compose -f docker-compose.test.yml build
    print_success "Build complete"
}

# Run all tests
run_tests() {
    print_header "Running all tests"
    cd "$DOCKER_DIR"
    docker compose -f docker-compose.test.yml run --rm app test
}

# Run E2E tests only
run_e2e_tests() {
    print_header "Running E2E tests"
    cd "$DOCKER_DIR"
    docker compose -f docker-compose.test.yml run --rm app test-e2e
}

# Run tests with coverage
run_coverage() {
    print_header "Running tests with coverage"
    cd "$DOCKER_DIR"
    docker compose -f docker-compose.test.yml run --rm app test-coverage
}

# Start the application
start_app() {
    print_header "Starting application"
    cd "$DOCKER_DIR"
    docker compose -f docker-compose.test.yml up -d
    print_success "Application started"
    echo ""
    echo "Access the application at:"
    echo "  - Frontend: http://localhost"
    echo "  - API: http://localhost/api/v1/"
    echo "  - API Docs: http://localhost/docs"
    echo ""
    echo "To stop: docker compose -f docker-compose.test.yml down"
}

# Stop the application
stop_app() {
    print_header "Stopping application"
    cd "$DOCKER_DIR"
    docker compose -f docker-compose.test.yml down
    print_success "Application stopped"
}

# Clean up everything
cleanup() {
    print_header "Cleaning up"
    cd "$DOCKER_DIR"
    docker compose -f docker-compose.test.yml down -v --rmi local
    print_success "Cleanup complete"
}

# Show logs
logs() {
    cd "$DOCKER_DIR"
    docker compose -f docker-compose.test.yml logs -f
}

# Main menu
show_menu() {
    echo ""
    echo -e "${BLUE}Mugnificent Test Runner${NC}"
    echo "========================="
    echo "1) Build Docker images"
    echo "2) Run all tests"
    echo "3) Run E2E tests"
    echo "4) Run tests with coverage"
    echo "5) Start application"
    echo "6) Stop application"
    echo "7) Show logs"
    echo "8) Cleanup (remove containers, volumes, images)"
    echo "9) Exit"
    echo ""
}

# Handle command line arguments
case "${1:-}" in
    build)
        check_docker
        build
        ;;
    test)
        check_docker
        run_tests
        ;;
    e2e)
        check_docker
        run_e2e_tests
        ;;
    coverage)
        check_docker
        run_coverage
        ;;
    start)
        check_docker
        start_app
        ;;
    stop)
        stop_app
        ;;
    logs)
        logs
        ;;
    cleanup)
        cleanup
        ;;
    *)
        check_docker
        show_menu
        read -p "Select option: " choice
        case $choice in
            1) build ;;
            2) run_tests ;;
            3) run_e2e_tests ;;
            4) run_coverage ;;
            5) start_app ;;
            6) stop_app ;;
            7) logs ;;
            8) cleanup ;;
            9) exit 0 ;;
            *) print_error "Invalid option" ;;
        esac
        ;;
esac

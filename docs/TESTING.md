# Testing Guide

## Overview

Mugnificent uses Docker Compose for all testing, ensuring tests run in a production-like environment with proper isolation.

## Quick Start

```bash
# Run all tests
./scripts/run.sh test

# Run API tests only
./scripts/run.sh test-api

# Run E2E tests only
./scripts/run.sh test-e2e
```

## Test Structure

```
tests/
├── unit/backend/           # Backend unit tests
│   ├── test_auth.py        # Authentication (10 tests)
│   ├── test_ecommerce.py   # Products, Cart, Orders (25 tests)
│   ├── test_forecasting.py # Forecasting, Inventory, Admin (20 tests)
│   ├── test_security.py    # SQL injection, XSS, Rate limiting (20 tests)
│   └── test_edge_cases.py  # Edge cases, boundaries (25 tests)
│
├── e2e/api/                # API workflow tests
│   └── test_e2e_workflows.py # Complete user journeys (15 tests)
│
├── e2e/playwright/         # Browser E2E tests
│   └── tests/
│       ├── auth.spec.ts          # Login, Register (4 tests)
│       ├── products.spec.ts      # Products, Cart (6 tests)
│       ├── forecasting.spec.ts   # Forecasting dashboard (11 tests)
│       └── user-journey.spec.ts  # Complete flows (8 tests)
│
├── integration/api/        # Integration tests
│   └── test_api_integration.py (10 tests)
│
├── docker-compose.test.yml # Test Docker environment
└── run-tests.sh            # Test runner script
```

## Test Types

### 1. Unit Tests (Backend)
Fast, isolated tests using SQLite in-memory database.

```bash
./scripts/run.sh test-unit
```

Coverage:
- Authentication (login, register, tokens)
- Products (CRUD, search)
- Cart (add, update, remove)
- Orders (checkout, history)
- Forecasting (dashboard, predictions)
- Auto-order (settings, thresholds)
- Inventory ML (predictions, refill requests)
- Admin/RBAC (permissions, roles)
- Security (SQL injection, XSS, rate limiting)
- Edge cases (pagination, boundaries)

### 2. API Workflow Tests (E2E)
Tests complete user workflows through the API.

```bash
./scripts/run.sh test-api
```

Workflows:
- Customer journey (register → login → browse → cart → checkout)
- Admin workflow (dashboard → analytics → RBAC)
- Warehouse workflow (forecast → inventory → auto-order)
- Security workflow (access control verification)

### 3. Browser E2E Tests (Playwright)
Automated browser tests for frontend.

```bash
./scripts/run.sh test-e2e
```

Tests:
- Login/Register flows
- Product browsing
- Cart operations
- Forecasting dashboard
- Admin dashboard
- Access control

## Test Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Manager | manager | manager123 |
| Warehouse | warehouse | warehouse123 |
| Customer | student1 | student123 |
| Customer | alumni1 | alumni123 |

## Test Reports

After running tests, reports are saved to:
- `tests/results/junit.xml` - JUnit XML format
- `tests/e2e/playwright/test-report/` - Playwright HTML report

View Playwright report:
```bash
cd tests/e2e/playwright && npx playwright show-report
```

## Running Specific Tests

```bash
# Run only security tests
docker compose -f tests/docker-compose.test.yml --profile test run --rm test-runner pytest tests/unit/backend/test_security.py -v

# Run specific test class
docker compose -f tests/docker-compose.test.yml --profile test run --rm test-runner pytest tests/unit/backend/test_auth.py::TestLogin -v

# Run specific test
docker compose -f tests/docker-compose.test.yml --profile test run --rm test-runner pytest tests/unit/backend/test_security.py::TestSQLInjectionPrevention::test_login_sql_injection_username -v
```

## CI/CD Integration

For CI/CD pipelines, use the JUnit XML output:

```yaml
# Example GitHub Actions
- name: Run tests
  run: ./scripts/run.sh test
  
- name: Upload test results
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: test-results
    path: tests/results/
```

## Troubleshooting

### Tests fail with database errors
```bash
./scripts/run.sh clean
./scripts/run.sh test
```

### Playwright browser not found
```bash
cd tests/e2e/playwright
npx playwright install chromium
```

### Docker build fails
```bash
docker system prune -a
./scripts/run.sh build
```

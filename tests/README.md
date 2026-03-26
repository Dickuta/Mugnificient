# Mugnificent Test Suite

## Quick Start

Run all tests using Docker Compose:
```bash
cd tests
./run-tests.sh
```

## Test Structure

```
tests/
├── unit/backend/           # Backend unit tests
│   ├── test_auth.py       # Authentication tests
│   ├── test_forecasting.py # Forecasting & inventory tests
│   └── test_ecommerce.py  # Products, cart, orders tests
│
├── e2e/
│   ├── api/               # API workflow tests
│   │   └── test_e2e_workflows.py
│   └── playwright/        # Browser E2E tests
│       └── tests/
│           ├── auth.spec.ts
│           ├── products.spec.ts
│           ├── forecasting.spec.ts
│           └── user-journey.spec.ts
│
├── integration/api/       # Integration tests
├── staging/               # Staging environment
├── docker-compose.test.yml # Test Docker setup
├── run-tests.sh           # Run all tests
└── run-e2e.sh             # Run E2E tests
```

## Running Tests with Docker

### All Tests (Backend + Frontend)
```bash
cd tests
./run-tests.sh
```

### API Tests Only
```bash
cd tests
docker compose -f docker-compose.test.yml --profile test up --build --abort-on-container-exit --exit-code-from test-runner
```

### E2E Browser Tests
```bash
cd tests
./run-e2e.sh
```

## Test Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Manager | manager | manager123 |
| Warehouse Staff | warehouse | warehouse123 |
| Customer | student1 | student123 |
| Customer | alumni1 | alumni123 |

## Workflows Tested

1. **Customer Journey**: Register → Login → Browse → Cart → Checkout
2. **Admin Workflow**: Dashboard → Analytics → RBAC Management
3. **Warehouse Workflow**: Forecast → Inventory ML → Auto-order → Refill
4. **Security**: Auth required, Role-based access, Token validation

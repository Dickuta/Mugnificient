# Frontend E2E Tests with Playwright

## Quick Start

```bash
cd tests/e2e/playwright
npm install
npx playwright install chromium
npx playwright test
```

## Test Files

| File | Description |
|------|-------------|
| `auth.spec.ts` | Login, Register, Authentication |
| `products.spec.ts` | Product browsing, Cart operations |
| `forecasting.spec.ts` | Forecasting dashboard, Inventory ML |
| `user-journey.spec.ts` | Complete user workflows |

## Prerequisites

1. Backend API running on `http://localhost:8000`
2. Frontend running on `http://localhost:8080`

## Running with Docker

```bash
# Start all services
cd tests
docker compose -f docker-compose.test.yml up -d

# Run Playwright tests
docker compose -f docker-compose.test.yml --profile e2e run --rm playwright

# Or run from the playwright directory
cd tests/e2e/playwright
npm test
```

## View Reports

```bash
# HTML Report
npx playwright show-report

# Or open the HTML file
open test-report/index.html
```

## Test Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Warehouse | warehouse | warehouse123 |
| Customer | student1 | student123 |

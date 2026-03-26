# Testing Guide

## Quick Start

### 1. Seed Database
```bash
cd backend
python -m app.seed_data
```

This creates:
- 5 users (admin, manager, warehouse, 2 customers)
- 8 UoS themed products
- 90 days of historical sales data
- Seasonal patterns for University calendar

### 2. Start Application
```bash
cd deployment/docker
docker-compose up -d
```

### 3. Run Tests

Access the application:
- Frontend: http://localhost
- API: http://localhost/docs

## Test Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Manager | manager | manager123 |
| Warehouse Staff | warehouse | warehouse123 |
| Customer | student1 | student123 |
| Customer | alumni1 | alumni123 |

## Test Scenarios

See `e2e/test_scenarios.py` for detailed test scenarios.

### Key Workflows to Test:

1. **View Forecasts**
   - Login as warehouse
   - Navigate to Stock Forecasting
   - Verify demand predictions

2. **Configure Seasonal Patterns**
   - Go to Seasonal Patterns tab
   - Set September to 2.0x (intake)
   - Verify forecast updates

3. **Enable Auto-Order**
   - Go to Auto-Order Settings
   - Enable for products
   - Set threshold

4. **Place Order**
   - Login as student
   - Add product to cart
   - Complete checkout
   - Verify stock deducted

5. **Trigger Refill**
   - Login as admin
   - View pending refills
   - Approve/Receive stock

## Unit Tests

Run unit tests:
```bash
cd backend
pytest tests/ -v
```

## API Tests

Test API endpoints:
```bash
# Health check
curl http://localhost/health

# Login
curl -X POST http://localhost/api/v1/auth/login \
  -d "username=admin&password=admin123"

# Get forecasts (requires auth token)
curl -H "Authorization: Bearer <token>" \
  http://localhost/api/v1/forecasting/dashboard
```

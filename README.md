# Mug Store - E-Commerce Full Stack Project

A modern full-stack e-commerce application for selling mugs, built with FastAPI backend and Quasar frontend.

## Product Categories
- Classic Mugs (ceramic, stoneware, earthenware)
- Travel Mugs (insulated, thermal)
- Sports Mugs (shaker bottles, outdoor)
- Kids Mugs (character, color-change)
- Premium Mugs (hand-painted, gold trim)

## Project Structure

```
Project Hackathon/
├── eshop-backend/          # FastAPI Backend
│   ├── app/
│   │   ├── core/          # Database, Security, Cache, RBAC
│   │   ├── models/        # SQLAlchemy Models
│   │   ├── routers/      # API Endpoints
│   │   └── schemas/      # Pydantic Schemas
│   ├── alembic/           # Database migrations
│   ├── images/           # Product images
│   ├── requirements.txt
│   ├── .env
│   └── eshop.db          # SQLite database
│
└── eshop-frontend/        # Quasar Frontend
    ├── src/
    │   ├── boot/         # Axios API
    │   ├── components/    # Vue Components
    │   ├── css/          # Styles
    │   ├── layouts/      # Page Layouts
    │   ├── pages/       # Vue Pages
    │   ├── router/      # Vue Router
    │   └── stores/      # Pinia Stores
    ├── quasar.config.js
    ├── package.json
    └── index.html
```

---

# Backend (FastAPI)

## Tech Stack
- **Framework**: FastAPI
- **Database**: SQLite (default) or PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (12 rounds)
- **Caching**: In-memory caching with TTL

## Quick Start

### Using SQLite (Default - No Setup Required)
```bash
cd eshop-backend
pip install -r requirements.txt
USE_SQLITE=true uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Using PostgreSQL
```bash
export USE_SQLITE=false
# Or update .env file
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eshop
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_SQLITE` | `true` | Use SQLite instead of PostgreSQL |
| `POSTGRES_HOST` | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_DB` | `eshop` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password |
| `SECRET_KEY` | (auto-generated) | JWT secret key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiry time |
| `STRIPE_SECRET_KEY` | - | Stripe secret key |
| `STRIPE_PUBLISHABLE_KEY` | - | Stripe publishable key |
| `SMTP_HOST` | `smtp.gmail.com` | Email SMTP host |
| `SMTP_PORT` | `587` | Email SMTP port |
| `SMTP_USER` | - | Email username |
| `SMTP_PASSWORD` | - | Email password |

---

# Features

## 1. Recommendation Engine
| Endpoint | Description |
|----------|-------------|
| `/api/recommendations/featured` | Featured products |
| `/api/recommendations/popular` | Most sold products |
| `/api/recommendations/new-arrivals` | Recently added |
| `/api/recommendations/similar/{id}` | Same category |
| `/api/recommendations/bought-together/{id}` | Frequently bought together |
| `/api/recommendations/for-you` | Personalized (requires login) |

## 2. Inventory Management
| Endpoint | Description |
|----------|-------------|
| `/api/inventory/dashboard` | Inventory overview |
| `/api/inventory/products` | Stock levels |
| `/api/inventory/alerts` | Restock alerts |
| `/api/inventory/suppliers` | Supplier management |
| `/api/inventory/stock/adjust` | Adjust stock |

## 3. Payment Integration (Stripe)
| Endpoint | Description |
|----------|-------------|
| `GET /api/payments/config` | Get payment config |
| `POST /api/payments/create-intent` | Create payment intent |
| `POST /api/payments/confirm` | Confirm payment |
| `POST /api/payments/checkout-session` | Stripe checkout |
| `POST /api/payments/refund` | Refund (admin) |

## 4. Delivery Integration
| Endpoint | Description |
|----------|-------------|
| `POST /api/delivery/create` | Create shipment |
| `GET /api/delivery/track/{tracking}` | Track delivery |
| `POST /api/delivery/cancel/{tracking}` | Cancel shipment |
| `GET /api/delivery/providers` | List providers |

**Providers:** InHouse Delivery (default), DHL

## 5. Real-Time Notifications
- WebSocket: `WS /ws/notifications`
- SSE: `GET /api/notifications/stream`
- Notifications for orders, stock alerts

## 6. Email Notifications
- Order confirmation
- Order shipped
- Welcome email
- Password reset
- Stock alerts

## 7. RBAC (Role-Based Access Control)
- **Roles**: admin, manager, staff, customer
- **22 Permissions**: view_products, create_products, manage_inventory, etc.
- **API Endpoints**: `/api/rbac/*`

## 8. Security Features
- Rate limiting (100 req/min default, 10 for auth)
- Security headers (XSS, CORS, HSTS, etc.)
- Input validation & sanitization
- Brute force protection (5 failed attempts)
- SQL injection prevention (via SQLAlchemy)
- JWT with expiration and unique token ID

---

# API Endpoints

## Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login (returns JWT) |
| GET | `/api/auth/me` | Get current user |

## Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List products |
| GET | `/api/products/featured` | Featured products |
| GET | `/api/products/{slug}` | Product by slug |
| POST | `/api/products/` | Create product |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |

## Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories/` | List categories |
| GET | `/api/categories/{slug}` | Category by slug |
| POST | `/api/categories/` | Create category |
| PUT | `/api/categories/{id}` | Update category |

## Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cart/` | Get cart |
| POST | `/api/cart/add` | Add item |
| PUT | `/api/cart/item/{id}` | Update quantity |
| DELETE | `/api/cart/item/{id}` | Remove item |

## Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders/` | List orders |
| GET | `/api/orders/{number}` | Order details |
| POST | `/api/orders/checkout` | Create order |
| POST | `/api/orders/{number}/pay` | Mark paid |

## Admin Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard` | Statistics |
| GET | `/api/admin/sales-by-category` | Sales by category |
| GET | `/api/admin/sales-over-time` | Sales trend |
| GET | `/api/admin/top-products` | Best sellers |
| GET | `/api/admin/recent-orders` | Latest orders |

## RBAC Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rbac/permissions` | List permissions |
| GET | `/api/rbac/roles` | List roles |
| POST | `/api/rbac/roles` | Create role |
| GET | `/api/rbac/my-permissions` | My permissions |
| POST | `/api/rbac/seed-defaults` | Seed defaults |

---

# Running the Application

## Backend
```bash
cd eshop-backend
USE_SQLITE=true uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Security Check: `http://localhost:8000/security`

## Frontend
```bash
cd eshop-frontend
npm install
npm run dev
```

- Frontend: `http://localhost:9001` (port may vary)

---

# Frontend Pages

| Path | Description |
|------|-------------|
| `/` | Home with featured, new, popular products |
| `/products` | Product listing with search & filter |
| `/products/:slug` | Product details |
| `/cart` | Shopping cart |
| `/checkout` | Checkout (requires login) |
| `/orders` | Order history |
| `/orders/:number` | Order details |
| `/profile` | User profile |
| `/admin` | Admin dashboard (requires staff) |
| `/auth/login` | Login |
| `/auth/register` | Register |

---

# Default Login

- **Username**: admin
- **Password**: admin123

---

# Security

## Implemented Security Measures

1. **Rate Limiting**
   - Default: 100 requests/minute
   - Auth: 10 requests/minute (prevents brute force)
   - Write: 30 requests/minute

2. **Security Headers**
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: 1; mode=block
   - Strict-Transport-Security: max-age=31536000
   - Referrer-Policy: strict-origin-when-cross-origin

3. **Input Validation**
   - Username: alphanumeric + underscore, 3-50 chars
   - Email: valid format required
   - Password: minimum 6 characters
   - All inputs sanitized

4. **Authentication**
   - bcrypt hashing (12 rounds)
   - JWT with expiration and unique JTI
   - Account lockout after 5 failed attempts

5. **CORS**
   - Configured for specific origins only

## Test Security
```bash
# Check security headers
curl -I http://localhost:8000/health

# Check security status
curl http://localhost:8000/security
```

---

# Troubleshooting

## Frontend won't start
- Ensure Node.js 18+ is installed
- Run `npm install` in the frontend directory

## Backend won't connect to database
- Default uses SQLite - no setup needed
- For PostgreSQL, ensure credentials are correct

## Port already in use
- Backend: port 8000
- Frontend: ports 9000/9001

---

# Version
- Current: 1.0.0
- Last Updated: March 2026

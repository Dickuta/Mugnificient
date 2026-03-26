# Docker Compose Deployment

## Quick Start

### 1. Configure Environment

```bash
# Copy environment template
cp ../../.env.production .env

# Edit with your values
nano .env
```

Required variables:
- `POSTGRES_PASSWORD` - Strong password
- `SECRET_KEY` - Run: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `ALLOWED_ORIGINS` - Your domain
- `ADMIN_EMAIL` - Admin email for alerts

### 2. Build and Start

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Verify

- API: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Commands

```bash
# Stop services
docker-compose down

# Restart
docker-compose restart

# Rebuild
docker-compose up -d --build

# View logs
docker-compose logs -f backend
```

## With Monitoring

```bash
docker-compose --profile monitoring up -d
```

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

# Docker Compose Deployment

## Quick Start

### 1. Environment is Pre-configured

The `.env` file is already configured with secure generated keys:

```bash
# The .env file already exists with secure keys
# Location: deployment/docker/.env
```

### 2. Build and Start

```bash
# From this directory (deployment/docker)
docker compose up -d --build

# Or from project root
docker compose -f deployment/docker/docker-compose.yml up -d
```

### 3. Access the Application

| Service | URL | Credentials |
|---------|-----|-------------|
| **Application** | http://localhost | - |
| **API Docs** | http://localhost/docs | - |
| **Admin Login** | http://localhost | admin / admin123 |
| **Grafana** | http://localhost:3000 | admin / (see .env) |
| **Prometheus** | http://localhost:9090 | - |
| **MinIO Console** | http://localhost:9001 | (see .env) |

## Environment Variables (.env)

| Variable | Value | Purpose |
|----------|-------|---------|
| `SECRET_KEY` | Auto-generated | JWT signing |
| `POSTGRES_DB` | mugnificent | Database name |
| `POSTGRES_USER` | mugnificent | Database user |
| `POSTGRES_PASSWORD` | Auto-generated | Database password |
| `REDIS_PASSWORD` | Auto-generated | Redis auth |
| `MINIO_ROOT_USER` | mugnificent-admin | MinIO username |
| `MINIO_ROOT_PASSWORD` | Auto-generated | MinIO password |
| `GRAFANA_PASSWORD` | Auto-generated | Grafana admin |
| `ALLOWED_ORIGINS` | http://localhost,... | CORS settings |

## Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Check status
docker compose ps

# Restart app
docker compose restart app
```

## Generate New Secret Key (Optional)

If you want to generate a new SECRET_KEY:

```bash
# Python
python3 -c "import secrets; print(secrets.token_urlsafe(48))"

# OpenSSL
openssl rand -base64 48

# Node.js
node -e "console.log(require('crypto').randomBytes(48).toString('base64'))"
```

Then update the SECRET_KEY in `.env` file.

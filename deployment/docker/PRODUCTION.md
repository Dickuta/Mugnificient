# Production Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Domain name with DNS configured
- SSL certificate (or use Let's Encrypt)

## Deployment Options

### Option 1: Railway (Recommended for Easy Setup)

1. **Push code to GitHub**

2. **Create Railway Account**
   - Go to [railway.app](https://railway.app) and sign up with GitHub

3. **Create New Project**
   ```
   Dashboard → New Project → Deploy from GitHub repo
   ```

4. **Add PostgreSQL Database**
   ```
   New → Database → Add PostgreSQL
   ```

5. **Configure Environment Variables**
   ```
   USE_SQLITE=false
   SECRET_KEY=<generate random key>
   ALLOWED_ORIGINS=https://yourappname.up.railway.app
   ```

6. **Deploy**
   - Railway will automatically build and deploy from your Dockerfile

**Quick CLI Deploy:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Init project
railway init

# Add PostgreSQL
railway add plugin postgresql

# Deploy
railway up
```

---

### Option 2: Render

See [render.yaml](./render.yaml) for configuration.

---

### Option 3: Docker Compose (Local/VPS)

#### 1. Configure Environment Variables

```bash
# Copy production template
cp .env.production .env

# Edit with your values
nano .env
```

Required values:
- `POSTGRES_PASSWORD` - Strong password for database
- `SECRET_KEY` - Run: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `ALLOWED_ORIGINS` - Your production domain
- `GRAFANA_PASSWORD` - Strong password for Grafana

#### 2. Build and Start

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

#### 3. Run Migrations

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head
```

#### 4. Verify

- Frontend: http://localhost
- API: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Production with HTTPS

### Option 1: Reverse Proxy (Recommended)

Use nginx or traefik as a reverse proxy with SSL termination.

### Option 2: Docker with SSL

1. Generate SSL certificates:
```bash
# Using Let's Encrypt (requires domain pointing to server)
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

2. Update nginx config:
```bash
# Copy SSL config
cp frontend/nginx-ssl.conf frontend/nginx.conf

# Edit with your certificate paths
nano frontend/nginx.conf
```

3. Rebuild:
```bash
docker-compose up -d --build frontend
```

---

## Kubernetes Deployment

```bash
# Apply Kubernetes configurations
kubectl apply -f k8s/

# Or use Helm (recommended for production)
```

---

## Monitoring

Start monitoring stack:
```bash
docker-compose --profile monitoring up -d
```

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

---

## Backup & Recovery

### Database Backup
```bash
docker-compose exec postgres pg_dump -U mugstore mugstore > backup.sql
```

### Restore
```bash
docker-compose exec -T postgres psql -U mugstore mugstore < backup.sql
```

---

## Security Checklist

- [ ] Change default passwords
- [ ] Use strong `SECRET_KEY`
- [ ] Configure CORS for production domain
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Configure log monitoring
- [ ] Set up alerts for errors

---

## Troubleshooting

### Check logs
```bash
docker-compose logs backend
docker-compose logs postgres
```

### Restart services
```bash
docker-compose restart backend
```

### Reset database
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

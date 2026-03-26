# Deployment Options

Choose your preferred deployment method:

## 1. Railway (Recommended for Easy Setup)
- Best for Docker-based deployments
- $5/month credit on free tier
- [See instructions](./railway/README.md)

## 2. Render
- Free tier: 750 hours/month
- [See instructions](./render/README.md)

## 3. Docker Compose (Local/VPS)
- For self-hosted deployments
- Requires Docker installed
- [See instructions](./docker/README.md)

## 4. Kubernetes
- For cloud-native deployments
- Requires Kubernetes cluster
- [See k8s folder](./k8s/)

## Quick Comparison

| Provider | Free Tier | Difficulty | Best For |
|----------|-----------|------------|----------|
| Railway | $5 credit | Easy | Quick start |
| Render | 750h/month | Easy | Simple apps |
| Docker | Free | Medium | Full control |
| K8s | Varies | Hard | Enterprise |

## Common Setup

Regardless of deployment method, you'll need:

1. **Environment Variables**
   ```bash
   # Copy template
   cp .env.production .env
   
   # Required values:
   - POSTGRES_PASSWORD
   - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
   - ALLOWED_ORIGINS
   - ADMIN_EMAIL
   ```

2. **Database Migrations**
   ```bash
   alembic upgrade head
   ```

3. **Production Secrets**
   - Change all default passwords
   - Use strong SECRET_KEY
   - Configure CORS for your domain

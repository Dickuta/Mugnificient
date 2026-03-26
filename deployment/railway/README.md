# Railway Deployment

## Quick Deploy

1. **Push code to GitHub**

2. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

3. **Create New Project**
   ```
   Dashboard → New Project → Deploy from GitHub repo
   ```

4. **Add PostgreSQL**
   ```
   New → Database → Add PostgreSQL
   ```

5. **Configure Variables**
   ```
   USE_SQLITE=false
   SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_urlsafe(32))">
   ALLOWED_ORIGINS=https://yourappname.up.railway.app
   ADMIN_EMAIL=admin@yourdomain.com
   ```

6. **Deploy** - Railway auto-detects `railway.json`

## CLI Deploy

```bash
# Install
npm i -g @railway/cli

# Login
railway login

# Init
railway init

# Add DB
railway add plugin postgresql

# Deploy
railway up
```

## Notes

- Free tier: $5/month credit
- Sleeps after 5 min inactivity (paid plans stay awake)
- Auto-scaling available on paid plans

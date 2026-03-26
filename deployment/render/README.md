# Render Deployment

## Quick Deploy

1. **Push code to GitHub**

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Create PostgreSQL**
   ```
   Dashboard → New → PostgreSQL
   Name: mugstore-db
   Plan: Free
   ```

4. **Create Web Service**
   ```
   Dashboard → New → Web Service
   Connect your GitHub repo
   Build Command: (leave empty)
   Start Command: (leave empty)
   ```

5. **Configure Variables**
   ```
   USE_SQLITE=false
   ALLOWED_ORIGINS=https://your-app.onrender.com
   ```
   Add database credentials from step 3:
   ```
   POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
   ```

6. **Deploy**

## Notes

- Free tier: 750 hours/month
- Sleeps after 15 min inactivity
- Paid plans: ~$7/month for always-on

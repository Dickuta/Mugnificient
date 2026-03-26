# Mugnificent Platform - Access Information

## 🌐 Service URLs & Credentials

### Main Application
- **Frontend**: http://localhost
- **API**: http://localhost/api/v1
- **API Documentation (Swagger)**: http://localhost/docs
- **API Documentation (ReDoc)**: http://localhost/redoc

### Database Management
- **pgAdmin**: http://localhost:5050
  - **Email**: admin@mugnificent.com
  - **Password**: Pg4dM1n8P2aS5sW7oR0dK3eY6jL9xQ2vB5nM8hJ1tG4pA7sD0fG3hJ6kL
  - **Database Connection**:
    - Host: postgres
    - Port: 5432
    - Database: mugnificent
    - Username: mugnificent
    - Password: Xk9mP2vL7nQ4wR8jT3yB6hD1sA5uF8iK2oN5pS7xZ3cV9bG4dH6jM8nL1qW

### Email Testing
- **Mailpit Web UI**: http://localhost:8025
- **SMTP Server**: localhost:1025 (no authentication required for testing)
- All emails sent by the application are captured here for testing

### Monitoring
- **Grafana**: http://localhost:3000
  - **Username**: admin
  - **Password**: G7r4A2f6N8a3D9m5I2n8P4aS7sW0oR3dK9eY2jL6xQ3vB8nM4hJ7tG1pA
  
- **Prometheus**: http://localhost:9090

### Storage
- **MinIO Console**: http://localhost:9001
  - **Username**: mugnificent-admin
  - **Password**: M5nI9oP2wS8eC3uR7eP4aS5sW9oR2dK5eY8jL0xQ4vB7nM3hJ6tG9pA2sD
- **MinIO S3 Endpoint**: http://localhost:9000

### Cache
- **Redis**: localhost:6379
  - **Password**: R7tY2uI5oP9wE4rT1yU8iO3pA5sD2fG6hJ8kL0zX3cV7bN4mQ9wE6rT2yU

## 🔧 Quick Commands

### Start Application
```bash
cd /Users/admin/workspaces/_active-projects/Mugnificient
bash scripts/start.sh
```

### Stop Application
```bash
cd /Users/admin/workspaces/_active-projects/Mugnificient
bash scripts/stop.sh
```

### View Logs
```bash
# All services
docker-compose -f deployment/docker/docker-compose.yml logs -f

# Specific service
docker-compose -f deployment/docker/docker-compose.yml logs -f app
docker-compose -f deployment/docker/docker-compose.yml logs -f mailpit
docker-compose -f deployment/docker/docker-compose.yml logs -f pgadmin
```

### Access Database via pgAdmin
1. Open http://localhost:5050
2. Login with credentials above
3. Right-click "Servers" → "Register" → "Server"
4. Name: Mugnificent DB
5. Connection tab:
   - Host name: postgres
   - Port: 5432
   - Maintenance database: mugnificent
   - Username: mugnificent
   - Password: (see Database credentials above)

### View Emails in Mailpit
1. Open http://localhost:8025
2. All sent emails appear automatically
3. Click on any email to view content
4. Useful for testing password resets, order confirmations, etc.

## 🔐 Security Notes

- ⚠️ **NEVER** commit the `.env` file to version control
- ⚠️ Change all default passwords before production deployment
- ⚠️ Keep pgAdmin and Mailpit behind authentication/firewall in production
- ⚠️ These credentials are for development/testing only

## 📊 Service Health

Check service health:
```bash
docker-compose -f deployment/docker/docker-compose.yml ps
```

All services should show "healthy" status.

## 🆘 Troubleshooting

### Service not starting
```bash
# Restart specific service
docker-compose -f deployment/docker/docker-compose.yml restart <service-name>

# View logs
docker-compose -f deployment/docker/docker-compose.yml logs <service-name>
```

### Database connection issues
1. Check PostgreSQL is running: `docker ps | grep mugstore-db`
2. Check credentials in `.env` file
3. Try connecting via pgAdmin

### Email not appearing in Mailpit
1. Check Mailpit is running: `docker ps | grep mailpit`
2. Verify EMAIL_HOST=mailpit in .env
3. Check application logs for email errors

---

**Generated**: 2026-03-26  
**Platform Version**: 1.0.0
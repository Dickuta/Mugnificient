# Deployment Guide - University of Suffolk Mug Shop

## Deployment Recommendation for University Use

Based on the University of Suffolk's specific requirements (part-time staff, limited IT resources, predictable academic calendar patterns), we recommend **Docker Compose** as the optimal deployment solution. This approach provides simplicity, reliability, and appropriate scale for a university shop environment.

**Kubernetes is out of scope for this project** - the complexity of K8s is unnecessary given the requirements and would increase maintenance burden on already limited university IT resources.

### Why Docker Compose for Universities:
- **Simplicity**: Single YAML file orchestration, easy to understand and maintain
- **Low IT Overhead**: Minimal ongoing maintenance required
- **Cost Effective**: Runs on affordable VPS hardware (no cloud vendor dependencies)
- **Reliable**: Battle-tested container orchestration technology
- **Appropriate Scale**: Perfect for university shop usage patterns
- **University Control**: Self-hosted with data sovereignty

## Deployment Options

### 1. Docker Compose (Recommended for University)
- **Best for**: Self-hosted, university infrastructure
- **Difficulty**: Medium (requires basic Linux/SSH skills)
- **Maintenance**: Low after initial setup
- **Hardware**: VPS with 4GB+ RAM (or dedicated server)
- **[Setup Instructions](./docker/README.md)**

### 2. Railway (Alternative Cloud Option)
- **Best for**: Universities without server infrastructure
- **Difficulty**: Easy (click-deploy)
- **Maintenance**: Very low (managed by provider)
- **Cost**: $5/month credit on free tier
- **[Setup Instructions](./railway/README.md)**

### 3. Render (Backup Cloud Option)
- **Best for**: Simple cloud deployment when Railway unavailable
- **Difficulty**: Easy (click-deploy)
- **Maintenance**: Very low (managed by provider)
- **Cost**: 750 hours/month free tier
- **[Setup Instructions](./render/README.md)**

## Out of Scope

### Kubernetes Deployment (Not Recommended)
Kubernetes is specifically out of scope for this project because:
- **Unnecessary Complexity**: University IT staff don't need K8s expertise
- **Over-Engineering**: Simple application doesn't require enterprise orchestration
- **Increased Maintenance**: More complex monitoring and troubleshooting
- **Higher Costs**: More expensive than necessary for university scale
- **Learning Curve**: Would require training for university IT staff

While the k8s folder exists for potential future scaling, it's not recommended for the current scope.

## Quick Comparison (In Scope Options)

| Provider | Free Tier | Difficulty | Best For |
|----------|-----------|------------|----------|
| Docker Compose | Free | Medium | University self-hosting |
| Railway | $5 credit | Easy | Cloud deployment |
| Render | 750h/month | Easy | Simple cloud apps |

## University-Specific Setup

### For Docker Compose (On-Premise/University Server)
```bash
# Navigate to the deployment directory
cd deployment/docker

# Configure environment variables
cp .env.production.example .env
# Edit .env with your university settings:
# - UNIVERSITY_EMAIL_DOMAIN (e.g., @uos.ac.uk)
# - SEMESTER_DATES (academic calendar integration)
# - ADMIN_USER for initial setup

# Start the application
docker-compose up -d

# Initial setup
docker-compose exec backend alembic upgrade head

# Create university admin account
docker-compose exec backend python -c "
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.models import User, Role

db = SessionLocal()

# Create admin user
admin_user = User(
    username='university-admin',
    email='admin@uos.ac.uk',
    hashed_password=get_password_hash('SecurePassword123!'),
    first_name='University',
    last_name='Administrator',
    is_active=True,
    is_staff=True,
    is_superuser=True
)
db.add(admin_user)
db.commit()
db.refresh(admin_user)
db.close()
"
```

### Post-Setup University Configuration
1. Access the application at your server URL
2. Log in with admin credentials
3. Configure academic calendar patterns (semester start/end dates)
4. Set up auto-ordering thresholds based on historical university patterns
5. Configure email notifications to relevant university staff
6. Train operational staff on the forecasting dashboard

### Security for University Data
- **Data Sovereignty**: Hosted on university infrastructure
- **Access Control**: Role-based permissions for different staff levels
- **Audit Trail**: All actions logged for compliance
- **Backups**: Regular database backups to university standards

## Common Setup (All Methods)

Regardless of deployment method, you'll need:

1. **Environment Variables**
   ```bash
   # Copy template
   cp .env.production .env
   
   # Key university-specific values:
   - UNIVERSITY_NAME="University of Suffolk"
   - UNIVERSITY_EMAIL_DOMAIN="uos.ac.uk"
   - ADMIN_EMAIL="admin@uos.ac.uk"
   - SEMESTER_START_DATES=["2023-09-15", "2024-01-15"] # Academic calendar
   - ACADEMIC_HOLIDAYS=[] # University holidays that affect demand
   ```

2. **Database Setup**  
   ```bash
   # Only needed once after deployment
   docker-compose exec backend alembic upgrade head
   ```

3. **University-Specific Configuration**
   - Upload university logo and branding
   - Configure seasonal patterns to match academic calendar
   - Set up notification contacts for university staff
   - Configure auto-ordering thresholds based on university patterns

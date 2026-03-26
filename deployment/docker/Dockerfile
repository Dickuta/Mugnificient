# Production stage
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists

# Copy backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy pre-built frontend
COPY frontend/dist/spa /var/www/html

# Configure nginx
RUN echo "server { \
    listen 80; \
    server_name localhost; \
    root /var/www/html; \
    index index.html; \
    location / { \
        try_files \$uri \$uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_set_header Host \$host; \
        proxy_set_header X-Real-IP \$remote_addr; \
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto \$scheme; \
    } \
    location /docs { \
        proxy_pass http://127.0.0.1:8000; \
    } \
    location /redoc { \
        proxy_pass http://127.0.0.1:8000; \
    } \
}" > /etc/nginx/sites-available/default

RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

RUN mkdir -p /app/images

ENV PYTHONUNBUFFERED=1
ENV USE_SQLITE=false

EXPOSE 80

# Start nginx and uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & nginx -g 'daemon off;'"]

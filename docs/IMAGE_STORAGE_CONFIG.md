# Image Storage Configuration

## Overview
The application supports two image storage options:
1. **Local Storage**: Images served from the backend server
2. **MinIO Storage**: Images served from MinIO object storage

## Configuration

### Environment Variables

#### Backend (.env)
```bash
# Image Storage Configuration
IMAGE_STORAGE_TYPE=local          # Options: 'local' or 'minio'
IMAGE_STORAGE_URL=http://localhost:9000/mugnificent
LOCAL_IMAGES_URL=/images/products
```

#### Frontend (.env)
```bash
# Image Storage Configuration
VITE_IMAGE_STORAGE_TYPE=local     # Options: 'local' or 'minio'
VITE_IMAGE_STORAGE_URL=http://localhost:9000/mugnificent
```

## Setup Options

### Option 1: Local Storage (Simple)

**Best for**: Development, small deployments

1. **Set configuration**:
   ```bash
   # Frontend .env
   VITE_IMAGE_STORAGE_TYPE=local
   
   # Backend .env
   IMAGE_STORAGE_TYPE=local
   ```

2. **Store images in backend**:
   ```
   backend/app/images/products/
   ├── classic-white-mug.jpeg
   ├── black-matte-mug.jpeg
   └── ...
   ```

3. **Update database**:
   ```sql
   UPDATE products SET image = '/images/products/classic-white-mug.jpeg';
   ```

### Option 2: MinIO Storage (Scalable)

**Best for**: Production, large deployments

1. **Set configuration**:
   ```bash
   # Frontend .env
   VITE_IMAGE_STORAGE_TYPE=minio
   VITE_IMAGE_STORAGE_URL=http://localhost:9000/mugnificent
   
   # Backend .env
   IMAGE_STORAGE_TYPE=minio
   IMAGE_STORAGE_URL=http://localhost:9000/mugnificent
   ```

2. **Upload images to MinIO**:
   ```bash
   docker exec mugstore-minio mc cp /path/to/images/*.jpeg mugstore/mugnificent/products/
   docker exec mugstore-minio mc anonymous set public mugstore/mugnificent/products
   ```

3. **Update database**:
   ```sql
   UPDATE products SET image = '/products/classic-white-mug.jpeg';
   ```

## Switching Between Storage

### From Local to MinIO:
1. Update `.env` files to use `minio`
2. Upload images to MinIO
3. Rebuild frontend: `npm run build`
4. Restart app: `docker-compose up -d --build`

### From MinIO to Local:
1. Update `.env` files to use `local`
2. Copy images to backend: `docker cp images/ mugstore-app:/app/app/images/`
3. Rebuild frontend: `npm run build`
4. Restart app: `docker-compose up -d --build`

## Testing

### Check Current Configuration:
```bash
# Frontend
grep VITE_IMAGE_STORAGE frontend/.env

# Backend
grep IMAGE_STORAGE deployment/docker/.env
```

### Verify Images Load:
1. Open browser to http://localhost
2. Check product images display correctly
3. Open DevTools Network tab
4. Verify image URLs match configured storage

## Troubleshooting

### Images Not Loading:
1. Check storage type in `.env`
2. Verify images exist in storage location
3. Check browser console for 404 errors
4. Verify database image paths

### MinIO Access Issues:
1. Check MinIO is running: `docker ps | grep minio`
2. Verify bucket exists: `docker exec mugstore-minio mc ls mugstore`
3. Check bucket is public: `docker exec mugstore-minio mc anonymous get mugstore/mugnificent`
4. Test direct access: `curl http://localhost:9000/mugnificent/products/test.jpeg`

## Default Configuration

By default, the application uses **local storage** for simplicity. To use MinIO, update the configuration as shown above.

# Deployment Guide

## Overview

This guide covers deploying the Visual Noise Museum to production environments.

## Prerequisites

- Docker & Docker Compose
- PostgreSQL 16+ with pgvector extension
- Redis 7+
- SSL certificates (for HTTPS)
- Domain name (optional)

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://host:6379/0
REDIS_CACHE_TTL=3600

# Security
SECRET_KEY=<generate-secure-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["https://yourdomain.com"]

# Rate Limiting
RATE_LIMIT_ANONYMOUS=100/minute
RATE_LIMIT_AUTHENTICATED=1000/minute

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Optional: Sentry
SENTRY_DSN=https://...
```

### Frontend (.env.production)

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
NEXT_PUBLIC_ENABLE_OFFLINE=true
NEXT_PUBLIC_ENABLE_WEBGPU=true
```

## Deployment Options

### Option 1: Vercel + Railway (Recommended)

#### Frontend on Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod

# Configure environment variables in Vercel dashboard
```

#### Backend on Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Create new project
railway init

# Add PostgreSQL and Redis
railway add --plugin postgresql
railway add --plugin redis

# Deploy
cd backend
railway up

# Set environment variables
railway variables set SECRET_KEY=...
```

### Option 2: Docker on VPS

#### Server Requirements
- 2+ CPU cores
- 4+ GB RAM
- 50+ GB SSD
- Ubuntu 22.04 LTS or similar

#### Setup Steps

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Clone repository
git clone <your-repo>
cd noise

# 5. Configure environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.production
# Edit .env files with production values

# 6. Start services
docker-compose -f docker-compose.prod.yml up -d

# 7. Run migrations
docker-compose exec backend alembic upgrade head

# 8. Setup Nginx reverse proxy (see below)
```

### Option 3: Kubernetes

```yaml
# Example k8s deployment (simplified)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: noise-museum-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/noise-museum-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## Nginx Configuration

```nginx
# Frontend
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /api/v1/sessions/ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

## SSL/HTTPS with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificates
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

## Database Setup

### PostgreSQL with pgvector

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE noise_museum;

# Enable pgvector extension
\c noise_museum
CREATE EXTENSION vector;

# Create user (if needed)
CREATE USER noise_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE noise_museum TO noise_user;
```

### Run Migrations

```bash
# Docker
docker-compose exec backend alembic upgrade head

# Manual
cd backend
alembic upgrade head
```

## Monitoring

### Log Management

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Save logs to file
docker-compose logs backend > backend.log
```

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Backend readiness
curl https://api.yourdomain.com/readiness

# Frontend
curl https://yourdomain.com
```

### Performance Monitoring

Consider setting up:
- **Sentry** for error tracking
- **Prometheus** for metrics
- **Grafana** for dashboards
- **New Relic** or **DataDog** for APM

## Backup Strategy

### Database Backups

```bash
# Automated daily backups
0 2 * * * docker exec noise-museum-db pg_dump -U postgres noise_museum | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz

# Keep 30 days
find /backups -name "db-*.sql.gz" -mtime +30 -delete
```

### Restore from Backup

```bash
# Decompress and restore
gunzip < backup.sql.gz | docker exec -i noise-museum-db psql -U postgres noise_museum
```

## Scaling

### Horizontal Scaling (Backend)

```bash
# Scale backend service
docker-compose up -d --scale backend=3

# Configure load balancer (Nginx/HAProxy)
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

### Database Read Replicas

```sql
-- Configure PostgreSQL streaming replication
-- See PostgreSQL documentation for details
```

### CDN for Frontend

- Use Vercel Edge Network (automatic)
- Or configure CloudFlare
- Or use AWS CloudFront

## Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Set secure SECRET_KEY
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up firewall (UFW)
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor logs for anomalies
- [ ] Use strong passwords
- [ ] Enable 2FA for admin accounts

## Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL

# Test connection
docker-compose exec backend psql $DATABASE_URL
```

#### Redis Connection Failed
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
```

#### WebSocket Not Working
- Check Nginx WebSocket configuration
- Ensure `proxy_http_version 1.1`
- Check firewall rules

#### High Memory Usage
- Check Docker container stats: `docker stats`
- Adjust connection pool sizes
- Enable query logging to find slow queries

## Rollback Procedure

```bash
# 1. Stop current deployment
docker-compose down

# 2. Checkout previous version
git checkout <previous-commit>

# 3. Rebuild and start
docker-compose up -d --build

# 4. Rollback database migration (if needed)
docker-compose exec backend alembic downgrade -1
```

## Maintenance

### Regular Tasks

- **Daily**: Monitor logs and metrics
- **Weekly**: Review error rates, check disk space
- **Monthly**: Update dependencies, security patches
- **Quarterly**: Performance audit, capacity planning

### Updates

```bash
# Update codebase
git pull origin main

# Rebuild containers
docker-compose build

# Restart with zero downtime
docker-compose up -d --no-deps backend

# Run migrations
docker-compose exec backend alembic upgrade head
```

## Support

For deployment issues:
- Check documentation
- Review logs
- Open GitHub issue
- Contact support team

# Deployment Guide - PDF Processing API

## 🚀 Quick Deployment

### Option 1: Docker Deployment (Recommended)

1. **Prerequisites:**
   ```bash
   # Ensure Docker and Docker Compose are installed
   docker --version
   docker-compose --version
   ```

2. **Deploy:**
   ```bash
   cd /Users/dev/Documents/test_assessment
   ./scripts/deploy.sh
   ```

3. **Verify:**
   ```bash
   curl http://localhost:8000/health
   ```

### Option 2: Local Development

1. **Setup:**
   ```bash
   cd /Users/dev/Documents/test_assessment
   ./scripts/start.sh
   ```

2. **Test:**
   ```bash
   ./scripts/test.sh
   ```

## 🔧 Configuration

### Environment Setup

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Update configuration:**
   ```bash
   # Edit .env with your specific settings
   nano .env
   ```

### Key Configuration Options

```env
# Security (IMPORTANT: Change in production)
SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/pdf_processing

# File Processing
MAX_FILE_SIZE=10485760  # 10MB
BATCH_SIZE=10

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## 📋 Production Checklist

### Security
- [ ] Change default `SECRET_KEY`
- [ ] Update default user passwords
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up proper CORS origins
- [ ] Enable security headers

### Performance
- [ ] Configure database connection pooling
- [ ] Set up Redis for caching
- [ ] Configure file storage (cloud storage for production)
- [ ] Set appropriate resource limits

### Monitoring
- [ ] Set up health check monitoring
- [ ] Configure log aggregation
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Monitor resource usage

### Infrastructure
- [ ] Configure load balancer
- [ ] Set up database backups
- [ ] Configure auto-scaling
- [ ] Set up CI/CD pipeline

## 🐳 Docker Services

The deployment includes:

- **API Service** (Port 8000): FastAPI application
- **Database** (Port 5432): PostgreSQL database
- **Cache** (Port 6379): Redis for caching
- **Proxy** (Port 80/443): Nginx reverse proxy

### Service Management

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Restart a service
docker-compose restart api

# Stop all services
docker-compose down

# Update and restart
docker-compose down && docker-compose up -d --build
```

## 🔍 Health Checks

### API Health
```bash
curl http://localhost:8000/health
```

### Service Health
```bash
curl http://localhost:8000/api/v1/pdf/health
```

### Database Connection
```bash
# Check if database is accessible
docker-compose exec db psql -U postgres -d pdf_processing -c "SELECT 1;"
```

## 📊 Monitoring

### Application Metrics

The API provides built-in monitoring endpoints:

- `/health` - General health check
- `/api/v1/pdf/health` - PDF service health
- `/api/v1/pdf/stats` - Processing statistics (admin only)

### Log Locations

```bash
# Application logs
docker-compose logs api

# Database logs  
docker-compose logs db

# Nginx logs
docker-compose logs nginx
```

## 🔧 Troubleshooting

### Common Issues

1. **Port Conflicts:**
   ```bash
   # Check which process is using the port
   lsof -i :8000
   
   # Kill the process if needed
   kill -9 <PID>
   ```

2. **Docker Permission Issues:**
   ```bash
   # Add user to docker group (Linux)
   sudo usermod -aG docker $USER
   
   # Restart docker service
   sudo systemctl restart docker
   ```

3. **Database Connection Issues:**
   ```bash
   # Check database logs
   docker-compose logs db
   
   # Restart database
   docker-compose restart db
   ```

4. **File Upload Issues:**
   ```bash
   # Check upload directory permissions
   ls -la uploads/
   
   # Create uploads directory if missing
   mkdir -p uploads
   ```

### Debug Mode

Enable debug mode for development:

```env
DEBUG=true
ENVIRONMENT=development
```

### Performance Issues

1. **High Memory Usage:**
   - Reduce `MAX_CONCURRENT_TASKS`
   - Implement file streaming for large files
   - Add memory monitoring

2. **Slow Processing:**
   - Check PDF file sizes
   - Monitor CPU usage
   - Consider horizontal scaling

## 🔄 Updates and Maintenance

### Application Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Database Migrations

```bash
# Run migrations (when using Alembic)
docker-compose exec api alembic upgrade head
```

### Backup and Restore

```bash
# Backup database
docker-compose exec db pg_dump -U postgres pdf_processing > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres pdf_processing < backup.sql
```

## 🌐 Production Deployment

### Cloud Deployment Options

1. **AWS:**
   - ECS/Fargate for containers
   - RDS for PostgreSQL
   - ElastiCache for Redis
   - S3 for file storage

2. **Google Cloud:**
   - Cloud Run for containers
   - Cloud SQL for PostgreSQL
   - Memorystore for Redis
   - Cloud Storage for files

3. **Azure:**
   - Container Instances
   - Azure Database for PostgreSQL
   - Azure Cache for Redis
   - Blob Storage for files

### Load Balancer Configuration

Example Nginx configuration for multiple API instances:

```nginx
upstream api_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    location /api/ {
        proxy_pass http://api_backend;
        # ... other proxy settings
    }
}
```

## 📞 Support

For deployment issues:

1. Check the logs first
2. Verify configuration settings
3. Ensure all prerequisites are met
4. Check resource availability (disk space, memory)

---

**Happy Deploying!** 🚀

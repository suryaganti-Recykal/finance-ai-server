# Docker Setup Guide

Run the entire Finance AI stack (backend + frontend) with Docker and Docker Compose.

## Prerequisites

- Docker 20.10+
- Docker Compose 1.29+

## Quick Start

### 1. Start All Services

```bash
# From project root
docker-compose up --build

# Or in background
docker-compose up -d --build
```

### 2. Access Applications

- **Frontend (Dashboard)**: http://localhost:3000
- **Backend (API)**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### 3. Stop Services

```bash
docker-compose down

# Remove volumes (data)
docker-compose down -v
```

## Individual Services

### Backend Only

```bash
docker-compose up backend

# Or build and run directly
docker build -t finance-ai-backend ./app
docker run -p 8000:8000 \
  -e USE_SHEETS_FOR_DEMO=true \
  -e DATABASE_URL=sqlite+aiosqlite:///./finance_ai.db \
  finance-ai-backend
```

### Frontend Only

```bash
docker-compose up frontend

# Or build and run directly
docker build -t finance-ai-frontend ./frontend
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
  finance-ai-frontend
```

## Environment Variables

### Backend (.env in app/)

```env
ENVIRONMENT=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=sqlite+aiosqlite:///./finance_ai.db
USE_SHEETS_FOR_DEMO=true
LOG_LEVEL=INFO
```

### Frontend (.env.local in frontend/)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Docker Compose Services

### Backend Service

- **Image**: Built from `./app/Dockerfile`
- **Port**: 8000
- **Health Check**: GET /api/v1/health every 10s
- **Auto Reload**: Enabled with `-e PYTHONUNBUFFERED=1`
- **Volumes**: Source code mounted for development

### Frontend Service

- **Image**: Built from `./frontend/Dockerfile` (multi-stage build)
- **Port**: 3000
- **Depends On**: Backend service
- **Optimized**: Production build in final stage

## Development Workflow

### With Live Reloading

```bash
# Terminal 1: Start Docker services
docker-compose up

# Services automatically reload on code changes
# Backend: uvicorn --reload
# Frontend: Next.js hot module replacement
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Follow without timestamp
docker-compose logs --no-log-prefix -f
```

### Run Commands Inside Container

```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# Run Python command
docker-compose exec backend python -c "import src; print('OK')"
```

## Production Deployment

### Build Production Images

```bash
# Build images
docker build -t finance-ai-backend:1.0.0 ./app
docker build -t finance-ai-frontend:1.0.0 ./frontend

# Tag for registry
docker tag finance-ai-backend:1.0.0 youregistry/finance-ai-backend:1.0.0
docker tag finance-ai-frontend:1.0.0 youregistry/finance-ai-frontend:1.0.0

# Push to registry
docker push youregistry/finance-ai-backend:1.0.0
docker push youregistry/finance-ai-frontend:1.0.0
```

### Environment Variables for Production

```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - DATABASE_URL=postgresql://user:pass@db:5432/finance_ai
      - SECRET_KEY=${SECRET_KEY}
      - CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
      # ... add your production secrets
```

### Run Production Stack

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Port Already in Use

```bash
# Change ports in docker-compose.yml
services:
  backend:
    ports:
      - "8001:8000"  # Expose as 8001
  frontend:
    ports:
      - "3001:3000"  # Expose as 3001
```

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Rebuild from scratch
docker-compose down --rmi all
docker-compose up --build
```

### CORS Errors

```bash
# Verify API URL is correct in frontend
NEXT_PUBLIC_API_URL=http://backend:8000/api/v1

# Or use service name instead of localhost (inside Docker network)
# For external access, use localhost:8000
```

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up --build
```

## Network

- **Network Name**: `finance-ai-network` (bridge)
- **Backend Service**: Accessible as `backend` from other services
- **Frontend Service**: Accessible as `frontend` from other services
- **From Host**: Use `localhost:8000` and `localhost:3000`

## Performance Tips

1. **Layer Caching**: Dockerfile instructions are ordered for better caching
2. **Multi-Stage Build**: Frontend uses multi-stage build to reduce image size
3. **Volume Mounts**: Only needed files are copied to production images
4. **Health Checks**: Ensure services are healthy before routing traffic

## Security

For production:

1. Use environment files (`.env`) for secrets
2. Never commit `.env` to git
3. Use strong `SECRET_KEY` values
4. Enable HTTPS with reverse proxy (nginx)
5. Use health checks before load balancing
6. Limit container resources

```yaml
# Add resource limits
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Monitoring

### Check Health

```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Frontend health
curl http://localhost:3000

# Container stats
docker stats finance-ai-backend finance-ai-frontend
```

## Documentation

- **Backend**: See `README.md` in app/ folder
- **Frontend**: See `frontend/README.md`
- **API**: http://localhost:8000/docs (Swagger UI)

# Deployment Guide

This guide covers deploying LinkedIn AI Agent to various environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Checklist](#production-checklist)

---

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL (optional)
- Redis (optional)

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/linkedin-ai-agent.git
cd linkedin-ai-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Running

```bash
# Run CLI
python -m src.cli.main

# Run API (development)
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Docker Deployment

### Single Container

```bash
# Build image
docker build -t linkedin-ai-agent .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e DATABASE_URL=your_db_url \
  linkedin-ai-agent
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Services Included

| Service | Port | Description |
|---------|------|-------------|
| app | 8000 | API server |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache |

---

## Cloud Deployment

### Railway

1. Connect GitHub repository
2. Add environment variables:
   - `GEMINI_API_KEY`
   - `DATABASE_URL` (provided by Railway)
   - `REDIS_URL` (add Redis plugin)
3. Deploy

### Render

```yaml
# render.yaml
services:
  - type: web
    name: linkedin-ai-agent
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false
```

### AWS (ECS)

```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URL
docker build -t linkedin-ai-agent .
docker tag linkedin-ai-agent:latest $ECR_URL/linkedin-ai-agent:latest
docker push $ECR_URL/linkedin-ai-agent:latest

# Deploy to ECS
aws ecs update-service --cluster my-cluster --service linkedin-ai-agent --force-new-deployment
```

### GCP (Cloud Run)

```bash
# Build with Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/linkedin-ai-agent

# Deploy to Cloud Run
gcloud run deploy linkedin-ai-agent \
  --image gcr.io/PROJECT_ID/linkedin-ai-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key
```

---

## Production Checklist

### Security

- [ ] Set strong `SECRET_KEY`
- [ ] Configure CORS origins (not `*`)
- [ ] Enable HTTPS
- [ ] Set up API key authentication
- [ ] Review rate limiting settings

### Performance

- [ ] Use production ASGI server (Gunicorn + Uvicorn)
- [ ] Configure connection pooling
- [ ] Set up Redis for caching
- [ ] Enable response compression

### Monitoring

- [ ] Set up health check endpoints
- [ ] Configure logging (structured JSON)
- [ ] Add APM (Datadog, New Relic, etc.)
- [ ] Set up alerts for errors

### Database

- [ ] Run migrations: `alembic upgrade head`
- [ ] Set up backups
- [ ] Configure connection limits

### Example Production Command

```bash
gunicorn src.api.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Google AI Studio API key |
| `DATABASE_URL` | No | SQLite | PostgreSQL connection string |
| `REDIS_URL` | No | In-memory | Redis connection string |
| `SECRET_KEY` | No | Generated | Application secret key |
| `DEBUG` | No | false | Enable debug mode |
| `LOG_LEVEL` | No | INFO | Logging level |

---

## Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify connection string format
postgresql://user:password@host:5432/database
```

**Redis Connection Failed**
```bash
# Check Redis is running
redis-cli ping

# Verify connection string
redis://localhost:6379
```

**Rate Limit Hit**
- Default: 30 requests/minute
- Adjust in `src/api/main.py`:
  ```python
  app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
  ```

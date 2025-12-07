# MCP Web Application - Deployment Guide

This guide covers deploying the MCP Web Application to various environments, from local development to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Environment Configuration](#environment-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Scaling](#scaling)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Software Requirements

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| Python | 3.11+ | Runtime environment |
| Docker | 20.10+ | Containerization |
| Docker Compose | 2.0+ | Multi-container orchestration |
| Git | 2.30+ | Source control |

### System Requirements

**Development:**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 2 GB free

**Production:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 10 GB free

## Local Development

### Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-username/mcp-web-app.git
   cd mcp-web-app
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   cd 04-app-integration/simple-webapp
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   # Copy example environment file
   cp config/.env.example config/.env

   # Edit .env file with your settings
   # MCP_EXEC_PATH should point to your Python and file_server.py
   ```

5. **Run Application**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. **Verify**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/mcp/health

### Development Workflow

```bash
# Terminal 1: Run application
uvicorn app.main:app --reload --port 8000

# Terminal 2: Run tests
pytest

# Terminal 3: Monitor logs
tail -f logs/app.log  # if logging to file
```

## Docker Deployment

### Quick Start

```powershell
# Build and run
.\06-deployment\build-and-run.ps1

# Run tests
.\06-deployment\test-docker.ps1
```

### Manual Docker Commands

**Build Image:**
```bash
docker build -t mcp-webapp:latest -f 06-deployment/Dockerfile .
```

**Run Container:**
```bash
docker run -d \
  --name mcp-webapp \
  -p 8000:8000 \
  -e MCP_TIMEOUT_DEFAULT=15 \
  -v $(pwd)/05-build-server/test_samples:/app/test_samples:ro \
  mcp-webapp:latest
```

**View Logs:**
```bash
docker logs -f mcp-webapp
```

**Stop Container:**
```bash
docker stop mcp-webapp
docker rm mcp-webapp
```

### Docker Compose

**Start Services:**
```bash
docker-compose -f 06-deployment/docker-compose.yml up -d
```

**Scale Services:**
```bash
docker-compose -f 06-deployment/docker-compose.yml up -d --scale mcp-webapp=3
```

**View Logs:**
```bash
docker-compose -f 06-deployment/docker-compose.yml logs -f
```

**Stop Services:**
```bash
docker-compose -f 06-deployment/docker-compose.yml down
```

## Production Deployment

### Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
┌──────▼────────────────────────┐
│  Reverse Proxy (nginx/Traefik)│
│  - TLS Termination             │
│  - Load Balancing              │
│  - Rate Limiting               │
└──────┬────────────────────────┘
       │
┌──────▼──────────────────────┐
│   MCP Web App (Containers)  │
│   - Auto-scaling            │
│   - Health Checks           │
│   - Resource Limits         │
└──────┬──────────────────────┘
       │
┌──────▼──────────────────────┐
│   Monitoring & Logging      │
│   - Prometheus              │
│   - Grafana                 │
│   - ELK Stack               │
└─────────────────────────────┘
```

### Pre-deployment Checklist

#### Security
- [ ] Secrets stored in secure vault (not in code)
- [ ] TLS/HTTPS configured
- [ ] Authentication/authorization implemented
- [ ] CORS configured appropriately
- [ ] Rate limiting enabled
- [ ] Input validation comprehensive
- [ ] Security headers configured

#### Performance
- [ ] Resource limits set (CPU, Memory)
- [ ] Health checks configured
- [ ] Timeout values tuned
- [ ] Caching strategy implemented
- [ ] Database connections pooled

#### Reliability
- [ ] Auto-restart on failure
- [ ] Graceful shutdown implemented
- [ ] Backup strategy defined
- [ ] Disaster recovery plan
- [ ] Monitoring and alerting setup

#### Compliance
- [ ] Data privacy requirements met
- [ ] Logging compliant (no PII in logs)
- [ ] Audit trail implemented
- [ ] License compliance verified

### Docker Production Configuration

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  mcp-webapp:
    image: mcp-webapp:${VERSION:-latest}
    restart: always
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
    environment:
      - MCP_MODE=stdio
      - MCP_TIMEOUT_DEFAULT=${MCP_TIMEOUT:-10}
      - PYTHONUNBUFFERED=1
    env_file:
      - .env.production
    secrets:
      - mcp_exec_path
    networks:
      - frontend
      - backend
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - mcp-webapp
    networks:
      - frontend

networks:
  frontend:
  backend:

secrets:
  mcp_exec_path:
    file: ./secrets/mcp_exec_path.txt
```

**Deploy:**
```bash
export VERSION=1.0.0
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-webapp
  labels:
    app: mcp-webapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-webapp
  template:
    metadata:
      labels:
        app: mcp-webapp
    spec:
      containers:
      - name: mcp-webapp
        image: mcp-webapp:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: MCP_MODE
          value: "stdio"
        - name: MCP_TIMEOUT_DEFAULT
          value: "10"
        envFrom:
        - secretRef:
            name: mcp-secrets
        resources:
          limits:
            cpu: "2"
            memory: "1Gi"
          requests:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /mcp/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /mcp/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: mcp-webapp-service
spec:
  selector:
    app: mcp-webapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## Environment Configuration

### Environment Variables

| Variable | Default | Production | Description |
|----------|---------|------------|-------------|
| `MCP_MODE` | `stdio` | `stdio` | MCP transport mode |
| `MCP_EXEC_PATH` | (path) | (secret) | MCP server executable path |
| `MCP_TIMEOUT_DEFAULT` | `10` | `15` | Default timeout (seconds) |
| `PYTHONUNBUFFERED` | `1` | `1` | Disable Python buffering |
| `LOG_LEVEL` | `INFO` | `WARNING` | Logging verbosity |
| `WORKERS` | `1` | `4` | Uvicorn worker count |

### Configuration Files

**Development (.env.development):**
```ini
MCP_MODE=stdio
MCP_EXEC_PATH=python c:\path\to\file_server.py
MCP_TIMEOUT_DEFAULT=10
LOG_LEVEL=DEBUG
```

**Production (.env.production):**
```ini
MCP_MODE=stdio
MCP_EXEC_PATH_FILE=/run/secrets/mcp_exec_path
MCP_TIMEOUT_DEFAULT=15
LOG_LEVEL=WARNING
WORKERS=4
```

### Secrets Management

**Docker Secrets:**
```bash
# Create secret
echo "python /app/servers/file_server.py" | docker secret create mcp_exec_path -

# Use in compose
services:
  app:
    secrets:
      - mcp_exec_path
```

**Kubernetes Secrets:**
```bash
# Create secret
kubectl create secret generic mcp-secrets \
  --from-literal=MCP_EXEC_PATH='python /app/servers/file_server.py'

# Use in deployment
envFrom:
- secretRef:
    name: mcp-secrets
```

## Monitoring & Logging

### Health Checks

**Endpoint:** `GET /mcp/health`

**Response:**
```json
{
  "status": "ok",
  "server_type": "stdio"
}
```

**Monitoring Script:**
```bash
#!/bin/bash
while true; do
  STATUS=$(curl -s http://localhost:8000/mcp/health | jq -r '.status')
  if [ "$STATUS" != "ok" ]; then
    echo "ALERT: Service unhealthy at $(date)"
    # Send alert
  fi
  sleep 30
done
```

### Logging

**Log Levels:**
- `DEBUG`: Development only
- `INFO`: Default
- `WARNING`: Production recommended
- `ERROR`: Critical issues only

**Log Format (JSON):**
```json
{
  "timestamp": "2025-12-07T10:30:00Z",
  "level": "INFO",
  "message": "Request processed",
  "tool": "read_file",
  "latency_ms": 12,
  "user_id": "user123"
}
```

**Centralized Logging (ELK Stack):**
```yaml
services:
  app:
    logging:
      driver: fluentd
      options:
        fluentd-address: localhost:24224
        tag: mcp-webapp
```

### Metrics

**Prometheus Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `mcp_tool_calls_total` - Total MCP tool calls
- `mcp_tool_errors_total` - MCP tool errors

**Example prometheus.yml:**
```yaml
scrape_configs:
  - job_name: 'mcp-webapp'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Alerting

**Alert Rules:**
```yaml
groups:
- name: mcp-webapp
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    annotations:
      summary: "High latency detected"
```

## Scaling

### Horizontal Scaling

**Docker Compose:**
```bash
docker-compose up -d --scale mcp-webapp=5
```

**Kubernetes:**
```bash
kubectl scale deployment mcp-webapp --replicas=5
```

**Auto-scaling (K8s):**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcp-webapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-webapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Load Balancing

**nginx.conf:**
```nginx
upstream mcp_backend {
    least_conn;
    server mcp-webapp-1:8000;
    server mcp-webapp-2:8000;
    server mcp-webapp-3:8000;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location / {
        proxy_pass http://mcp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

**Symptoms:**
- Container exits immediately
- Health check fails

**Diagnosis:**
```bash
docker logs mcp-webapp
docker inspect mcp-webapp
```

**Solutions:**
- Check environment variables
- Verify MCP_EXEC_PATH points to valid file
- Ensure sufficient resources allocated

#### 2. High Memory Usage

**Diagnosis:**
```bash
docker stats mcp-webapp
```

**Solutions:**
- Reduce worker count
- Set memory limits
- Check for memory leaks
- Enable garbage collection logging

#### 3. Slow Response Times

**Diagnosis:**
- Check `latency_ms` in responses
- Monitor CPU usage
- Review logs for bottlenecks

**Solutions:**
- Increase timeout values
- Scale horizontally
- Optimize MCP server code
- Add caching layer

#### 4. MCP Communication Failures

**Symptoms:**
- "EOF: Server closed connection"
- "Timeout" errors

**Diagnosis:**
```bash
# Check MCP server directly
python 05-build-server/file_server.py

# Test stdio communication
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python 05-build-server/file_server.py
```

**Solutions:**
- Verify encoding='utf-8' in subprocess.Popen
- Check MCP server doesn't use print()
- Increase timeout values
- Verify MCP_EXEC_PATH is correct

### Emergency Procedures

**Rollback:**
```bash
# Docker
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Kubernetes
kubectl rollout undo deployment/mcp-webapp
```

**Emergency Shutdown:**
```bash
docker-compose -f docker-compose.prod.yml down
```

**Data Backup:**
```bash
# Backup volumes
docker run --rm -v mcp_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data
```

## Maintenance

### Update Procedure

1. **Backup Current State**
   ```bash
   docker-compose -f docker-compose.prod.yml down
   docker save mcp-webapp:latest -o mcp-webapp-backup.tar
   ```

2. **Deploy New Version**
   ```bash
   export VERSION=1.1.0
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

3. **Verify Deployment**
   ```bash
   ./06-deployment/test-docker.ps1
   ```

4. **Monitor for Issues**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

### Regular Maintenance

**Weekly:**
- Review logs for errors
- Check disk usage
- Verify backups

**Monthly:**
- Update dependencies
- Review security advisories
- Performance testing
- Capacity planning

**Quarterly:**
- Disaster recovery drill
- Security audit
- Documentation review

## Support

For deployment issues:
1. Check logs first: `docker logs mcp-webapp`
2. Review this guide
3. Consult [TEAM_GUIDE.md](TEAM_GUIDE.md)
4. Open GitHub issue with logs and config (redacted)

---

**Last Updated**: 2025-12-07
**Version**: 1.0.0

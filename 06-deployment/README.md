# MCP Web Application - Docker Deployment

This directory contains Docker deployment files for the MCP (Model Context Protocol) Web Application.

## Overview

The MCP Web Application is containerized using Docker for easy deployment and consistent runtime environments across different systems.

### Architecture

```
┌─────────────────────────────────────┐
│   Docker Container (mcp-webapp)     │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  FastAPI App │  │ MCP Server  │ │
│  │  (Port 8000) │──│file_server  │ │
│  └──────────────┘  └─────────────┘ │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Test Samples (Volume)      │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Files

- **`Dockerfile`** - Multi-stage Docker image definition
- **`docker-compose.yml`** - Service orchestration configuration
- **`.dockerignore`** - Files excluded from Docker build context
- **`build-and-run.ps1`** - Automated build and run script (PowerShell)
- **`test-docker.ps1`** - Integration test script (PowerShell)
- **`README.md`** - This file

## Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher (included with Docker Desktop)
- **PowerShell**: For running build and test scripts (Windows)

### Installation

#### Windows
1. Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. Ensure WSL2 backend is enabled for better performance

#### Mac
1. Download and install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)

#### Linux
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Quick Start

### Option 1: Using PowerShell Script (Recommended)

```powershell
# Build and run the application
.\06-deployment\build-and-run.ps1
```

This script will:
1. Clean up existing containers
2. Build the Docker image
3. Start the container
4. Wait for the application to be ready
5. Run health checks

### Option 2: Using Docker Compose

```bash
# Navigate to project root
cd c:\AI_study\Projects\MCP\MCP_Basic_Higher_Models_GC

# Build and start
docker-compose -f 06-deployment/docker-compose.yml up -d

# View logs
docker-compose -f 06-deployment/docker-compose.yml logs -f

# Stop
docker-compose -f 06-deployment/docker-compose.yml down
```

### Option 3: Using Docker CLI

```bash
# Build image
docker build -t mcp-webapp:latest -f 06-deployment/Dockerfile .

# Run container
docker run -d \
  --name mcp-webapp \
  -p 8000:8000 \
  -v $(pwd)/05-build-server/test_samples:/app/test_samples:ro \
  mcp-webapp:latest

# View logs
docker logs -f mcp-webapp

# Stop and remove
docker stop mcp-webapp && docker rm mcp-webapp
```

## Testing

### Automated Tests

Run the integration test suite:

```powershell
.\06-deployment\test-docker.ps1
```

Tests include:
1. Health check
2. List tools
3. Read file
4. List files
5. List files with pattern filter
6. Error handling

### Manual Testing

#### Health Check
```bash
curl http://localhost:8000/mcp/health
```

#### API Documentation
Open in browser: http://localhost:8000/docs

#### List MCP Tools
```bash
curl http://localhost:8000/mcp/tools
```

#### Call a Tool
```bash
curl -X POST http://localhost:8000/mcp/actions/read_file \
  -H "Content-Type: application/json" \
  -d '{"params": {"path": "/app/test_samples/sample1.txt"}}'
```

## Configuration

### Environment Variables

The following environment variables can be configured in `docker-compose.yml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_MODE` | `stdio` | MCP transport mode |
| `MCP_EXEC_PATH` | `/home/mcpuser/.local/bin/python /app/servers/file_server.py` | Path to MCP server executable |
| `MCP_TIMEOUT_DEFAULT` | `10` | Default timeout in seconds |
| `PYTHONUNBUFFERED` | `1` | Disable Python output buffering |

### Volumes

- **Test Samples**: `../05-build-server/test_samples:/app/test_samples:ro`
  - Mounted read-only for demo purposes
  - Can be modified for custom file paths

### Ports

- **8000**: FastAPI web application port

### Health Check

The container includes a health check that runs every 30 seconds:
- **URL**: `http://localhost:8000/mcp/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

## Troubleshooting

### Container won't start

**Check logs:**
```bash
docker-compose -f 06-deployment/docker-compose.yml logs
```

**Common issues:**
1. Port 8000 already in use
   - Stop other services using port 8000
   - Or change port in `docker-compose.yml`

2. Build fails
   - Check Docker daemon is running
   - Ensure internet connection for package downloads

### Application returns errors

**Check container is healthy:**
```bash
docker ps
```

Look for `(healthy)` status.

**Restart container:**
```bash
docker-compose -f 06-deployment/docker-compose.yml restart
```

### Performance issues

**Check resource usage:**
```bash
docker stats mcp-webapp
```

**Allocate more resources:**
- Docker Desktop → Settings → Resources
- Increase CPU and Memory limits

## Security Considerations

### Production Deployment

For production use, consider:

1. **Environment Variables**: Use secrets management (e.g., Docker Secrets, Vault)
2. **Network**: Use reverse proxy (nginx, Traefik) with TLS
3. **User Permissions**: The container runs as non-root user `mcpuser` (UID 1000)
4. **Image Scanning**: Scan image for vulnerabilities before deployment
5. **Resource Limits**: Set memory and CPU limits in `docker-compose.yml`

### Example Production Configuration

```yaml
services:
  mcp-webapp:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    environment:
      - MCP_EXEC_PATH_FILE=/run/secrets/mcp_exec_path
    secrets:
      - mcp_exec_path
```

## Maintenance

### Updating the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f 06-deployment/docker-compose.yml up -d --build
```

### Cleaning Up

```bash
# Remove containers and networks
docker-compose -f 06-deployment/docker-compose.yml down

# Remove images
docker rmi mcp-webapp:latest

# Remove all unused Docker resources
docker system prune -a
```

### Backup

Important files to backup:
- Application code (Git repository)
- Environment configuration (`.env` files - **never commit to Git**)
- Custom test samples or data volumes

## Advanced Usage

### Multi-container Setup

To add additional MCP servers:

```yaml
services:
  mcp-webapp:
    # ... existing config

  custom-mcp-server:
    build: ./path/to/custom/server
    networks:
      - mcp-network
```

### Custom Build Args

Pass build arguments:

```bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t mcp-webapp:latest \
  -f 06-deployment/Dockerfile .
```

### Docker Compose Profiles

Use profiles for different environments:

```yaml
services:
  mcp-webapp:
    profiles: ["production"]
    # production config

  mcp-webapp-dev:
    profiles: ["development"]
    # development config
```

Run with profile:
```bash
docker-compose --profile production up -d
```

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MCP Specification](https://modelcontextprotocol.io/)

## Support

For issues or questions:
1. Check the logs first
2. Review this README
3. Consult the main project documentation in `07-release-share/`
4. Open an issue on the project repository

---

**Last Updated**: 2025-12-07
**Version**: 1.0.0

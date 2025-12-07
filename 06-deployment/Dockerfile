# Multi-stage Dockerfile for MCP Web Application
# Stage 1: Build stage - installs dependencies
# Stage 2: Runtime stage - runs the application

# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.11-slim AS builder

LABEL maintainer="MCP Learning Team"
LABEL description="Build stage for MCP Web Application"

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY 04-app-integration/simple-webapp/requirements.txt .

# Install Python dependencies to user directory
RUN pip install --user --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.11-slim

LABEL maintainer="MCP Learning Team"
LABEL description="MCP Web Application with FastAPI and custom MCP servers"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/mcpuser/.local

# Make sure scripts in .local are usable
ENV PATH=/home/mcpuser/.local/bin:$PATH

# Copy application code
COPY --chown=mcpuser:mcpuser 04-app-integration/simple-webapp/app ./app
COPY --chown=mcpuser:mcpuser 04-app-integration/simple-webapp/config ./config

# Copy MCP server
COPY --chown=mcpuser:mcpuser 05-build-server ./servers

# Copy test samples (for demo purposes)
COPY --chown=mcpuser:mcpuser 05-build-server/test_samples ./test_samples

# Expose port
EXPOSE 8000

# Switch to non-root user
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/mcp/health', timeout=5)"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    MCP_MODE=stdio \
    MCP_EXEC_PATH="/home/mcpuser/.local/bin/python /app/servers/file_server.py" \
    MCP_TIMEOUT_DEFAULT=10

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

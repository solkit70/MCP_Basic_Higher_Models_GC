# syntax=docker/dockerfile:1
# Base image for MCP study projects. Extended in M4+ when web app is added.
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps optionally (kept minimal for now)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy requirement files (may be empty/minimal in M2)
COPY 02-env-setup/requirements.txt /tmp/requirements.txt
COPY 02-env-setup/requirements-dev.txt /tmp/requirements-dev.txt

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt -r /tmp/requirements-dev.txt

# Copy project (later: target subdirs for webapp/server)
COPY . /app

# Default command placeholder; overridden in M4+ (uvicorn, etc.)
CMD ["python", "-V"]

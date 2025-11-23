# Use an official Python runtime as a parent image
FROM python:3.10-slim

LABEL org.opencontainers.image.source=https://github.com/PatrykIti/blender-ai-mcp

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* /app/

# Config poetry to not use virtualenvs (we are in docker)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application
COPY server /app/server

# Set environment variables
# For Docker -> Host communication on Mac/Windows, use host.docker.internal
# On Linux, use --network host or the host IP
ENV BLENDER_RPC_HOST=host.docker.internal
ENV BLENDER_RPC_PORT=8765
ENV PYTHONPATH=/app

# Run the server
CMD ["python", "-m", "server.main"]

# Root-level Dockerfile for Railway backend deployment
# Builds the FastAPI backend from the app/ subdirectory
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY app/pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application source
COPY app/src/ src/
COPY app/alembic/ alembic/
COPY app/alembic.ini .

# Expose port (Railway injects $PORT)
EXPOSE 8000

# Run application
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

# Run application
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}

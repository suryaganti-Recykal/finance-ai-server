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
COPY scripts/ scripts/
COPY alembic/ alembic/
COPY alembic.ini .

# Run application
CMD ["/bin/sh", "-c", "alembic upgrade head && python scripts/seed_demo_data.py && uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

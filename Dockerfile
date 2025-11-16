# Dictat Backend Dockerfile
# Multi-stage build for optimized production image

# TODO Phase 5:
# - Add security scanning
# - Implement healthcheck
# - Optimize layer caching
# - Add non-root user
# - Minimize image size

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user
RUN groupadd -r dictat && useradd -r -g dictat dictat

# Create directories for storage and logs
RUN mkdir -p /app/storage/audio /app/logs && \
    chown -R dictat:dictat /app

# Copy application code
COPY --chown=dictat:dictat app/ ./app/
COPY --chown=dictat:dictat alembic/ ./alembic/
COPY --chown=dictat:dictat alembic.ini ./

# Switch to non-root user
USER dictat

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

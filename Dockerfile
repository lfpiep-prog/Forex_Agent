# Forex Agent - Production Dockerfile
# ===================================
FROM python:3.11.8-slim

# Build metadata for tracking
ARG BUILD_DATE
ARG GIT_COMMIT
LABEL org.opencontainers.image.title="Forex Agent"
LABEL org.opencontainers.image.description="Automated Forex Trading Bot"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"

# Python configuration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Runtime configuration (can be overridden)
ENV SMOKE_MODE=false

WORKDIR /app

# Install system dependencies (gcc for some Python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user with specific UID/GID
RUN useradd -m -u 1001 appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Ensure data directories exist with correct permissions
RUN mkdir -p /app/logs && \
    touch /app/trade_journal.csv && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check - verifies Python can import main modules
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "from execution.config import config; print('healthy')" || exit 1

# Default entrypoint
CMD ["python", "execution/main_loop.py"]

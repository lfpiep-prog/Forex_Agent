FROM python:3.10-slim

# Keep Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turn off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies if needed (e.g. for ta-lib or build tools)
# RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user and switch to it
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Entrypoint
CMD ["python", "main_loop.py"]

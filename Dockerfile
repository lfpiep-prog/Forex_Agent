FROM python:3.11-slim

# Keep Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turn off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies if needed (e.g. for ta-lib or build tools)
RUN apt-get update && apt-get install -y gcc build-essential python3-dev libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN useradd -m appuser

# Copy application code
COPY . .

# Ensure trade_journal.csv exists and has correct permissions
RUN touch /app/trade_journal.csv && chown appuser:appuser /app/trade_journal.csv && chown -R appuser:appuser /app

USER appuser

# Entrypoint
CMD ["python", "execution/main_loop.py"]

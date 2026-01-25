# Forex Trading Agent 🤖

A robust, containerized Forex Trading Agent built with Python, Docker, and SQLite.

## Features
- **3-Layer Architecture**: Directives (SOPs) | Execution (Engine) | Orchestration
- **Strategy**: Customizable strategies (Default: SMA Cross)
- **Risk Management**: Configurable limits (Daily Loss, Max Drawdown)
- **Database**: Zero-config SQLite persistence (`trades.db`)
- **Deployment**: `docker-compose` ready

## 🚀 Quick Start

### 1. Requirements
- [Docker & Docker Compose](https://www.docker.com/products/docker-desktop/)

### 2. Configuration
Copy the template and fill in your API keys:
```bash
cp .env.example .env
```
Edit `.env` and add your:
- `IG_USERNAME`, `IG_PASSWORD`, `IG_API_KEY` (Broker)
- `BRAVE_API_KEY` (Sentiment Analysis)

> **Note:** No database configuration needed! It defaults to a local `trades.db` file.

### 3. Run the System
Build and start the services:
```bash
docker-compose up --build -d
```
- **Agent**: Runs the trading loop.
- **Macro Server**: Provides contextual market data.

### 4. Monitor
Check the logs to see the agent in action:
```bash
docker-compose logs -f agent
```

### 5. Verify Data
Trades are saved to `trades.db`. You can view them using any SQLite viewer or:
```bash
# Check trade count inside the container
docker-compose exec agent python -c "from core.database import SessionLocal, init_db; from core.models import TradeResult; init_db(); db=SessionLocal(); print(db.query(TradeResult).all()); db.close()"
```

### 6. System Health Check
Run the included script to verify container status, API health, and data persistence:
```bash
python check_system.py
```
```

## Development
To run tests:
```bash
pytest
```

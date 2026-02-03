# Forex Agent - Deployment Guide

Complete guide for deploying the Forex Trading Bot via GitHub + Docker.

## Prerequisites

- Docker + Docker Compose installed on server
- SSH access configured (key-based authentication recommended)
- Git repository cloned: `git clone <repo-url> ~/Forex_Agent`
- `.env` file configured with credentials (copy from `.env.example`)

---

## Quick Deploy (Standard)

```bash
# 1. From local machine: push changes
git add . && git commit -m "feat: your changes" && git push origin main

# 2. SSH to server
ssh forex  # or: ssh user@your.server.ip

# 3. Update and rebuild
cd ~/Forex_Agent && bash execution/scripts/update_server.sh
```

---

## First-Time Server Setup

```bash
# Clone repository
git clone <your-repo-url> ~/Forex_Agent
cd ~/Forex_Agent

# Create .env file
cp .env.example .env
nano .env  # Fill in your credentials

# Create required files/directories
touch trade_journal.csv
touch trades.db
touch macro_data.db
mkdir -p logs

# Build and start
docker compose up -d --build

# Verify
docker ps
docker logs forex-agent --tail 50
```

---

## Smoke Test (Deployment Validation)

Run before going live to verify the system works:

```bash
# Inside container
docker compose exec agent python execution/main_loop.py --smoke

# Or standalone
docker run --rm --env-file .env forex-agent:latest python execution/main_loop.py --smoke
```

**Success**: Exit code 0, shows "✅ SMOKE TEST PASSED"  
**Failure**: Exit code 1, shows error details

---

## Common Operations

### View Logs
```bash
# Live logs
docker logs forex-agent -f

# Last 100 lines
docker logs forex-agent --tail 100

# All container logs
docker compose logs -f
```

### Check Status
```bash
# Container health
docker ps

# Run health check
docker compose exec agent python -m execution.health_check --json
```

### Restart Services
```bash
docker compose restart agent
# or full rebuild:
docker compose down && docker compose up -d --build
```

### Stop Everything
```bash
docker compose down
```

---

## Rollback Procedure

If deployment fails:

```bash
# Quick rollback - revert to previous commit
cd ~/Forex_Agent
git log --oneline -5           # Find last working commit
git checkout <commit-hash> .   # Revert files
docker compose up -d --build   # Rebuild

# OR use rollback script
bash execution/scripts/rollback.sh
```

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `POLYGON_API_KEY` | Yes | Market data API key |
| `BROKER` | Yes | `mock` or `ig` |
| `LIVE_TRADING_ENABLED` | Yes | `true`/`false` safety switch |
| `IG_*` | For live | IG Markets credentials |
| `DISCORD_WEBHOOK_URL` | Optional | Notifications |

### Modes

| Mode | BROKER | LIVE_TRADING_ENABLED | Behavior |
|------|--------|----------------------|----------|
| Simulation | `mock` | `false` | Safe testing |
| Paper Trading | `ig` | `false` | IG API, no orders |
| **Live** | `ig` | `true` | Real trades! |

---

## Troubleshooting

### Container won't start
```bash
docker compose logs agent | tail 50
docker compose exec agent python -c "from execution.config import config"
```

### "Unhealthy" status
```bash
docker inspect forex-agent --format='{{.State.Health.Log}}'
```

### Network issues
```bash
docker compose exec agent curl -I http://macro-server:8000/health
```

### Full diagnostics
```bash
python execution/tools/troubleshoot_server.py
```

---

## Risk Warnings

> ⚠️ **Live Trading**: Ensure `LIVE_TRADING_ENABLED=true` ONLY after full validation

> ⚠️ **IG Integration**: Still WIP - test thoroughly in DEMO mode first

> ⚠️ **Secrets**: Never commit `.env` - it contains API keys

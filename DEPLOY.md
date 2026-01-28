# Deployment Workflow

This project uses a **semi-automated** deployment workflow:
- **Push to GitHub**: Automated from local machine
- **Pull on Server**: Manual (you SSH and run the update script)

## How to Deploy

### Step 1: Commit Your Changes
```bash
git add .
git commit -m "feat: your changes"
```

### Step 2: Push to GitHub
Run the deployment script from the project root:
```bash
python deploy.py
```

This will:
- Check for uncommitted changes
- Push to `origin/main`
- Display manual server instructions

### Step 3: Update the Server (MANUAL)
SSH into the server and run the update script:

```bash
ssh forex
cd ~/Forex_Agent
bash execution/scripts/update_server.sh
```

**OR** run commands individually:
```bash
cd ~/Forex_Agent
git pull origin main
docker compose down && docker compose up -d --build
```

### Step 4: Verify Deployment
```bash
docker ps
docker logs forex_agent-agent-1 --tail 50
```

## Prerequisites

- SSH alias `forex` configured in `~/.ssh/config`
- SSH Key authorized on the server
- Python dependencies installed locally

## Troubleshooting

If deployment fails:
- Run `python execution/tools/troubleshoot_server.py` for a deep health check
- Run `python execution/tools/remote_ops.py logs` to check container logs

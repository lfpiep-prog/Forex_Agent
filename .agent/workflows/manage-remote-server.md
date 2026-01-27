---
description: Standard workflow for managing the remote Forex Agent server (login, troubleshooting, deployment)
---

# Remote Server Management Workflow

This workflow guides you through connecting to, troubleshooting, and deploying code to the remote Forex Agent server.

**Prerequisites:**
- SSH Config alias `forex` must be configured.
- SSH Private Key must be available and authorized on the server.
- Python dependencies installed locally.

## 1. Verify Connection / Health Check
Before doing anything, verify the server status.

```bash
# Run the troubleshooting tool to get a full health report
python tools/troubleshoot_server.py
```

If you need a simple status check:
```bash
python tools/remote_ops.py status
```

## 2. Viewing Logs
To debug issues, view the logs remotely without logging in manually.

```bash
# View last 100 lines of the agent log
python tools/remote_ops.py logs --lines 100
```

## 3. Deployment (Edit -> Push -> Deploy)
**NEVER** edit files directly on the server. Follow this cycle:

1.  **Edit Locally**: Make your code changes in the local workspace.
2.  **Verify**: Run local tests if applicable.
3.  **Deploy**: Run the deployment script.

```bash
# This script will:
# 1. Check for uncommitted changes
# 2. Push to origin/main
# 3. SSH into server, git pull, and docker restart
# 4. Wait and run a health check
python deploy.py
```

## 4. Manual SSH Access (Fallback)
If automation fails or deep debugging is needed:
```bash
ssh forex
```

**Common Server Paths:**
- App Directory: `~/ForexAgent`
- Logs: `docker logs forex_agent-agent-1`

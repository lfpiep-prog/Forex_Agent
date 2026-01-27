#!/bin/bash
# ===========================================
# Forex Agent - Server Update Script
# ===========================================
# Usage: bash update_server.sh

set -e

echo "=== 1. Pulling latest changes from Git ==="
git pull origin main

echo "=== 2. Rebuilding and Restarting Docker Containers ==="
docker compose down
docker compose up --build -d

echo "=== 3. Verifying System Health ==="
# Wait a moment for containers to initialize
echo "Waiting 10 seconds for service initialization..."
sleep 10
python3 check_system.py

echo ""
echo "=== UPDATE COMPLETE ==="

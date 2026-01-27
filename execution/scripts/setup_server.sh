#!/bin/bash
# ===========================================
# Forex Agent - Hetzner Server Setup Script
# ===========================================
# Run this script on a fresh Ubuntu/Debian server
# Usage: bash setup_server.sh

set -e

echo "=== 1. Updating System ==="
sudo apt update && sudo apt upgrade -y

echo "=== 2. Installing Docker ==="
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

echo "=== 3. Installing Docker Compose Plugin ==="
sudo apt install -y docker-compose-plugin

echo "=== 4. Installing Git ==="
sudo apt install -y git

echo "=== 5. Cloning Repository ==="
cd ~
git clone https://github.com/lfpiep-prog/Forex_Agent.git
cd Forex_Agent

echo "=== 6. Creating .env file template ==="
# Note: User has already set up .env with DEMO credentials on the server.
# To switch to LIVE, they need to edit the .env file and change IG_ACC_TYPE to LIVE.

echo ""
echo "============================================"
echo "  SETUP COMPLETE!"
echo "============================================"
echo ""
echo "NEXT STEPS:"
echo "1. Log out and log back in (for docker group)"
echo "2. Edit the .env file with your real credentials:"
echo "   nano ~/Forex_Agent/.env"
echo ""
echo "3. Start the agent:"
echo "   cd ~/Forex_Agent && docker compose up --build -d"
echo ""
echo "4. View logs:"
echo "   docker logs -f forex_agent-agent-1"
echo ""

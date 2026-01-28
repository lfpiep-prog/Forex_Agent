#!/bin/bash
# ===========================================
# Forex Agent - Firewall Setup Script
# ===========================================
# Konfiguriert UFW Firewall mit minimalem Port-Zugang
#
# Usage: sudo bash setup_firewall.sh
# ===========================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== UFW Firewall Setup ===${NC}"
echo ""

# Install UFW if not present
if ! command -v ufw &> /dev/null; then
    echo "Installiere UFW..."
    sudo apt update && sudo apt install -y ufw
fi

# Reset to defaults
echo -e "${GREEN}1. Setze Standardregeln...${NC}"
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (WICHTIG: Zuerst erlauben!)
echo -e "${GREEN}2. Erlaube SSH (Port 22)...${NC}"
sudo ufw allow 22/tcp comment 'SSH'

# Ask about additional ports
echo ""
echo "Zusätzliche Ports:"
read -p "Macro-Server Port 8000 von außen erlauben? (ja/nein): " allow_8000
if [ "$allow_8000" == "ja" ]; then
    sudo ufw allow 8000/tcp comment 'Macro Server'
    echo "   Port 8000 erlaubt"
else
    echo "   Port 8000 bleibt blockiert (nur Docker-intern erreichbar)"
fi

# Enable firewall
echo ""
echo -e "${GREEN}3. Aktiviere Firewall...${NC}"
sudo ufw --force enable

# Show status
echo ""
echo -e "${GREEN}=== Firewall Status ===${NC}"
sudo ufw status verbose

echo ""
echo -e "${GREEN}Fertig! Firewall ist aktiv.${NC}"

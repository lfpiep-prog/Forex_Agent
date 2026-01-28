#!/bin/bash
# ===========================================
# Forex Agent - SSH Hardening Script
# ===========================================
# WICHTIG: Führe dieses Script NACH dem Einloggen über SSH aus!
# Stelle sicher, dass dein SSH-Key bereits funktioniert!
# 
# Usage: sudo bash harden_ssh.sh
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== SSH Hardening Script ===${NC}"
echo ""

# Safety check
echo -e "${RED}WARNUNG: Dieses Script deaktiviert Passwort-Login!${NC}"
echo "Stelle sicher, dass dein SSH-Key bereits funktioniert."
echo ""
read -p "Fortfahren? (ja/nein): " confirm
if [ "$confirm" != "ja" ]; then
    echo "Abgebrochen."
    exit 0
fi

# Backup original config
SSHD_CONFIG="/etc/ssh/sshd_config"
BACKUP_FILE="/etc/ssh/sshd_config.backup.$(date +%Y%m%d_%H%M%S)"

echo -e "${GREEN}1. Erstelle Backup von sshd_config...${NC}"
sudo cp "$SSHD_CONFIG" "$BACKUP_FILE"
echo "   Backup erstellt: $BACKUP_FILE"

# Apply hardening settings
echo -e "${GREEN}2. Wende Sicherheitseinstellungen an...${NC}"

# Disable password authentication
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' "$SSHD_CONFIG"
sudo sed -i 's/^#*ChallengeResponseAuthentication.*/ChallengeResponseAuthentication no/' "$SSHD_CONFIG"

# Disable root login
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' "$SSHD_CONFIG"

# Enable pubkey authentication
sudo sed -i 's/^#*PubkeyAuthentication.*/PubkeyAuthentication yes/' "$SSHD_CONFIG"

# Limit auth tries
sudo sed -i 's/^#*MaxAuthTries.*/MaxAuthTries 3/' "$SSHD_CONFIG"

# Client alive settings (idle timeout)
if ! grep -q "^ClientAliveInterval" "$SSHD_CONFIG"; then
    echo "ClientAliveInterval 300" | sudo tee -a "$SSHD_CONFIG" > /dev/null
fi
if ! grep -q "^ClientAliveCountMax" "$SSHD_CONFIG"; then
    echo "ClientAliveCountMax 2" | sudo tee -a "$SSHD_CONFIG" > /dev/null
fi

# Validate config before restart
echo -e "${GREEN}3. Validiere SSH-Konfiguration...${NC}"
sudo sshd -t
if [ $? -ne 0 ]; then
    echo -e "${RED}FEHLER: SSH-Konfiguration ungültig! Stelle Backup wieder her...${NC}"
    sudo cp "$BACKUP_FILE" "$SSHD_CONFIG"
    exit 1
fi

echo -e "${GREEN}4. Starte SSH-Dienst neu...${NC}"
sudo systemctl restart sshd

echo ""
echo -e "${GREEN}=== SSH Hardening Abgeschlossen ===${NC}"
echo ""
echo "Aktive Einstellungen:"
sudo sshd -T | grep -E "passwordauthentication|permitrootlogin|pubkeyauthentication|maxauthtries"
echo ""
echo -e "${YELLOW}WICHTIG: Teste den SSH-Login in einem NEUEN Terminal-Fenster,${NC}"
echo -e "${YELLOW}bevor du diese Verbindung schließt!${NC}"

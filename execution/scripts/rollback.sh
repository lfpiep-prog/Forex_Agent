#!/bin/bash
# ===========================================
# Forex Agent - Rollback Script
# ===========================================
# Usage: bash rollback.sh
#
# Reverts to the previous deployment commit.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "  Forex Agent - ROLLBACK"
echo "=========================================="
echo ""

# Check for saved rollback commit
ROLLBACK_FILE="/tmp/forex_agent_rollback_commit"

if [ -f "$ROLLBACK_FILE" ]; then
    ROLLBACK_COMMIT=$(cat "$ROLLBACK_FILE")
    echo -e "${YELLOW}Found rollback point: ${ROLLBACK_COMMIT:0:8}${NC}"
else
    echo -e "${RED}No rollback point found!${NC}"
    echo "Showing last 5 commits:"
    git log --oneline -5
    echo ""
    read -p "Enter commit hash to rollback to: " ROLLBACK_COMMIT
fi

if [ -z "$ROLLBACK_COMMIT" ]; then
    echo -e "${RED}No commit specified. Aborting.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Rolling back to: $ROLLBACK_COMMIT${NC}"

# Rollback
git fetch origin
git reset --hard "$ROLLBACK_COMMIT"

# Rebuild
echo ""
echo -e "${YELLOW}Rebuilding containers...${NC}"
docker compose down
docker compose up -d --build

# Wait and verify
echo ""
echo -e "${YELLOW}Verifying (waiting 10s)...${NC}"
sleep 10
docker ps

echo ""
echo "=========================================="
echo -e "${GREEN}  ROLLBACK COMPLETE${NC}"
echo "=========================================="
echo ""
echo "Current commit: $(git rev-parse --short HEAD)"
echo "Run 'docker logs forex-agent -f' to monitor"

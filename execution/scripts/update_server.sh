#!/bin/bash
# ===========================================
# Forex Agent - Server Update Script
# ===========================================
# Usage: bash update_server.sh
#
# This script:
# 1. Creates rollback backup
# 2. Pulls latest code
# 3. Rebuilds containers
# 4. Runs smoke test
# 5. Verifies health

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "  Forex Agent - Server Update"
echo "=========================================="
echo ""

# Step 1: Save current commit for rollback
echo -e "${YELLOW}[1/5] Saving rollback point...${NC}"
CURRENT_COMMIT=$(git rev-parse HEAD)
echo "$CURRENT_COMMIT" > /tmp/forex_agent_rollback_commit
echo "  Saved: ${CURRENT_COMMIT:0:8}"

# Step 2: Pull latest changes
echo ""
echo -e "${YELLOW}[2/5] Pulling latest changes...${NC}"
git fetch origin main
git reset --hard origin/main
NEW_COMMIT=$(git rev-parse HEAD)
echo "  Updated to: ${NEW_COMMIT:0:8}"

if [ "$CURRENT_COMMIT" = "$NEW_COMMIT" ]; then
    echo -e "${GREEN}  Already up to date.${NC}"
fi

# Step 3: Rebuild containers
echo ""
echo -e "${YELLOW}[3/5] Rebuilding containers...${NC}"
docker compose down
docker compose build --no-cache
docker compose up -d

# Step 4: Wait and run smoke test
echo ""
echo -e "${YELLOW}[4/5] Running smoke test (waiting 15s for startup)...${NC}"
sleep 15

if docker compose exec -T agent python execution/main_loop.py --smoke; then
    echo -e "${GREEN}  Smoke test PASSED${NC}"
else
    echo -e "${RED}  Smoke test FAILED - triggering rollback${NC}"
    bash "$SCRIPT_DIR/rollback.sh"
    exit 1
fi

# Step 5: Final health check
echo ""
echo -e "${YELLOW}[5/5] Running health check...${NC}"
docker compose exec -T agent python execution/scripts/check_system.py

echo ""
echo "=========================================="
echo -e "${GREEN}  UPDATE COMPLETE${NC}"
echo "=========================================="
echo ""
echo "Useful commands:"
echo "  docker logs forex-agent -f        # Live logs"
echo "  docker ps                         # Container status"
echo "  bash execution/scripts/rollback.sh # Rollback if issues"

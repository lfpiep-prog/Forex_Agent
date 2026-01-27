#!/bin/bash
# Deployment script for Discord duplicate alerts fix

echo "=== Forex Agent - Deploying Discord Fix ==="
echo ""

# Navigate to project directory
cd /root/Forex_Agent || exit 1

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Check if files were updated
if [ $? -eq 0 ]; then
    echo "✅ Git pull successful"
else
    echo "❌ Git pull failed"
    exit 1
fi

# Restart Docker containers to apply changes
echo ""
echo "🔄 Restarting Docker containers..."
docker-compose down
docker-compose up -d --build

# Wait for containers to start
echo ""
echo "⏳ Waiting for containers to start..."
sleep 10

# Check container status
echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Monitor Discord for the next hourly cycle"
echo "2. Verify no duplicate notifications"
echo "3. Check that Order IDs appear correctly"

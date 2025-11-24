#!/bin/bash

# ============================================================================
# Script 6: View Container App Logs
# ============================================================================
# This script shows logs from your deployed containers

set -e

# Load environment variables
if [ ! -f .env.azure ]; then
    echo "❌ .env.azure not found"
    exit 1
fi

source .env.azure

echo "=================================================="
echo "📋 Container App Logs"
echo "=================================================="
echo ""
echo "Which logs do you want to view?"
echo "  1) Backend logs"
echo "  2) Frontend logs"
echo "  3) Both (streaming)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "📋 Backend Logs (last 100 lines):"
        az containerapp logs show \
            --name rfprag-backend \
            --resource-group $RESOURCE_GROUP \
            --tail 100 \
            --follow
        ;;
    2)
        echo ""
        echo "📋 Frontend Logs (last 100 lines):"
        az containerapp logs show \
            --name rfprag-frontend \
            --resource-group $RESOURCE_GROUP \
            --tail 100 \
            --follow
        ;;
    3)
        echo ""
        echo "📋 Streaming logs from both containers..."
        echo "Press Ctrl+C to stop"
        echo ""
        echo "=== BACKEND ==="
        az containerapp logs show \
            --name rfprag-backend \
            --resource-group $RESOURCE_GROUP \
            --tail 50 &
        
        echo ""
        echo "=== FRONTEND ==="
        az containerapp logs show \
            --name rfprag-frontend \
            --resource-group $RESOURCE_GROUP \
            --tail 50 &
        
        wait
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

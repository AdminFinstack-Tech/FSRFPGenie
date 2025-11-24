#!/bin/bash

# ============================================================================
# Script 8: Cleanup Azure Resources
# ============================================================================
# WARNING: This will delete ALL resources and cannot be undone!

set -e

# Load environment variables
if [ ! -f .env.azure ]; then
    echo "❌ .env.azure not found"
    exit 1
fi

source .env.azure

echo "=================================================="
echo "⚠️  WARNING: CLEANUP AZURE RESOURCES"
echo "=================================================="
echo ""
echo "This will DELETE the following resource group and ALL its contents:"
echo "  Resource Group: $RESOURCE_GROUP"
echo ""
echo "This includes:"
echo "  - Container Apps (frontend, backend)"
echo "  - Container Registry and all images"
echo "  - Cosmos DB and all data"
echo "  - Redis Cache"
echo "  - All associated resources"
echo ""
echo "⚠️  THIS CANNOT BE UNDONE!"
echo ""
read -p "Are you SURE you want to delete everything? (yes/no) " confirmation

if [ "$confirmation" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🗑️  Deleting resource group $RESOURCE_GROUP..."
az group delete \
    --name $RESOURCE_GROUP \
    --yes \
    --no-wait

echo ""
echo "=================================================="
echo "✅ Cleanup initiated"
echo "=================================================="
echo ""
echo "Resource group deletion is running in the background."
echo "It may take 5-10 minutes to complete."
echo ""
echo "Check status with:"
echo "  az group show --name $RESOURCE_GROUP"
echo ""

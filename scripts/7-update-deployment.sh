#!/bin/bash

# ============================================================================
# Script 7: Update Deployment (Rebuild and Redeploy)
# ============================================================================
# This script rebuilds images and updates the running containers

set -e

echo "=================================================="
echo "🔄 Update Deployment"
echo "=================================================="

# Load environment variables
if [ ! -f .env.azure ]; then
    echo "❌ .env.azure not found"
    exit 1
fi

source .env.azure

echo ""
echo "This will:"
echo "  1. Rebuild Docker images for Linux"
echo "  2. Push to Azure Container Registry"
echo "  3. Update running containers"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Navigate to project root
cd "$(dirname "$0")/.."

# Rebuild images
echo ""
echo "🏗️  Rebuilding images..."
docker buildx use multiplatform

docker buildx build \
    --platform linux/amd64 \
    --tag rfprag-frontend:linux \
    --load \
    ./frontend

docker buildx build \
    --platform linux/amd64 \
    --tag rfprag-backend:linux \
    --load \
    ./backend

# Tag images
echo ""
echo "🏷️  Tagging images..."
docker tag rfprag-frontend:linux $ACR_LOGIN_SERVER/rfprag-frontend:latest
docker tag rfprag-backend:linux $ACR_LOGIN_SERVER/rfprag-backend:latest

# Push images
echo ""
echo "📤 Pushing to ACR..."
echo $ACR_PASSWORD | docker login $ACR_LOGIN_SERVER \
    --username $ACR_USERNAME \
    --password-stdin

docker push $ACR_LOGIN_SERVER/rfprag-frontend:latest
docker push $ACR_LOGIN_SERVER/rfprag-backend:latest

# Update container apps
echo ""
echo "🔄 Updating backend..."
az containerapp update \
    --name rfprag-backend \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_LOGIN_SERVER/rfprag-backend:latest

echo ""
echo "🔄 Updating frontend..."
az containerapp update \
    --name rfprag-frontend \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_LOGIN_SERVER/rfprag-frontend:latest

echo ""
echo "=================================================="
echo "✅ Deployment updated successfully!"
echo "=================================================="
echo ""
echo "🌐 Frontend: $FRONTEND_URL"
echo "🔧 Backend:  $BACKEND_URL"
echo ""

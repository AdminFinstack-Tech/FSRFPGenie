#!/bin/bash

# ============================================================================
# Script 4: Push Docker Images to Azure Container Registry
# ============================================================================
# This script tags and pushes your Linux-built images to ACR

set -e

echo "=================================================="
echo "📤 Pushing images to Azure Container Registry"
echo "=================================================="

# Load environment variables
if [ ! -f .env.azure ]; then
    echo "❌ .env.azure not found. Please run ./3-setup-azure.sh first"
    exit 1
fi

source .env.azure

echo ""
echo "ACR Login Server: $ACR_LOGIN_SERVER"
echo ""

# Login to ACR
echo "🔐 Logging in to Azure Container Registry..."
echo $ACR_PASSWORD | docker login $ACR_LOGIN_SERVER \
    --username $ACR_USERNAME \
    --password-stdin

# Tag images
echo ""
echo "🏷️  Tagging images..."
docker tag rfprag-frontend:linux $ACR_LOGIN_SERVER/rfprag-frontend:latest
docker tag rfprag-backend:linux $ACR_LOGIN_SERVER/rfprag-backend:latest

# Push images
echo ""
echo "📤 Pushing frontend image..."
docker push $ACR_LOGIN_SERVER/rfprag-frontend:latest

echo ""
echo "📤 Pushing backend image..."
docker push $ACR_LOGIN_SERVER/rfprag-backend:latest

echo ""
echo "=================================================="
echo "✅ Images pushed successfully!"
echo "=================================================="
echo ""
echo "Images in registry:"
az acr repository list --name $ACR_NAME --output table
echo ""
echo "Next step: Run ./5-deploy-to-azure.sh to deploy to Container Apps"
echo ""

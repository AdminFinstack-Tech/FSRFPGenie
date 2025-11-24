#!/bin/bash

# ============================================================================
# Script 5: Deploy to Azure Container Apps
# ============================================================================
# This script deploys frontend and backend containers to Azure Container Apps

set -e

echo "=================================================="
echo "🚀 Deploying to Azure Container Apps"
echo "=================================================="

# Load environment variables
if [ ! -f .env.azure ]; then
    echo "❌ .env.azure not found. Please run ./3-setup-azure.sh first"
    exit 1
fi

source .env.azure

# Check if OpenAI key is set
if [ "$OPENAI_API_KEY" == "your-openai-api-key-here" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set in .env.azure"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Deploy Backend
echo ""
echo "📦 Deploying Backend Container App..."
az containerapp create \
    --name rfprag-backend \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --image $ACR_LOGIN_SERVER/rfprag-backend:latest \
    --target-port 5001 \
    --ingress external \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --cpu 1.0 \
    --memory 2.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars \
        "MONGODB_URI=$COSMOS_CONNECTION" \
        "REDIS_URL=$REDIS_CONNECTION" \
        "OPENAI_API_KEY=$OPENAI_API_KEY" \
        "AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT" \
        "AZURE_OPENAI_KEY=$AZURE_OPENAI_KEY" \
        "FLASK_ENV=production" \
        "CORS_ORIGINS=*" \
    --output table

# Get backend URL
BACKEND_URL=$(az containerapp show \
    --name rfprag-backend \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

echo ""
echo "✅ Backend URL: https://$BACKEND_URL"

# Deploy Frontend
echo ""
echo "📦 Deploying Frontend Container App..."
az containerapp create \
    --name rfprag-frontend \
    --resource-group $RESOURCE_GROUP \
    --environment $ENV_NAME \
    --image $ACR_LOGIN_SERVER/rfprag-frontend:latest \
    --target-port 80 \
    --ingress external \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --cpu 0.5 \
    --memory 1.0Gi \
    --min-replicas 1 \
    --max-replicas 5 \
    --env-vars \
        "VUE_APP_API_URL=https://$BACKEND_URL" \
    --output table

# Get frontend URL
FRONTEND_URL=$(az containerapp show \
    --name rfprag-frontend \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

echo ""
echo "=================================================="
echo "✅ Deployment Complete!"
echo "=================================================="
echo ""
echo "🌐 Frontend URL: https://$FRONTEND_URL"
echo "🔧 Backend URL:  https://$BACKEND_URL"
echo ""
echo "📝 Saving URLs to .env.azure..."

# Append URLs to .env.azure
cat >> .env.azure << EOF

# Deployed URLs
FRONTEND_URL=https://$FRONTEND_URL
BACKEND_URL=https://$BACKEND_URL
EOF

echo ""
echo "✅ URLs saved to .env.azure"
echo ""
echo "Next steps:"
echo "  1. Visit https://$FRONTEND_URL to test your application"
echo "  2. Check logs: ./6-view-logs.sh"
echo "  3. Update deployment: ./7-update-deployment.sh"
echo ""

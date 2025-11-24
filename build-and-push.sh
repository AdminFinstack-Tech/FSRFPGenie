#!/bin/bash

# 🐳 Docker Build & Push to Azure Container Registry
# This script builds both frontend and backend Docker images and pushes them to ACR

set -e  # Exit on any error

echo "════════════════════════════════════════════════════════════"
echo "  🐳 Docker Build & Push to Azure Container Registry"
echo "════════════════════════════════════════════════════════════"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load Azure configuration
if [ -f ".env.azure" ]; then
    echo "📋 Loading Azure configuration from .env.azure..."
    source .env.azure
else
    echo "❌ Error: .env.azure file not found!"
    echo "Please run 3-setup-azure.sh first or create .env.azure with your ACR details"
    exit 1
fi

# Validate required variables
if [ -z "$ACR_LOGIN_SERVER" ] || [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
    echo "❌ Error: ACR credentials not found in .env.azure"
    echo "Required: ACR_LOGIN_SERVER, ACR_USERNAME, ACR_PASSWORD"
    exit 1
fi

echo "✅ Configuration loaded"
echo "   ACR Server: ${ACR_LOGIN_SERVER}"
echo "   ACR Name: ${ACR_NAME}"
echo ""

# Login to Azure Container Registry
echo "🔐 Logging in to Azure Container Registry..."
echo "${ACR_PASSWORD}" | docker login ${ACR_LOGIN_SERVER} \
    --username ${ACR_USERNAME} \
    --password-stdin

if [ $? -eq 0 ]; then
    echo "✅ Successfully logged in to ACR"
else
    echo "❌ Failed to login to ACR"
    exit 1
fi
echo ""

# Set image names and tags
BACKEND_IMAGE="${ACR_LOGIN_SERVER}/rfprag-backend"
FRONTEND_IMAGE="${ACR_LOGIN_SERVER}/rfprag-frontend"
TAG="${1:-latest}"  # Use first argument as tag, default to "latest"

echo "📦 Image Configuration:"
echo "   Backend:  ${BACKEND_IMAGE}:${TAG}"
echo "   Frontend: ${FRONTEND_IMAGE}:${TAG}"
echo "   Tag:      ${TAG}"
echo ""

# Build Backend
echo "════════════════════════════════════════════════════════════"
echo "🔨 Building Backend Docker Image..."
echo "════════════════════════════════════════════════════════════"
cd backend

docker build \
    --platform linux/amd64 \
    -t ${BACKEND_IMAGE}:${TAG} \
    -t ${BACKEND_IMAGE}:latest \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend image built successfully${NC}"
else
    echo -e "${RED}❌ Backend build failed${NC}"
    exit 1
fi

cd ..
echo ""

# Build Frontend
echo "════════════════════════════════════════════════════════════"
echo "🔨 Building Frontend Docker Image..."
echo "════════════════════════════════════════════════════════════"
cd frontend

docker build \
    --platform linux/amd64 \
    -t ${FRONTEND_IMAGE}:${TAG} \
    -t ${FRONTEND_IMAGE}:latest \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend image built successfully${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi

cd ..
echo ""

# Push Backend
echo "════════════════════════════════════════════════════════════"
echo "📤 Pushing Backend Image to ACR..."
echo "════════════════════════════════════════════════════════════"

docker push ${BACKEND_IMAGE}:${TAG}
docker push ${BACKEND_IMAGE}:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend image pushed successfully${NC}"
else
    echo -e "${RED}❌ Backend push failed${NC}"
    exit 1
fi
echo ""

# Push Frontend
echo "════════════════════════════════════════════════════════════"
echo "📤 Pushing Frontend Image to ACR..."
echo "════════════════════════════════════════════════════════════"

docker push ${FRONTEND_IMAGE}:${TAG}
docker push ${FRONTEND_IMAGE}:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend image pushed successfully${NC}"
else
    echo -e "${RED}❌ Frontend push failed${NC}"
    exit 1
fi
echo ""

# Verify images in ACR
echo "════════════════════════════════════════════════════════════"
echo "🔍 Verifying Images in Azure Container Registry..."
echo "════════════════════════════════════════════════════════════"

echo "📦 Backend images:"
az acr repository show-tags \
    --name ${ACR_NAME} \
    --repository rfprag-backend \
    --output table 2>/dev/null || echo "   (Using docker login verification)"

echo ""
echo "📦 Frontend images:"
az acr repository show-tags \
    --name ${ACR_NAME} \
    --repository rfprag-frontend \
    --output table 2>/dev/null || echo "   (Using docker login verification)"

echo ""
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ SUCCESS! All images built and pushed${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📋 Summary:"
echo "   ✅ Backend:  ${BACKEND_IMAGE}:${TAG}"
echo "   ✅ Frontend: ${FRONTEND_IMAGE}:${TAG}"
echo ""
echo "🚀 Next Steps:"
echo "   1. Deploy to Azure Container Apps:"
echo "      ./scripts/5-deploy-to-azure.sh"
echo ""
echo "   2. Or update existing deployment:"
echo "      ./scripts/7-update-deployment.sh"
echo ""
echo "   3. View logs after deployment:"
echo "      ./scripts/6-view-logs.sh"
echo ""
echo "════════════════════════════════════════════════════════════"

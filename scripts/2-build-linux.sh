#!/bin/bash

# ============================================================================
# Script 2: Build Docker Images for Linux Platform (Azure Compatible)
# ============================================================================
# This script builds both frontend and backend for linux/amd64 architecture
# which is required for Azure Container Apps deployment

set -e

echo "=================================================="
echo "🏗️  Building Docker images for Linux (amd64)"
echo "=================================================="

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if buildx is set up
if ! docker buildx ls | grep -q "multiplatform"; then
    echo "❌ Buildx not set up. Please run ./1-setup-buildx.sh first"
    exit 1
fi

# Use the multiplatform builder
docker buildx use multiplatform

echo ""
echo "📦 Building Frontend for Linux..."
echo "-----------------------------------"
docker buildx build \
    --platform linux/amd64 \
    --tag rfprag-frontend:linux \
    --load \
    ./frontend

echo ""
echo "📦 Building Backend for Linux..."
echo "-----------------------------------"
docker buildx build \
    --platform linux/amd64 \
    --tag rfprag-backend:linux \
    --load \
    ./backend

echo ""
echo "=================================================="
echo "✅ Linux builds complete!"
echo "=================================================="
echo ""
echo "Images created:"
docker images | grep "rfprag.*linux"
echo ""
echo "Next step: Run ./3-setup-azure.sh to create Azure resources"
echo ""

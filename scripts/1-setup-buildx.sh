#!/bin/bash

# ============================================================================
# Script 1: Setup Docker Buildx for Multi-Platform Builds
# ============================================================================
# This script sets up Docker Buildx to build Linux images for Azure deployment
# Run this ONCE before building images

set -e

echo "=================================================="
echo "🔧 Setting up Docker Buildx for Linux builds"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"

# Create buildx builder instance if it doesn't exist
if ! docker buildx ls | grep -q "multiplatform"; then
    echo "📦 Creating multiplatform builder..."
    docker buildx create --name multiplatform --driver docker-container --use
else
    echo "✅ Multiplatform builder already exists"
    docker buildx use multiplatform
fi

# Bootstrap the builder
echo "🚀 Bootstrapping builder..."
docker buildx inspect --bootstrap

echo ""
echo "=================================================="
echo "✅ Docker Buildx setup complete!"
echo "=================================================="
echo ""
echo "Next step: Run ./2-build-linux.sh to build images for Linux"
echo ""

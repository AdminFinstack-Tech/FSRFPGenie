# 🐳 Docker Build & Push Guide

## Quick Start

### Build and Push Everything (Recommended)

```bash
# Build both images and push to Azure Container Registry
./build-and-push.sh

# Or with a specific tag
./build-and-push.sh v1.0.0
```

---

## Step-by-Step Instructions

### Prerequisites

1. **Docker Desktop** installed and running
2. **Azure CLI** installed (`az` command available)
3. **Azure Container Registry** created (already done in your `.env.azure`)

### Check Your Configuration

```bash
# Verify .env.azure exists
cat .env.azure | grep ACR

# Should show:
# ACR_LOGIN_SERVER=rfpragreg.azurecr.io
# ACR_USERNAME=rfpragreg
# ACR_PASSWORD=...
```

---

## 🚀 Build and Push Commands

### Option 1: All-in-One Script (Easiest)

```bash
# From project root
./build-and-push.sh
```

This will:
- ✅ Login to Azure Container Registry
- ✅ Build backend Docker image (linux/amd64)
- ✅ Build frontend Docker image (linux/amd64)
- ✅ Tag images with 'latest'
- ✅ Push both images to ACR
- ✅ Verify images in registry

### Option 2: Using Existing Scripts

```bash
# Step 1: Build images for Linux
cd scripts
./2-build-linux.sh

# Step 2: Push to ACR
./4-push-to-acr.sh
```

### Option 3: Manual Build (Advanced)

```bash
# Load configuration
source .env.azure

# Login to ACR
echo $ACR_PASSWORD | docker login $ACR_LOGIN_SERVER \
    --username $ACR_USERNAME \
    --password-stdin

# Build Backend
cd backend
docker build --platform linux/amd64 \
    -t ${ACR_LOGIN_SERVER}/rfprag-backend:latest .
cd ..

# Build Frontend
cd frontend
docker build --platform linux/amd64 \
    -t ${ACR_LOGIN_SERVER}/rfprag-frontend:latest .
cd ..

# Push to ACR
docker push ${ACR_LOGIN_SERVER}/rfprag-backend:latest
docker push ${ACR_LOGIN_SERVER}/rfprag-frontend:latest
```

---

## 🏷️ Image Tagging

### Tag with Version

```bash
# Build with custom tag
./build-and-push.sh v1.2.0

# This creates:
# - rfpragreg.azurecr.io/rfprag-backend:v1.2.0
# - rfpragreg.azurecr.io/rfprag-backend:latest
# - rfpragreg.azurecr.io/rfprag-frontend:v1.2.0
# - rfpragreg.azurecr.io/rfprag-frontend:latest
```

### Tag with Git Commit

```bash
# Use git commit hash as tag
./build-and-push.sh $(git rev-parse --short HEAD)

# Or use git describe
./build-and-push.sh $(git describe --tags --always)
```

---

## 🔍 Verify Images

### Check Local Images

```bash
# List local Docker images
docker images | grep rfprag

# Should show:
# rfpragreg.azurecr.io/rfprag-backend   latest   ...   
# rfpragreg.azurecr.io/rfprag-frontend  latest   ...
```

### Check Images in Azure Container Registry

```bash
# Using Azure CLI
az acr repository list --name rfpragreg --output table

# Show tags for backend
az acr repository show-tags \
    --name rfpragreg \
    --repository rfprag-backend \
    --output table

# Show tags for frontend
az acr repository show-tags \
    --name rfpragreg \
    --repository rfprag-frontend \
    --output table
```

### Test Images Locally

```bash
# Test backend image
docker run -p 5001:5001 \
    -e MONGODB_URI="mongodb://localhost:27017/rfprag" \
    rfpragreg.azurecr.io/rfprag-backend:latest

# Test frontend image
docker run -p 8080:80 \
    rfpragreg.azurecr.io/rfprag-frontend:latest

# Then open: http://localhost:8080
```

---

## 🐛 Troubleshooting

### Error: "Cannot connect to Docker daemon"

```bash
# Make sure Docker Desktop is running
# On macOS:
open -a Docker

# Wait for Docker to start, then try again
```

### Error: "unauthorized: authentication required"

```bash
# Re-login to ACR
source .env.azure
echo $ACR_PASSWORD | docker login $ACR_LOGIN_SERVER \
    --username $ACR_USERNAME \
    --password-stdin
```

### Error: "ACR_LOGIN_SERVER not found"

```bash
# Check .env.azure exists
ls -la .env.azure

# If missing, create it or copy from scripts directory
cp scripts/.env.azure .env.azure
```

### Error: "platform does not match"

```bash
# Make sure to build for linux/amd64 (required for Azure)
docker build --platform linux/amd64 -t myimage .

# Check your platform
docker info | grep "Operating System"
```

### Build is Slow

```bash
# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Then run build again
./build-and-push.sh
```

### Frontend Build Fails with Memory Error

```bash
# Increase Docker memory limit
# Docker Desktop > Settings > Resources > Memory
# Set to at least 4GB

# Or build with fewer parallel jobs
cd frontend
docker build --build-arg NODE_OPTIONS=--max_old_space_size=4096 .
```

---

## 📊 Build Optimization

### Use Docker Build Cache

The Dockerfiles are optimized for caching:

**Backend:**
- Dependencies installed first (cached unless requirements.txt changes)
- Code copied last (rebuilds only when code changes)

**Frontend:**
- npm packages installed first (cached unless package.json changes)
- Build happens in multi-stage (smaller final image)

### Speed Up Builds

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Use build cache mount
docker build --cache-from=rfpragreg.azurecr.io/rfprag-backend:latest \
    -t rfpragreg.azurecr.io/rfprag-backend:latest \
    backend/

# Parallel builds (if you have multiple cores)
docker build backend/ &
docker build frontend/ &
wait
```

---

## 🚀 Next Steps After Push

### 1. Deploy to Azure Container Apps

```bash
# First time deployment
cd scripts
./5-deploy-to-azure.sh
```

### 2. Update Existing Deployment

```bash
# Update running containers with new images
cd scripts
./7-update-deployment.sh
```

### 3. View Logs

```bash
# View application logs
cd scripts
./6-view-logs.sh
```

### 4. Verify Deployment

```bash
# Get application URLs
az containerapp show \
    --name rfprag-backend \
    --resource-group rfprag-rg \
    --query properties.configuration.ingress.fqdn \
    -o tsv

az containerapp show \
    --name rfprag-frontend \
    --resource-group rfprag-rg \
    --query properties.configuration.ingress.fqdn \
    -o tsv
```

---

## 📝 Complete Workflow

### Initial Deployment

```bash
# 1. Build and push images
./build-and-push.sh

# 2. Deploy to Azure
cd scripts
./5-deploy-to-azure.sh

# 3. View logs to verify
./6-view-logs.sh

# 4. Test the application
# Open the frontend URL in browser
```

### Update Existing Deployment

```bash
# 1. Make code changes
# Edit files...

# 2. Rebuild and push with new tag
./build-and-push.sh v1.0.1

# 3. Update deployment
cd scripts
./7-update-deployment.sh

# 4. Monitor logs
./6-view-logs.sh
```

### Rollback to Previous Version

```bash
# Update to use previous tag
az containerapp update \
    --name rfprag-backend \
    --resource-group rfprag-rg \
    --image rfpragreg.azurecr.io/rfprag-backend:v1.0.0

az containerapp update \
    --name rfprag-frontend \
    --resource-group rfprag-rg \
    --image rfpragreg.azurecr.io/rfprag-frontend:v1.0.0
```

---

## 🔒 Security Best Practices

### 1. Use Specific Tags in Production

```bash
# Don't use 'latest' in production
./build-and-push.sh v1.0.0

# Deploy with specific version
az containerapp update --image rfpragreg.azurecr.io/rfprag-backend:v1.0.0
```

### 2. Scan Images for Vulnerabilities

```bash
# Scan with Azure Defender (if enabled)
az acr repository show \
    --name rfpragreg \
    --image rfprag-backend:latest

# Or use Trivy
docker run --rm \
    -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image \
    rfpragreg.azurecr.io/rfprag-backend:latest
```

### 3. Clean Up Old Images

```bash
# List all tags
az acr repository show-tags \
    --name rfpragreg \
    --repository rfprag-backend \
    --output table

# Delete specific tag
az acr repository delete \
    --name rfpragreg \
    --image rfprag-backend:old-version \
    --yes
```

---

## 📊 Image Sizes

Expected image sizes:

| Image | Uncompressed | Compressed | Notes |
|-------|-------------|------------|-------|
| **Backend** | ~500-800 MB | ~200-300 MB | Python + dependencies |
| **Frontend** | ~50-100 MB | ~20-40 MB | Nginx + static files |

To reduce sizes:
- Backend: Use multi-stage builds, alpine base
- Frontend: Already optimized with multi-stage build

---

## 🎯 Summary

**Quick Command:**
```bash
./build-and-push.sh
```

**What it does:**
1. ✅ Logs into Azure Container Registry
2. ✅ Builds backend image for linux/amd64
3. ✅ Builds frontend image for linux/amd64
4. ✅ Tags images with latest + custom tag
5. ✅ Pushes to Azure Container Registry
6. ✅ Verifies upload

**Time:** ~5-15 minutes (depending on your internet and if cache is warm)

**After this:** Ready to deploy with `./scripts/5-deploy-to-azure.sh`! 🚀

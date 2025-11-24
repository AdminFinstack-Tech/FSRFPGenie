# Azure Deployment Scripts

Step-by-step scripts to deploy FS RFP Genie to Azure Container Apps.

## 📋 Prerequisites

Before running these scripts, ensure you have:

1. **Azure Account** with active subscription
   - Sign up at https://azure.microsoft.com/free/

2. **Azure CLI** installed
   ```bash
   brew update && brew install azure-cli
   ```

3. **Docker Desktop** running
   - Download from https://www.docker.com/products/docker-desktop

4. **Your OpenAI API Key** ready
   - Get from https://platform.openai.com/api-keys

## 🚀 Quick Start

Run the scripts in order:

### 1. Setup Docker Buildx (one-time setup)
```bash
cd scripts
chmod +x *.sh
./1-setup-buildx.sh
```
This configures Docker to build Linux-compatible images for Azure.

### 2. Build Images for Linux
```bash
./2-build-linux.sh
```
Builds frontend and backend images for linux/amd64 architecture.

**Time**: ~3-5 minutes

### 3. Setup Azure Resources
```bash
./3-setup-azure.sh
```
Creates:
- Resource Group
- Container Registry (ACR)
- Container Apps Environment
- Cosmos DB (MongoDB API)
- Azure Cache for Redis

**Time**: ~10-15 minutes  
**Cost**: ~$100-150/month

### 4. Push Images to ACR
```bash
./4-push-to-acr.sh
```
Uploads your Docker images to Azure Container Registry.

**Time**: ~2-3 minutes

### 5. Deploy to Azure
```bash
# IMPORTANT: Edit .env.azure first and add your OpenAI API key!
nano .env.azure  # or use your preferred editor

# Then deploy
./5-deploy-to-azure.sh
```
Deploys frontend and backend containers to Azure.

**Time**: ~5-7 minutes

### 6. View Logs
```bash
./6-view-logs.sh
```
Shows real-time logs from your deployed containers.

### 7. Update Deployment
```bash
./7-update-deployment.sh
```
Rebuilds and redeploys when you make code changes.

**Time**: ~5-7 minutes

### 8. Cleanup (Optional)
```bash
./8-cleanup-azure.sh
```
⚠️ **WARNING**: Deletes ALL Azure resources. Cannot be undone!

## 📝 Configuration

After running `./3-setup-azure.sh`, edit `.env.azure`:

```bash
# Required - Add your OpenAI key
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Optional - If using Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_KEY=your-azure-openai-key-here
```

## 🏗️ Architecture

```
Azure Container Apps
├── Frontend (nginx + Vue.js)
│   └── Port 80, External ingress
├── Backend (Flask + Python)
│   └── Port 5001, External ingress
├── Cosmos DB (MongoDB API)
│   └── Database storage
└── Redis Cache
    └── Session + caching
```

## 💰 Cost Estimate

**Development** (~$100-150/month):
- Container Apps: $30-50
- Cosmos DB: Free tier
- Redis: $16 (Basic C0)
- Container Registry: $5
- Storage: $5-10

**Production** (~$400-600/month):
- Container Apps: $150-200 (3 replicas)
- Cosmos DB: $24 (400 RU/s)
- Redis: $76 (Standard C1)
- Container Registry: $20
- Azure AI Search: $75
- Other: $20-30

## 🔍 Troubleshooting

### Build fails: "buildx: command not found"
```bash
# Update Docker Desktop to latest version
# Enable experimental features in Docker Desktop settings
```

### Azure CLI not found
```bash
brew update && brew install azure-cli
```

### ACR name conflict
Edit `3-setup-azure.sh` and change `ACR_NAME` to something unique:
```bash
ACR_NAME="rfprag$(date +%s)"  # Adds timestamp
```

### Deployment fails: "InsufficientQuota"
Try a different Azure region:
```bash
# In 3-setup-azure.sh, change:
LOCATION="westus2"  # or "westeurope", "southeastasia"
```

### Frontend can't reach backend
Check CORS settings in backend and environment variables:
```bash
az containerapp show --name rfprag-backend --resource-group rfprag-rg
```

## 📊 Monitoring

### View container status
```bash
source .env.azure
az containerapp list --resource-group $RESOURCE_GROUP -o table
```

### Check container health
```bash
az containerapp show \
    --name rfprag-backend \
    --resource-group $RESOURCE_GROUP \
    --query properties.runningStatus
```

### View recent logs
```bash
./6-view-logs.sh
```

## 🔄 CI/CD (Optional)

To set up automated deployments with GitHub Actions, see:
- `/RFPAI/AZURE_DEPLOYMENT_GUIDE.md` - Full CI/CD guide
- Create `.github/workflows/azure-deploy.yml`

## 🛟 Support

- Azure Container Apps docs: https://learn.microsoft.com/azure/container-apps/
- Cosmos DB docs: https://learn.microsoft.com/azure/cosmos-db/
- Azure CLI reference: https://learn.microsoft.com/cli/azure/

## 📦 What Gets Created

| Resource | Name | Purpose |
|----------|------|---------|
| Resource Group | `rfprag-rg` | Contains all resources |
| Container Registry | `rfpragreg` | Stores Docker images |
| Container Apps Environment | `rfprag-env` | Runtime environment |
| Container App (Frontend) | `rfprag-frontend` | Vue.js web app |
| Container App (Backend) | `rfprag-backend` | Flask API |
| Cosmos DB | `rfprag-cosmos` | MongoDB database |
| Redis Cache | `rfprag-redis` | Session + cache |

## ⏱️ Total Deployment Time

- First deployment: ~25-35 minutes
- Subsequent updates: ~5-7 minutes

## ✅ Success Checklist

After deployment:
- [ ] Frontend URL loads in browser
- [ ] Backend API responds at `/health`
- [ ] Can upload documents
- [ ] Search functionality works
- [ ] Logs show no errors
- [ ] Database connection successful

## 🎯 Next Steps

After successful deployment:
1. Configure custom domain (optional)
2. Set up monitoring with Application Insights
3. Configure auto-scaling rules
4. Set up GitHub Actions for CI/CD
5. Configure backup policies

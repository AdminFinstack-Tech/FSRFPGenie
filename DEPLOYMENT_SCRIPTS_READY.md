# ✅ Azure Deployment Scripts Created

## 🎯 What I've Prepared for You

I've created a complete set of deployment scripts to help you deploy FS RFP Genie to Azure Container Apps. Everything is ready to use!

---

## 📦 What's Been Created

### 1. Deployment Scripts (8 files)
Located in `/scripts/` directory:

| Script | Purpose | Time |
|--------|---------|------|
| `1-setup-buildx.sh` | Setup multi-platform Docker builds | 2 min |
| `2-build-linux.sh` | Build images for Linux (Azure) | 5 min |
| `3-setup-azure.sh` | Create all Azure resources | 15 min |
| `4-push-to-acr.sh` | Upload images to Azure Registry | 3 min |
| `5-deploy-to-azure.sh` | Deploy to Azure Container Apps | 7 min |
| `6-view-logs.sh` | View container logs | instant |
| `7-update-deployment.sh` | Update deployment after changes | 7 min |
| `8-cleanup-azure.sh` | Delete all Azure resources | 2 min |

**Total First Deployment**: ~30-35 minutes  
**Future Updates**: ~5-7 minutes

### 2. Documentation
- ✅ `AZURE_QUICK_START.md` - Step-by-step visual guide (this is your main guide!)
- ✅ `scripts/README.md` - Detailed script documentation
- ✅ `AZURE_DEPLOYMENT_GUIDE.md` - Comprehensive technical guide (already existed)

### 3. Configuration Template
- ✅ `.env.azure` - Will be auto-generated with your Azure credentials

---

## 🚀 How to Start

### Quick Start (Just 3 Commands!)
```bash
cd /Users/ilyasashu/RFPAI/scripts

# 1. Setup Docker for Linux builds
./1-setup-buildx.sh

# 2. Build images for Linux
./2-build-linux.sh

# 3. Create Azure resources (requires Azure login)
./3-setup-azure.sh
```

After step 3, you'll have `.env.azure` file created. **Edit it and add your OpenAI API key**, then:

```bash
# 4. Push images to Azure
./4-push-to-acr.sh

# 5. Deploy!
./5-deploy-to-azure.sh
```

**That's it!** 🎉 Your app will be live on Azure!

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:

- [ ] **Azure Account** (sign up free: https://azure.microsoft.com/free/)
- [ ] **Azure CLI installed** (`brew install azure-cli`)
- [ ] **Docker Desktop running** (you already have this ✅)
- [ ] **OpenAI API Key** ready (from https://platform.openai.com/api-keys)
- [ ] **30-40 minutes** for first deployment

---

## 💰 Cost Breakdown

### Development Environment (~$56-81/month with free tiers)
```
Container Apps (Consumption)     $30-50/month
Cosmos DB (Free Tier)            $0 (first 1000 RU/s free)
Redis Cache (Basic C0)           $16/month
Container Registry (Basic)       $5/month
Storage Account                  $5-10/month
────────────────────────────────────────────
Total                            ~$56-81/month
```

**Cost-Saving Tips**:
- ✅ Use $200 Azure free credit (30 days)
- ✅ Cosmos DB free tier covers most dev usage
- ✅ Delete resources when not in use (`./8-cleanup-azure.sh`)
- ✅ Set up auto-shutdown for after-hours

---

## 🏗️ What Gets Deployed

### Azure Resources Created
1. **Resource Group** (`rfprag-rg`)
   - Container for all resources

2. **Azure Container Registry** (`rfpragreg`)
   - Stores your Docker images
   - Similar to Docker Hub but private

3. **Container Apps Environment** (`rfprag-env`)
   - Runtime environment for containers

4. **Frontend Container App**
   - Vue.js + nginx on port 80
   - Auto-scaling: 1-5 replicas
   - External HTTPS ingress

5. **Backend Container App**
   - Flask + Python on port 5001
   - Auto-scaling: 1-3 replicas
   - External HTTPS ingress

6. **Cosmos DB** (`rfprag-cosmos`)
   - MongoDB API compatible
   - Free tier: 1000 RU/s, 25GB storage

7. **Azure Cache for Redis** (`rfprag-redis`)
   - Session management
   - Response caching
   - Basic C0 tier (250MB)

### Architecture
```
Internet (HTTPS)
    │
    ├─── Frontend Container (Vue.js)
    │    └─── https://rfprag-frontend.xxx.azurecontainerapps.io
    │
    └─── Backend Container (Flask)
         └─── https://rfprag-backend.xxx.azurecontainerapps.io
              │
              ├─── Cosmos DB (MongoDB)
              ├─── Redis Cache
              └─── Storage Account
```

---

## 📊 Script Details

### Script 1: Setup Buildx
**What it does**:
- Creates Docker Buildx builder
- Enables multi-platform builds
- Required for building Linux images on Mac

**Run once**: Yes (one-time setup)

---

### Script 2: Build for Linux
**What it does**:
- Builds frontend image for linux/amd64
- Builds backend image for linux/amd64
- Tags images as `:linux`

**Why needed**: Azure runs on Linux servers. Your current images are built for Mac (arm64/amd64) and won't work on Azure.

**Output**:
```
rfprag-frontend:linux
rfprag-backend:linux
```

---

### Script 3: Setup Azure
**What it does**:
- Creates resource group
- Creates container registry
- Creates container apps environment
- Creates Cosmos DB
- Creates Redis cache
- Saves all connection strings to `.env.azure`

**Interactive**: Yes, you'll need to:
1. Login to Azure (browser opens)
2. Confirm subscription
3. Wait ~15 minutes for resources to be created

**Output**: Creates `.env.azure` with all credentials

---

### Script 4: Push to ACR
**What it does**:
- Logs into Azure Container Registry
- Tags images with ACR URL
- Pushes images to ACR

**Requirements**: 
- Script 2 must be completed
- `.env.azure` must exist

---

### Script 5: Deploy
**What it does**:
- Deploys backend container with environment variables
- Deploys frontend container with backend URL
- Configures auto-scaling
- Sets up external ingress (HTTPS)

**⚠️ Important**: Make sure you've edited `.env.azure` with your OpenAI API key!

**Output**: Two URLs:
- Frontend: `https://rfprag-frontend.xxx.azurecontainerapps.io`
- Backend: `https://rfprag-backend.xxx.azurecontainerapps.io`

---

### Script 6: View Logs
**What it does**:
- Shows real-time logs from containers
- Helps debug issues
- Choose backend, frontend, or both

**Usage**:
```bash
./6-view-logs.sh
# Select: 1 (backend), 2 (frontend), or 3 (both)
```

---

### Script 7: Update Deployment
**What it does**:
- Rebuilds images
- Pushes to ACR
- Updates running containers
- Zero-downtime deployment

**When to use**: After making code changes

**Time**: ~5-7 minutes

---

### Script 8: Cleanup
**What it does**:
- Deletes entire resource group
- Removes all resources
- **Cannot be undone!**

**When to use**: 
- When you're done testing
- To avoid ongoing costs
- To start fresh

---

## 🔍 Monitoring Your Deployment

### Check Container Status
```bash
source .env.azure
az containerapp list --resource-group $RESOURCE_GROUP -o table
```

### View Logs
```bash
./6-view-logs.sh
```

### Check Resource Costs
```bash
az consumption usage list --output table
```

### Azure Portal
Visit https://portal.azure.com to see all resources visually

---

## 🐛 Troubleshooting

### "Docker not running"
**Solution**: Open Docker Desktop and wait for it to start

### "az command not found"
**Solution**: 
```bash
brew update && brew install azure-cli
```

### "ACR name already exists"
**Solution**: Edit `3-setup-azure.sh`, line 18:
```bash
ACR_NAME="rfprag$(date +%s)"  # Adds timestamp
```

### "InsufficientQuota"
**Solution**: Try a different region in `3-setup-azure.sh`:
```bash
LOCATION="westus2"  # or westeurope, southeastasia
```

### Frontend can't reach backend
**Solution**: Check environment variables:
```bash
az containerapp show \
    --name rfprag-frontend \
    --resource-group rfprag-rg \
    --query properties.template.containers[0].env
```

### "ImagePullBackOff" error
**Solution**: Check if images exist in ACR:
```bash
az acr repository list --name rfpragreg --output table
```

---

## 🎯 Next Steps After Deployment

### 1. Test Your Application
- ✅ Visit frontend URL
- ✅ Upload a document
- ✅ Test search functionality
- ✅ Check column mapping
- ✅ Verify templates work

### 2. Monitor Performance
```bash
./6-view-logs.sh
```

### 3. Set Up Custom Domain (Optional)
```bash
az containerapp hostname add \
    --name rfprag-frontend \
    --resource-group rfprag-rg \
    --hostname yourdomain.com
```

### 4. Set Up CI/CD (Optional)
See `AZURE_DEPLOYMENT_GUIDE.md` for GitHub Actions workflow

### 5. Configure Auto-Scaling
```bash
az containerapp update \
    --name rfprag-backend \
    --resource-group rfprag-rg \
    --min-replicas 1 \
    --max-replicas 10
```

---

## 📚 Additional Documentation

1. **AZURE_QUICK_START.md** ⭐ Start here!
   - Visual step-by-step guide
   - Screenshots and examples
   - Troubleshooting

2. **scripts/README.md**
   - Detailed script documentation
   - Cost estimates
   - Monitoring commands

3. **AZURE_DEPLOYMENT_GUIDE.md**
   - Comprehensive technical guide
   - CI/CD setup
   - Production best practices

---

## ✅ Success Criteria

Your deployment is successful when:
- [ ] All 5 scripts complete without errors
- [ ] Frontend URL loads in browser
- [ ] Backend API responds (check `/health` endpoint)
- [ ] Can upload documents
- [ ] Search works
- [ ] No errors in logs
- [ ] Database connection successful

---

## 🎓 What You've Accomplished

By completing this deployment, you've:
1. ✅ Built multi-platform Docker images
2. ✅ Created production Azure infrastructure
3. ✅ Deployed a full-stack application
4. ✅ Set up auto-scaling containers
5. ✅ Configured managed database (Cosmos DB)
6. ✅ Set up caching with Redis
7. ✅ Enabled HTTPS automatically
8. ✅ Created a reproducible deployment process

---

## 🚀 Ready to Deploy?

Start with the **AZURE_QUICK_START.md** guide:
```bash
cat /Users/ilyasashu/RFPAI/AZURE_QUICK_START.md
```

Or jump right in:
```bash
cd /Users/ilyasashu/RFPAI/scripts
./1-setup-buildx.sh
```

---

## 📞 Getting Help

If you encounter issues:
1. Check **AZURE_QUICK_START.md** troubleshooting section
2. Run `./6-view-logs.sh` to see what's happening
3. Check Azure Portal for resource status
4. Review script output - errors are descriptive

---

**Good luck! 🎉 Your Azure deployment adventure starts now!**

---

## 📋 File Checklist

All files created and ready:
- ✅ `/scripts/1-setup-buildx.sh` (executable)
- ✅ `/scripts/2-build-linux.sh` (executable)
- ✅ `/scripts/3-setup-azure.sh` (executable)
- ✅ `/scripts/4-push-to-acr.sh` (executable)
- ✅ `/scripts/5-deploy-to-azure.sh` (executable)
- ✅ `/scripts/6-view-logs.sh` (executable)
- ✅ `/scripts/7-update-deployment.sh` (executable)
- ✅ `/scripts/8-cleanup-azure.sh` (executable)
- ✅ `/scripts/README.md`
- ✅ `/AZURE_QUICK_START.md` (⭐ START HERE)
- ✅ This summary document

**Everything is ready for deployment!** 🚀

# 🚀 Azure Deployment - Quick Start Guide

## ✅ You're Ready to Deploy!

I've created 8 deployment scripts that will guide you step-by-step through deploying FS RFP Genie to Azure Container Apps.

---

## 📋 What You Need (5 minutes)

### 1. Azure Account
- Sign up (free): https://azure.microsoft.com/free/
- Gives you $200 credit for 30 days

### 2. Install Azure CLI
```bash
brew update && brew install azure-cli
```

### 3. Your OpenAI API Key
- Get from: https://platform.openai.com/api-keys
- Keep it handy - you'll add it in step 5

### 4. Docker Desktop
- Already running ✅ (since your local containers work)

---

## 🎯 Deployment Steps

### Step 1: Setup Multi-Platform Build (2 minutes)
```bash
cd /Users/ilyasashu/RFPAI/scripts
./1-setup-buildx.sh
```

**What it does**: Configures Docker to build Linux images (required for Azure)

**Expected output**:
```
✅ Docker is running
📦 Creating multiplatform builder...
🚀 Bootstrapping builder...
✅ Docker Buildx setup complete!
```

---

### Step 2: Build for Linux Platform (5 minutes)
```bash
./2-build-linux.sh
```

**What it does**: Rebuilds your frontend and backend for Linux (Azure uses Linux servers)

**Expected output**:
```
📦 Building Frontend for Linux...
[+] Building 45.2s (18/18) FINISHED
📦 Building Backend for Linux...
[+] Building 32.1s (15/15) FINISHED
✅ Linux builds complete!

rfprag-frontend   linux     abc123def456
rfprag-backend    linux     789ghi012jkl
```

---

### Step 3: Create Azure Resources (15 minutes)
```bash
./3-setup-azure.sh
```

**What it does**: Creates all Azure resources you need

**You'll be asked**:
1. Login to Azure (opens browser)
2. Confirm your subscription
3. Wait while resources are created

**Creates**:
- ✅ Resource Group (`rfprag-rg`)
- ✅ Container Registry (stores your images)
- ✅ Container Apps Environment (runs your containers)
- ✅ Cosmos DB with MongoDB API (your database)
- ✅ Azure Redis Cache (for sessions)

**Expected output**:
```
✅ Azure resources created successfully!

📝 Save these connection details:
ACR_LOGIN_SERVER=rfpragreg.azurecr.io
COSMOS_CONNECTION=mongodb://...
REDIS_CONNECTION=rediss://...

✅ Configuration saved to .env.azure
```

**⚠️ IMPORTANT**: After this step completes, edit `.env.azure` and add your OpenAI key:
```bash
nano .env.azure  # or: code .env.azure

# Find this line:
OPENAI_API_KEY=your-openai-api-key-here

# Replace with your actual key:
OPENAI_API_KEY=sk-proj-abc123...
```

---

### Step 4: Push Images to Azure (3 minutes)
```bash
./4-push-to-acr.sh
```

**What it does**: Uploads your Docker images to Azure Container Registry

**Expected output**:
```
🔐 Logging in to Azure Container Registry...
🏷️  Tagging images...
📤 Pushing frontend image...
📤 Pushing backend image...
✅ Images pushed successfully!

Images in registry:
NAME              UPDATED
rfprag-frontend   2024-11-11T21:45:00Z
rfprag-backend    2024-11-11T21:46:00Z
```

---

### Step 5: Deploy to Azure (7 minutes)
```bash
./5-deploy-to-azure.sh
```

**What it does**: Deploys your containers to Azure Container Apps

**Expected output**:
```
📦 Deploying Backend Container App...
✅ Backend URL: https://rfprag-backend.xxx.azurecontainerapps.io

📦 Deploying Frontend Container App...

✅ Deployment Complete!

🌐 Frontend URL: https://rfprag-frontend.xxx.azurecontainerapps.io
🔧 Backend URL:  https://rfprag-backend.xxx.azurecontainerapps.io
```

**🎉 You're done!** Visit the Frontend URL to see your deployed app!

---

## 🔍 After Deployment

### View Logs
```bash
./6-view-logs.sh
```
Shows real-time logs from your containers. Choose:
- 1 = Backend logs only
- 2 = Frontend logs only  
- 3 = Both (streaming)

### Update Your App
When you make code changes:
```bash
./7-update-deployment.sh
```
This rebuilds, pushes, and redeploys everything automatically.

### Delete Everything
If you want to remove all Azure resources:
```bash
./8-cleanup-azure.sh
```
⚠️ **WARNING**: This deletes everything and cannot be undone!

---

## 💰 Costs

**Development Setup** (~$100-150/month):
- Container Apps: $30-50
- Cosmos DB: Free tier (first 1000 RU/s free)
- Redis Cache: $16 (Basic C0)
- Container Registry: $5
- Storage: $5-10
- **Total**: ~$56-81/month (with free Cosmos tier)

**Cost-Saving Tips**:
1. Use Azure Free Tier (includes $200 credit for 30 days)
2. Delete resources when not in use (`./8-cleanup-azure.sh`)
3. Set up auto-pause for Container Apps during off-hours
4. Use Cosmos DB free tier (1000 RU/s, 25GB storage)

---

## 🐛 Common Issues

### "Docker not running"
- Open Docker Desktop
- Wait for it to fully start
- Run script again

### "az command not found"
```bash
brew install azure-cli
```

### "ACR name already exists"
Edit `3-setup-azure.sh`, line 18:
```bash
ACR_NAME="rfprag$(whoami)reg"  # Makes it unique
```

### "InsufficientQuota" error
Try a different Azure region in `3-setup-azure.sh`, line 17:
```bash
LOCATION="westus2"  # or "westeurope", "southeastasia"
```

### Frontend shows "Cannot connect to backend"
Check if both containers are running:
```bash
source .env.azure
az containerapp list --resource-group $RESOURCE_GROUP -o table
```

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────┐
│         Internet (HTTPS)                    │
└──────────────┬──────────────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼─────────┐  ┌───▼──────────┐
│   Frontend    │  │   Backend    │
│ (Vue + nginx) │  │   (Flask)    │
│  Port 80      │  │  Port 5001   │
│  1 replica    │  │  1-3 replicas│
└───────────────┘  └───┬──────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
    ┌─────▼────┐  ┌───▼────┐  ┌───▼────┐
    │ Cosmos DB│  │ Redis  │  │  ACR   │
    │ (MongoDB)│  │ Cache  │  │ Images │
    │ Free Tier│  │ Basic  │  │ Basic  │
    └──────────┘  └────────┘  └────────┘
```

---

## ✅ Success Checklist

After running all scripts:
- [ ] Step 1 completed: Buildx setup
- [ ] Step 2 completed: Linux images built
- [ ] Step 3 completed: Azure resources created
- [ ] ✏️ Edited `.env.azure` with OpenAI key
- [ ] Step 4 completed: Images pushed to ACR
- [ ] Step 5 completed: Deployed to Azure
- [ ] 🌐 Frontend URL opens in browser
- [ ] ✅ Can log in to the application
- [ ] ✅ Can upload a document
- [ ] ✅ Search functionality works

---

## 🎓 What You Learned

By running these scripts, you've:
1. ✅ Built multi-platform Docker images
2. ✅ Created Azure Container Registry
3. ✅ Set up Azure Container Apps
4. ✅ Deployed Cosmos DB (MongoDB API)
5. ✅ Configured Redis Cache
6. ✅ Deployed a full-stack application to Azure
7. ✅ Set up environment variables and secrets
8. ✅ Enabled auto-scaling (1-3 replicas)

---

## 🚀 Ready to Start?

```bash
cd /Users/ilyasashu/RFPAI/scripts
./1-setup-buildx.sh
```

**Total time**: ~30-35 minutes for first deployment  
**Updates**: ~5-7 minutes with `./7-update-deployment.sh`

---

## 📚 Additional Resources

- **Full Guide**: `/RFPAI/AZURE_DEPLOYMENT_GUIDE.md`
- **Scripts README**: `/RFPAI/scripts/README.md`
- **Azure Docs**: https://learn.microsoft.com/azure/container-apps/
- **Docker Buildx**: https://docs.docker.com/buildx/working-with-buildx/

---

## 🆘 Need Help?

If you run into issues:
1. Check the **Common Issues** section above
2. Run `./6-view-logs.sh` to see container logs
3. Check Azure Portal: https://portal.azure.com
4. Review script output carefully - error messages are descriptive

---

**Good luck with your deployment! 🎉**

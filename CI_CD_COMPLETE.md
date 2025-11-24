# 🎉 GitHub to Azure CI/CD - Complete Setup

## ✅ What Has Been Created

Your repository now has a complete CI/CD pipeline from GitHub to Azure! Here's what was added:

### 1. GitHub Actions Workflow
**File**: `.github/workflows/azure-deploy.yml`

This workflow automatically:
- Builds Docker images for backend and frontend
- Pushes images to Azure Container Registry
- Deploys to Azure Container Apps
- Runs on every push to `main` branch
- Can be triggered manually from GitHub Actions UI

### 2. Comprehensive Setup Guide
**File**: `CI_CD_SETUP_GUIDE.md`

Complete step-by-step instructions including:
- Azure resource creation commands
- Service Principal setup
- GitHub Secrets configuration
- Troubleshooting common issues
- Security best practices

### 3. Automated Setup Script
**File**: `scripts/setup-azure-cicd.sh`

One-command Azure setup that creates:
- Resource Group
- Azure Container Registry
- Container Apps Environment
- Backend Container App
- Frontend Container App
- Service Principal for GitHub Actions

Usage:
```bash
./scripts/setup-azure-cicd.sh
```

### 4. Quick Reference Checklist
**File**: `CI_CD_CHECKLIST.md`

Interactive checklist to ensure:
- All Azure resources are created
- GitHub Secrets are configured
- Deployment is successful
- Applications are working

## 🚀 Quick Start (3 Steps)

### Step 1: Set Up Azure Resources

Run the automated setup script:
```bash
# Make sure you're logged in to Azure
az login

# Run the setup script
./scripts/setup-azure-cicd.sh
```

**Important**: Copy the Service Principal JSON output!

### Step 2: Configure GitHub Secrets

Go to: **GitHub Repository → Settings → Secrets and variables → Actions**

Add these secrets:

1. **AZURE_CREDENTIALS** - The JSON from Step 1
2. **AZURE_OPENAI_ENDPOINT** - Your Azure OpenAI endpoint
3. **AZURE_OPENAI_API_KEY** - Your Azure OpenAI key
4. **AZURE_OPENAI_DEPLOYMENT_NAME** - Chat model deployment name
5. **AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME** - Embedding model name
6. **MONGO_URI** - MongoDB connection string
7. **AZURE_STORAGE_CONNECTION_STRING** - Storage connection string
8. **AZURE_STORAGE_CONTAINER_NAME** - Storage container name

### Step 3: Deploy!

```bash
# Push to trigger deployment
git push origin main

# Or trigger manually from GitHub Actions UI
```

Watch deployment at: **GitHub Repository → Actions tab**

## 📊 What Happens on Every Push

```
GitHub Push → main branch
    ↓
GitHub Actions Triggered
    ↓
Build Backend Docker Image
    ↓
Build Frontend Docker Image
    ↓
Push Both Images to Azure Container Registry
    ↓
Deploy Backend to Azure Container Apps
    ↓
Deploy Frontend to Azure Container Apps
    ↓
Verify Deployment Success
    ↓
✅ Live Application Updated!
```

## 🎯 Deployment Features

✅ **Automated**: Push code → Automatic deployment
✅ **Zero Downtime**: Container Apps handles rolling updates
✅ **Scalable**: Auto-scales based on load (1-3 replicas backend, 1-5 frontend)
✅ **Secure**: Secrets managed via GitHub Secrets
✅ **Fast**: Parallel build and deployment
✅ **Monitored**: Full logging and diagnostics
✅ **Cost-Effective**: Consumption-based pricing

## 📍 After First Deployment

Get your application URLs:

```bash
# Backend URL
az containerapp show --name rfpai-backend --resource-group rfpai-rg \
  --query properties.configuration.ingress.fqdn -o tsv

# Frontend URL
az containerapp show --name rfpai-frontend --resource-group rfpai-rg \
  --query properties.configuration.ingress.fqdn -o tsv
```

Test your backend:
```bash
curl https://YOUR-BACKEND-URL/health
```

## 🔍 Monitoring & Logs

### View in Azure Portal
1. Go to Azure Portal → Container Apps
2. Select your app
3. Click "Log stream" for real-time logs

### View via CLI
```bash
# Backend logs
az containerapp logs show --name rfpai-backend --resource-group rfpai-rg --follow

# Frontend logs
az containerapp logs show --name rfpai-frontend --resource-group rfpai-rg --follow
```

### View in GitHub
1. Go to GitHub → Actions tab
2. Click on any workflow run
3. View detailed build and deployment logs

## 💡 Pro Tips

### Manual Deployment
Trigger deployment without pushing code:
1. Go to GitHub → Actions
2. Select "Deploy to Azure Container Apps"
3. Click "Run workflow"

### Environment Variables
Update environment variables without redeploying:
```bash
az containerapp update \
  --name rfpai-backend \
  --resource-group rfpai-rg \
  --set-env-vars NEW_VAR=value
```

### Scale Settings
Adjust replica counts:
```bash
az containerapp update \
  --name rfpai-backend \
  --resource-group rfpai-rg \
  --min-replicas 2 \
  --max-replicas 5
```

### View Deployment History
```bash
az containerapp revision list \
  --name rfpai-backend \
  --resource-group rfpai-rg \
  --output table
```

## 🔐 Security Notes

⚠️ **IMPORTANT**: The Azure OpenAI keys that were previously committed are compromised. 

**You MUST rotate them**:
1. Go to Azure Portal → Azure OpenAI
2. Click "Keys and Endpoint"
3. Regenerate keys
4. Update GitHub Secrets with new keys

## 💰 Cost Estimate

**Development (with auto-scale to zero)**:
- ~$50-100/month

**Production (always running)**:
- ~$200-400/month

Set up cost alerts:
```bash
az consumption budget create \
  --resource-group rfpai-rg \
  --budget-name monthly-budget \
  --amount 100 \
  --time-grain Monthly \
  --time-period start-date=2025-11-01
```

## 🆘 Troubleshooting

### Deployment Fails
1. Check GitHub Actions logs for errors
2. Verify all secrets are configured
3. Check Azure Portal → Container Apps → Diagnostics

### Container Crashes
1. View logs: `az containerapp logs show --name rfpai-backend --resource-group rfpai-rg`
2. Check environment variables
3. Verify MongoDB and Azure OpenAI connections

### Can't Access Application
1. Check ingress is enabled: Azure Portal → Container App → Ingress
2. Verify container is healthy: Check revision status
3. Test backend URL directly

## 📚 Documentation Files

- **CI_CD_SETUP_GUIDE.md** - Detailed setup instructions
- **CI_CD_CHECKLIST.md** - Step-by-step verification checklist
- **scripts/setup-azure-cicd.sh** - Automated Azure setup
- **.github/workflows/azure-deploy.yml** - GitHub Actions workflow

## 🎊 Success Criteria

Your CI/CD is working when:

✅ Push to main triggers deployment
✅ GitHub Actions workflow completes successfully
✅ Applications are accessible via HTTPS
✅ Backend health check passes
✅ Frontend loads correctly
✅ All features work (upload, search, Q&A)

## 🚀 Next Steps

1. **Set up staging environment** - Separate branch for testing
2. **Add automated tests** - Run tests before deployment
3. **Configure custom domain** - Use your own domain
4. **Enable Application Insights** - Advanced monitoring
5. **Set up alerts** - Get notified of issues
6. **Implement blue-green deployment** - Advanced zero-downtime

## 📞 Support

If you need help:

1. Check `CI_CD_SETUP_GUIDE.md` for detailed instructions
2. Review `CI_CD_CHECKLIST.md` to ensure all steps completed
3. View GitHub Actions logs for build errors
4. Check Azure Portal diagnostics for runtime errors

## 🎓 Learn More

- [Azure Container Apps Docs](https://learn.microsoft.com/azure/container-apps/)
- [GitHub Actions Docs](https://docs.github.com/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Created**: November 24, 2025
**Status**: ✅ Ready to Deploy
**Version**: 1.0

**Your CI/CD pipeline is ready! Push to main to deploy!** 🚀

# GitHub to Azure CI/CD - Quick Checklist

Use this checklist to ensure you've completed all steps for CI/CD setup.

## ☑️ Pre-Deployment Checklist

### Azure Setup
- [ ] Azure account with active subscription
- [ ] Azure CLI installed and logged in (`az login`)
- [ ] Resource group created
- [ ] Azure Container Registry created
- [ ] Container Apps Environment created
- [ ] Backend Container App created
- [ ] Frontend Container App created
- [ ] Container Registry credentials configured
- [ ] Service Principal created for GitHub Actions

### GitHub Configuration
- [ ] Repository admin access
- [ ] GitHub Secrets configured:
  - [ ] `AZURE_CREDENTIALS` (Service Principal JSON)
  - [ ] `AZURE_OPENAI_ENDPOINT`
  - [ ] `AZURE_OPENAI_API_KEY`
  - [ ] `AZURE_OPENAI_DEPLOYMENT_NAME`
  - [ ] `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`
  - [ ] `MONGO_URI`
  - [ ] `AZURE_STORAGE_CONNECTION_STRING`
  - [ ] `AZURE_STORAGE_CONTAINER_NAME`

### Code Repository
- [ ] `.github/workflows/azure-deploy.yml` file created
- [ ] Workflow variables match your Azure resource names
- [ ] Dockerfiles exist for backend and frontend
- [ ] `.gitignore` configured to exclude secrets

## 🚀 Quick Setup Commands

### Option 1: Automated Setup (Recommended)
```bash
# Run the setup script
./scripts/setup-azure-cicd.sh

# Follow the prompts and save the Service Principal JSON
```

### Option 2: Manual Setup
```bash
# See CI_CD_SETUP_GUIDE.md for detailed manual steps
```

## 📋 Post-Deployment Verification

After pushing to GitHub:

- [ ] GitHub Actions workflow triggered
- [ ] Build phase completed successfully
- [ ] Images pushed to Azure Container Registry
- [ ] Backend deployed successfully
- [ ] Frontend deployed successfully
- [ ] Backend URL accessible (https://...)
- [ ] Frontend URL accessible (https://...)
- [ ] Backend health check passes
- [ ] Frontend can communicate with backend
- [ ] MongoDB connection working
- [ ] Azure OpenAI integration working
- [ ] File upload to Azure Storage working

## 🔍 Testing Commands

```bash
# Get deployment URLs
az containerapp show --name rfpai-backend --resource-group rfpai-rg --query properties.configuration.ingress.fqdn -o tsv
az containerapp show --name rfpai-frontend --resource-group rfpai-rg --query properties.configuration.ingress.fqdn -o tsv

# Test backend health
curl https://YOUR-BACKEND-URL/health

# View backend logs
az containerapp logs show --name rfpai-backend --resource-group rfpai-rg --follow

# View frontend logs
az containerapp logs show --name rfpai-frontend --resource-group rfpai-rg --follow

# List images in ACR
az acr repository list --name rfpaiacr --output table
```

## ⚠️ Common Issues

### Build Fails
- [ ] Check Dockerfile syntax
- [ ] Verify all dependencies are in requirements.txt / package.json
- [ ] Check GitHub Actions logs for errors

### Deployment Fails
- [ ] Verify AZURE_CREDENTIALS is correct JSON
- [ ] Check service principal has contributor role
- [ ] Ensure resource names match in workflow file

### Container Crashes
- [ ] Check environment variables are set correctly
- [ ] View container logs for error messages
- [ ] Verify MongoDB connection string
- [ ] Check Azure OpenAI endpoint and keys

### Image Pull Fails
- [ ] Verify ACR credentials are configured
- [ ] Check image was pushed successfully
- [ ] Run: `az acr repository list --name rfpaiacr`

## 💰 Cost Monitoring

- [ ] Set up Azure Cost Management alerts
- [ ] Monitor daily spend in Azure Portal
- [ ] Review Container Apps scaling settings
- [ ] Consider scale-to-zero for non-production

## 🔐 Security Checklist

- [ ] All secrets stored in GitHub Secrets (not in code)
- [ ] Azure OpenAI keys rotated after previous exposure
- [ ] Service Principal has minimal required permissions
- [ ] ACR admin access limited
- [ ] Container Apps ingress properly configured
- [ ] MongoDB uses strong authentication
- [ ] Azure Storage uses secure connection strings

## 📚 Reference

- Full Guide: `CI_CD_SETUP_GUIDE.md`
- Workflow File: `.github/workflows/azure-deploy.yml`
- Setup Script: `scripts/setup-azure-cicd.sh`
- Azure Deployment Guide: `AZURE_DEPLOYMENT_GUIDE.md`

## 🎯 Success Criteria

Your CI/CD is working when:

1. ✅ Push to `main` triggers automatic deployment
2. ✅ Both containers deploy without errors
3. ✅ Applications are accessible via HTTPS
4. ✅ All features work (upload, search, Q&A)
5. ✅ Zero downtime during updates
6. ✅ Logs show healthy application state

---

**Last Updated**: November 24, 2025

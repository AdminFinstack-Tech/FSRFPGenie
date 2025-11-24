# GitHub to Azure CI/CD Setup Guide

## 🎯 Overview

This guide walks you through setting up automated CI/CD from GitHub to Azure Container Apps using GitHub Actions.

## 📋 Prerequisites

- Azure subscription with appropriate permissions
- GitHub repository with admin access
- Azure CLI installed locally
- Docker installed (for local testing)

## 🏗️ Architecture

```
GitHub (Push to main) 
    ↓
GitHub Actions Workflow
    ↓
Build Docker Images (Backend + Frontend)
    ↓
Push to Azure Container Registry
    ↓
Deploy to Azure Container Apps
    ↓
Verify Deployment
```

## 🚀 Step-by-Step Setup

### Step 1: Create Azure Resources

First, create all required Azure resources. Run these commands in Azure Cloud Shell or your terminal:

```bash
# Set variables (customize these)
RESOURCE_GROUP="rfpai-rg"
LOCATION="eastus"
ACR_NAME="rfpaiacr"
ENV_NAME="rfpai-env"
BACKEND_APP="rfpai-backend"
FRONTEND_APP="rfpai-frontend"

# Login to Azure
az login

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Create Container Apps Environment
az containerapp env create \
  --name $ENV_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Create Backend Container App
az containerapp create \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --target-port 5001 \
  --ingress external \
  --registry-server $ACR_NAME.azurecr.io \
  --cpu 1.0 \
  --memory 2.0Gi \
  --min-replicas 1 \
  --max-replicas 3

# Create Frontend Container App
az containerapp create \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --target-port 80 \
  --ingress external \
  --registry-server $ACR_NAME.azurecr.io \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 1 \
  --max-replicas 5
```

### Step 2: Create Azure Service Principal

Create a service principal for GitHub Actions to authenticate with Azure:

```bash
# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-rfpai" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth
```

**⚠️ IMPORTANT**: Copy the entire JSON output. You'll need it in the next step.

The output should look like:
```json
{
  "clientId": "xxxx",
  "clientSecret": "xxxx",
  "subscriptionId": "xxxx",
  "tenantId": "xxxx",
  ...
}
```

### Step 3: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets:

#### Required Secrets:

1. **AZURE_CREDENTIALS**
   - Value: The entire JSON output from Step 2

2. **AZURE_OPENAI_ENDPOINT**
   - Value: `https://your-openai-resource.openai.azure.com/`
   - Get from Azure Portal → OpenAI Resource → Keys and Endpoint

3. **AZURE_OPENAI_API_KEY**
   - Value: Your Azure OpenAI API key
   - Get from Azure Portal → OpenAI Resource → Keys and Endpoint

4. **AZURE_OPENAI_DEPLOYMENT_NAME**
   - Value: Your chat deployment name (e.g., `gpt-4o`)

5. **AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME**
   - Value: Your embedding deployment name (e.g., `text-embedding-ada-002`)

6. **MONGO_URI**
   - Value: Your MongoDB connection string
   - Format: `mongodb://username:password@host:port/database?options`
   - For Cosmos DB: Get from Azure Portal → Cosmos DB → Connection String

7. **AZURE_STORAGE_CONNECTION_STRING**
   - Value: Your Azure Storage connection string
   - Get from Azure Portal → Storage Account → Access keys

8. **AZURE_STORAGE_CONTAINER_NAME**
   - Value: Container name for document storage (e.g., `documents`)

### Step 4: Update Workflow Variables (Optional)

If you used different names for your Azure resources, update these variables in `.github/workflows/azure-deploy.yml`:

```yaml
env:
  AZURE_RESOURCE_GROUP: rfpai-rg          # Your resource group name
  AZURE_CONTAINER_REGISTRY: rfpaiacr      # Your ACR name (without .azurecr.io)
  CONTAINER_APP_BACKEND: rfpai-backend    # Your backend app name
  CONTAINER_APP_FRONTEND: rfpai-frontend  # Your frontend app name
  CONTAINER_APP_ENVIRONMENT: rfpai-env    # Your environment name
```

### Step 5: Configure Container Registry Access

Grant Container Apps access to pull from ACR:

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Update backend container app with registry credentials
az containerapp registry set \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --server $ACR_NAME.azurecr.io \
  --username $ACR_USERNAME \
  --password $ACR_PASSWORD

# Update frontend container app with registry credentials
az containerapp registry set \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --server $ACR_NAME.azurecr.io \
  --username $ACR_USERNAME \
  --password $ACR_PASSWORD
```

### Step 6: Test the CI/CD Pipeline

1. Commit and push the workflow files to your `main` branch:

```bash
git add .github/
git commit -m "Add Azure CI/CD workflow"
git push origin main
```

2. Watch the deployment:
   - Go to GitHub → **Actions** tab
   - You should see the workflow running
   - Click on it to see detailed logs

3. Get your deployment URLs:

```bash
# Get backend URL
az containerapp show \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv

# Get frontend URL
az containerapp show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv
```

## 🔧 Workflow Behavior

The CI/CD pipeline will automatically:

1. **Trigger on**:
   - Push to `main` branch
   - Manual trigger from GitHub Actions UI

2. **Build Phase**:
   - Build Docker images for backend and frontend
   - Tag with both commit SHA and `latest`
   - Push to Azure Container Registry

3. **Deploy Phase** (parallel):
   - Deploy backend with all environment variables
   - Deploy frontend

4. **Verify Phase**:
   - Check deployments
   - Display URLs

## 🔍 Monitoring and Debugging

### View Logs in Azure Portal

1. Go to Azure Portal → Container Apps → Your App
2. Click **Log stream** or **Logs** for real-time monitoring

### View Logs via CLI

```bash
# Backend logs
az containerapp logs show \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --follow

# Frontend logs
az containerapp logs show \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --follow
```

### Common Issues and Solutions

#### 1. **Deployment fails with "Image pull failed"**
- Check ACR credentials are correctly configured
- Verify image was successfully pushed to ACR
- Run: `az acr repository list --name $ACR_NAME`

#### 2. **Backend container crashes**
- Check environment variables are set correctly
- View logs: `az containerapp logs show --name $BACKEND_APP --resource-group $RESOURCE_GROUP`
- Verify MongoDB connection string

#### 3. **Frontend can't reach backend**
- Check backend URL is accessible
- Update frontend environment variables with correct backend URL
- Check CORS settings in backend

#### 4. **GitHub Actions fails with authentication error**
- Verify AZURE_CREDENTIALS secret is correct
- Check service principal has correct permissions
- Ensure subscription ID is correct

## 🔄 Making Updates

After initial setup, the workflow will automatically:

1. **On every push to main**:
   - Build new images
   - Deploy to Azure
   - Zero-downtime deployment (Container Apps handles this)

2. **Manual deployment**:
   - Go to Actions tab
   - Select "Deploy to Azure Container Apps"
   - Click "Run workflow"

## 🔐 Security Best Practices

1. **Never commit secrets** to the repository
2. **Rotate Azure OpenAI keys** that were previously exposed
3. **Use Azure Key Vault** for production (optional enhancement)
4. **Enable Azure AD authentication** for Container Apps (production)
5. **Restrict ACR access** to specific IPs or networks
6. **Enable container scanning** in ACR for vulnerabilities

## 📊 Cost Optimization

- **Consumption plan**: Pay only for what you use
- **Scale to zero**: Frontend can scale to 0 replicas when idle
- **Use Basic ACR**: Sufficient for small-medium projects
- **Monitor costs**: Set up Azure Cost Management alerts

## 🎉 Next Steps

1. **Set up custom domain**: Configure your own domain with SSL
2. **Add Application Insights**: Monitor performance and errors
3. **Configure auto-scaling**: Based on HTTP requests or CPU
4. **Set up staging environment**: Test before production
5. **Add health checks**: Ensure containers are healthy
6. **Implement blue-green deployment**: For zero-downtime updates

## 📚 Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/azure/container-apps/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Azure Container Registry Documentation](https://learn.microsoft.com/azure/container-registry/)
- [Troubleshooting Guide](https://learn.microsoft.com/azure/container-apps/troubleshooting)

## 🆘 Support

If you encounter issues:

1. Check GitHub Actions logs for detailed error messages
2. View Azure Container Apps logs
3. Verify all secrets are correctly configured
4. Check Azure resource quotas and limits
5. Review Azure Portal → Container Apps → Diagnostics

---

**Created**: November 24, 2025
**Last Updated**: November 24, 2025
**Version**: 1.0

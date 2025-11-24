# Azure Container Apps Deployment Guide

## 📋 Prerequisites

1. **Azure Account** with active subscription
2. **Azure CLI** installed (`az --version`)
3. **Docker** installed and running
4. **GitHub Account** (for CI/CD)

## 💰 Cost Estimation (Monthly USD)

### Development Environment (~$100-150/month)
```
✅ Container Apps (Consumption Plan)    $30-50
✅ Azure Cosmos DB (Free Tier)          $0
✅ Azure Cache for Redis (Basic)        $16
✅ Container Registry (Basic)           $5
✅ Storage Account                      $5-10
✅ Application Insights                 $2-5
```

### Production Environment (~$400-600/month)
```
✅ Container Apps (3 replicas)          $150-200
✅ Azure Cosmos DB (400 RU/s)           $24
✅ Azure Cache for Redis (Standard C1)  $76
✅ Container Registry (Standard)        $20
✅ Storage Account (Hot tier)           $20-30
✅ Application Insights (5GB)           $10-15
✅ Azure AI Search (Basic)              $75
✅ Virtual Network                      $10-20
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Azure Front Door                    │
│              (SSL/CDN/WAF - Optional)               │
└──────────────────┬──────────────────────────────────┘
                   │
      ┌────────────┴────────────┐
      │                         │
┌─────▼──────┐          ┌──────▼──────┐
│  Frontend  │          │   Backend   │
│ Container  │◄────────►│  Container  │
│    App     │          │     App     │
└────────────┘          └──────┬──────┘
                               │
                    ┌──────────┼──────────┐
                    │          │          │
              ┌─────▼────┐ ┌──▼────┐ ┌──▼────────┐
              │  Celery  │ │ Cosmos│ │   Redis   │
              │ Container│ │   DB  │ │   Cache   │
              └──────────┘ └───────┘ └───────────┘
                    │
              ┌─────▼────────┐
              │   Storage    │
              │   Account    │
              └──────────────┘
```

## 🚀 Deployment Steps

### Step 1: Set Up Azure Resources

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="rfpai-rg"
LOCATION="eastus"
ACR_NAME="rfpaiacr"
ENV_NAME="rfpai-env"
APP_NAME="rfpai"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 2: Create Container Registry

```bash
# Create Azure Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Login to ACR
az acr login --name $ACR_NAME

# Get login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
```

### Step 3: Build and Push Images

```bash
# Tag and push backend
docker tag rfpai-backend:latest $ACR_LOGIN_SERVER/rfpai-backend:latest
docker push $ACR_LOGIN_SERVER/rfpai-backend:latest

# Tag and push frontend
docker tag rfpai-frontend:latest $ACR_LOGIN_SERVER/rfpai-frontend:latest
docker push $ACR_LOGIN_SERVER/rfpai-frontend:latest

# Tag and push celery
docker tag rfpai-celery:latest $ACR_LOGIN_SERVER/rfpai-celery:latest
docker push $ACR_LOGIN_SERVER/rfpai-celery:latest
```

### Step 4: Create Azure Cosmos DB (MongoDB API)

```bash
# Create Cosmos DB account
az cosmosdb create \
  --name $APP_NAME-cosmos \
  --resource-group $RESOURCE_GROUP \
  --kind MongoDB \
  --server-version 6.0 \
  --default-consistency-level Session \
  --locations regionName=$LOCATION failoverPriority=0 \
  --enable-free-tier true

# Create database
az cosmosdb mongodb database create \
  --account-name $APP_NAME-cosmos \
  --resource-group $RESOURCE_GROUP \
  --name rfprag

# Get connection string
COSMOS_CONNECTION=$(az cosmosdb keys list \
  --name $APP_NAME-cosmos \
  --resource-group $RESOURCE_GROUP \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" \
  --output tsv)
```

### Step 5: Create Azure Cache for Redis

```bash
# Create Redis cache
az redis create \
  --name $APP_NAME-redis \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Basic \
  --vm-size c1 \
  --enable-non-ssl-port

# Get Redis connection string
REDIS_KEY=$(az redis list-keys \
  --name $APP_NAME-redis \
  --resource-group $RESOURCE_GROUP \
  --query primaryKey \
  --output tsv)

REDIS_HOST=$(az redis show \
  --name $APP_NAME-redis \
  --resource-group $RESOURCE_GROUP \
  --query hostName \
  --output tsv)

REDIS_URL="redis://:$REDIS_KEY@$REDIS_HOST:6379/0"
```

### Step 6: Create Storage Account

```bash
# Create storage account
az storage account create \
  --name ${APP_NAME}storage \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS

# Create blob container for uploads
az storage container create \
  --name uploads \
  --account-name ${APP_NAME}storage \
  --public-access off

# Get storage connection string
STORAGE_CONNECTION=$(az storage account show-connection-string \
  --name ${APP_NAME}storage \
  --resource-group $RESOURCE_GROUP \
  --output tsv)
```

### Step 7: Create Container Apps Environment

```bash
# Create Container Apps environment
az containerapp env create \
  --name $ENV_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 8: Deploy Backend Container App

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv)

# Deploy backend
az containerapp create \
  --name rfpai-backend \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image $ACR_LOGIN_SERVER/rfpai-backend:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 5000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 1.0 \
  --memory 2.0Gi \
  --env-vars \
    "MONGO_URI=$COSMOS_CONNECTION" \
    "REDIS_URL=$REDIS_URL" \
    "VECTOR_DB_URL=http://rfpai-qdrant" \
    "FLASK_ENV=production"
```

### Step 9: Deploy Celery Worker

```bash
az containerapp create \
  --name rfpai-celery \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image $ACR_LOGIN_SERVER/rfpai-celery:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 1.0 \
  --memory 2.0Gi \
  --env-vars \
    "MONGO_URI=$COSMOS_CONNECTION" \
    "REDIS_URL=$REDIS_URL" \
    "VECTOR_DB_URL=http://rfpai-qdrant"
```

### Step 10: Deploy Qdrant (Vector DB)

```bash
az containerapp create \
  --name rfpai-qdrant \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image qdrant/qdrant:latest \
  --target-port 6333 \
  --ingress internal \
  --min-replicas 1 \
  --max-replicas 1 \
  --cpu 0.5 \
  --memory 1.0Gi
```

### Step 11: Deploy Frontend

```bash
# Get backend URL
BACKEND_URL=$(az containerapp show \
  --name rfpai-backend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

# Deploy frontend
az containerapp create \
  --name rfpai-frontend \
  --resource-group $RESOURCE_GROUP \
  --environment $ENV_NAME \
  --image $ACR_LOGIN_SERVER/rfpai-frontend:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 80 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars \
    "VUE_APP_API_URL=https://$BACKEND_URL/api"
```

### Step 12: Get Application URLs

```bash
# Get frontend URL
FRONTEND_URL=$(az containerapp show \
  --name rfpai-frontend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "🎉 Application deployed successfully!"
echo "Frontend: https://$FRONTEND_URL"
echo "Backend: https://$BACKEND_URL"
```

## 🔒 Security Best Practices

### 1. Use Azure Key Vault for Secrets

```bash
# Create Key Vault
az keyvault create \
  --name $APP_NAME-kv \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Store secrets
az keyvault secret set --vault-name $APP_NAME-kv --name "MongoUri" --value "$COSMOS_CONNECTION"
az keyvault secret set --vault-name $APP_NAME-kv --name "RedisUrl" --value "$REDIS_URL"
```

### 2. Enable Managed Identity

```bash
# Enable managed identity for backend
az containerapp identity assign \
  --name rfpai-backend \
  --resource-group $RESOURCE_GROUP \
  --system-assigned
```

### 3. Configure Custom Domain and SSL

```bash
# Add custom domain
az containerapp hostname add \
  --name rfpai-frontend \
  --resource-group $RESOURCE_GROUP \
  --hostname "www.yourdomain.com"
```

## 📊 Monitoring and Logging

### 1. Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app $APP_NAME-insights \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP

# Get instrumentation key
INSIGHTS_KEY=$(az monitor app-insights component show \
  --app $APP_NAME-insights \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey \
  --output tsv)
```

### 2. View Logs

```bash
# View backend logs
az containerapp logs show \
  --name rfpai-backend \
  --resource-group $RESOURCE_GROUP \
  --follow

# View frontend logs
az containerapp logs show \
  --name rfpai-frontend \
  --resource-group $RESOURCE_GROUP \
  --follow
```

## 🔄 CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [main]

env:
  AZURE_CONTAINER_REGISTRY: rfpaiacr
  RESOURCE_GROUP: rfpai-rg

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Login to ACR
        run: az acr login --name ${{ env.AZURE_CONTAINER_REGISTRY }}
      
      - name: Build and push backend
        run: |
          docker build -t ${{ env.AZURE_CONTAINER_REGISTRY }}.azurecr.io/rfpai-backend:${{ github.sha }} ./backend
          docker push ${{ env.AZURE_CONTAINER_REGISTRY }}.azurecr.io/rfpai-backend:${{ github.sha }}
      
      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name rfpai-backend \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --image ${{ env.AZURE_CONTAINER_REGISTRY }}.azurecr.io/rfpai-backend:${{ github.sha }}
```

## 🎯 Cost Optimization Tips

1. **Use Consumption Plan** for dev/test (pay per use)
2. **Enable autoscaling** (scale to 0 during idle)
3. **Use Cosmos DB free tier** (1000 RU/s free)
4. **Use Azure Front Door** for caching
5. **Set up budget alerts** in Azure Portal
6. **Monitor with Application Insights** (optimize performance)

## 📞 Support and Resources

- [Azure Container Apps Documentation](https://docs.microsoft.com/azure/container-apps/)
- [Azure Cosmos DB Pricing](https://azure.microsoft.com/pricing/details/cosmos-db/)
- [Azure Container Apps Pricing](https://azure.microsoft.com/pricing/details/container-apps/)

## 🎉 You're Done!

Your RFP AI application is now running on Azure Container Apps with:
- ✅ Fully managed infrastructure
- ✅ Auto-scaling capabilities
- ✅ High availability
- ✅ Secure connections
- ✅ Production monitoring

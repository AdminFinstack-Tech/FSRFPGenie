#!/bin/bash

# ============================================================================
# Script 3: Setup Azure Resources
# ============================================================================
# This script creates all necessary Azure resources:
# - Resource Group
# - Container Registry (ACR)
# - Container Apps Environment
# - Cosmos DB with MongoDB API
# - Azure Cache for Redis

set -e

# Configuration
RESOURCE_GROUP="rfprag-rg"
LOCATION="eastus"
ACR_NAME="rfpragreg"  # Must be globally unique, lowercase, alphanumeric
ENV_NAME="rfprag-env"
COSMOS_ACCOUNT="rfprag-cosmos"
REDIS_NAME="rfprag-redis"

echo "=================================================="
echo "☁️  Setting up Azure Resources"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  ACR Name: $ACR_NAME"
echo "  Environment: $ENV_NAME"
echo "  Cosmos DB: $COSMOS_ACCOUNT"
echo "  Redis: $REDIS_NAME"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it:"
    echo "   brew update && brew install azure-cli"
    exit 1
fi

echo "✅ Azure CLI found"

# Check if logged in
if ! az account show &> /dev/null; then
    echo "🔐 Not logged in to Azure. Logging in..."
    az login
else
    echo "✅ Already logged in to Azure"
fi

# Show current subscription
echo ""
echo "Current Azure Subscription:"
az account show --query "{Name:name, ID:id, State:state}" -o table
echo ""
read -p "Is this the correct subscription? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please run: az account list -o table"
    echo "Then: az account set --subscription <subscription-id>"
    exit 1
fi

# Create Resource Group
echo ""
echo "📦 Creating Resource Group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

# Create Container Registry
echo ""
echo "📦 Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --location $LOCATION \
    --output table

# Get ACR credentials
echo ""
echo "🔑 Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

echo "ACR Login Server: $ACR_LOGIN_SERVER"

# Create Container Apps Environment
echo ""
echo "📦 Creating Container Apps Environment..."
az containerapp env create \
    --name $ENV_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

# Create Cosmos DB with MongoDB API
echo ""
echo "📦 Creating Cosmos DB (MongoDB API)..."
az cosmosdb create \
    --name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --locations regionName=$LOCATION \
    --kind MongoDB \
    --server-version 4.2 \
    --default-consistency-level Session \
    --enable-free-tier true \
    --output table

# Get Cosmos DB connection string
echo ""
echo "🔑 Getting Cosmos DB connection string..."
COSMOS_CONNECTION=$(az cosmosdb keys list \
    --name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --type connection-strings \
    --query "connectionStrings[0].connectionString" -o tsv)

# Create Azure Cache for Redis
echo ""
echo "📦 Creating Azure Cache for Redis (Basic C0)..."
az redis create \
    --name $REDIS_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Basic \
    --vm-size c0 \
    --output table

# Get Redis connection info
echo ""
echo "🔑 Getting Redis connection info..."
REDIS_HOST=$(az redis show --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query hostName -o tsv)
REDIS_KEY=$(az redis list-keys --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query primaryKey -o tsv)
REDIS_CONNECTION="rediss://:${REDIS_KEY}@${REDIS_HOST}:6380"

echo ""
echo "=================================================="
echo "✅ Azure resources created successfully!"
echo "=================================================="
echo ""
echo "📝 Save these connection details:"
echo ""
echo "ACR_LOGIN_SERVER=$ACR_LOGIN_SERVER"
echo "ACR_USERNAME=$ACR_USERNAME"
echo "ACR_PASSWORD=$ACR_PASSWORD"
echo ""
echo "COSMOS_CONNECTION=$COSMOS_CONNECTION"
echo ""
echo "REDIS_CONNECTION=$REDIS_CONNECTION"
echo ""
echo "Writing to .env.azure file..."

# Create .env.azure file
cat > .env.azure << EOF
# Azure Container Registry
ACR_LOGIN_SERVER=$ACR_LOGIN_SERVER
ACR_USERNAME=$ACR_USERNAME
ACR_PASSWORD=$ACR_PASSWORD

# Azure Resources
RESOURCE_GROUP=$RESOURCE_GROUP
LOCATION=$LOCATION
ACR_NAME=$ACR_NAME
ENV_NAME=$ENV_NAME

# Database Connections
COSMOS_CONNECTION=$COSMOS_CONNECTION
REDIS_CONNECTION=$REDIS_CONNECTION

# Application Settings (UPDATE THESE)
OPENAI_API_KEY=your-openai-api-key-here
AZURE_OPENAI_ENDPOINT=your-azure-openai-endpoint-here
AZURE_OPENAI_KEY=your-azure-openai-key-here
EOF

echo ""
echo "✅ Configuration saved to .env.azure"
echo ""
echo "⚠️  IMPORTANT: Edit .env.azure and add your OpenAI API keys!"
echo ""
echo "Next step: Run ./4-push-to-acr.sh to push images to Azure"
echo ""

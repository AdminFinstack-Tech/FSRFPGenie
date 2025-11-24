#!/bin/bash

# Azure CI/CD Quick Setup Script
# This script creates all required Azure resources for the RFP AI application

set -e  # Exit on error

echo "🚀 RFP AI - Azure CI/CD Setup Script"
echo "===================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration - CUSTOMIZE THESE
RESOURCE_GROUP="${RESOURCE_GROUP:-rfpai-rg}"
LOCATION="${LOCATION:-eastus}"
ACR_NAME="${ACR_NAME:-rfpaiacr}"
ENV_NAME="${ENV_NAME:-rfpai-env}"
BACKEND_APP="${BACKEND_APP:-rfpai-backend}"
FRONTEND_APP="${FRONTEND_APP:-rfpai-frontend}"

echo -e "${BLUE}Configuration:${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  ACR Name: $ACR_NAME"
echo "  Environment: $ENV_NAME"
echo "  Backend App: $BACKEND_APP"
echo "  Frontend App: $FRONTEND_APP"
echo ""

read -p "Continue with these settings? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo -e "${GREEN}Step 1: Creating Resource Group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION
echo -e "${GREEN}✅ Resource Group created${NC}"
echo ""

echo -e "${GREEN}Step 2: Creating Azure Container Registry...${NC}"
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true
echo -e "${GREEN}✅ Container Registry created${NC}"
echo ""

echo -e "${GREEN}Step 3: Creating Container Apps Environment...${NC}"
az containerapp env create \
  --name $ENV_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
echo -e "${GREEN}✅ Container Apps Environment created${NC}"
echo ""

echo -e "${GREEN}Step 4: Creating Backend Container App...${NC}"
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
echo -e "${GREEN}✅ Backend Container App created${NC}"
echo ""

echo -e "${GREEN}Step 5: Creating Frontend Container App...${NC}"
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
echo -e "${GREEN}✅ Frontend Container App created${NC}"
echo ""

echo -e "${GREEN}Step 6: Configuring Container Registry Access...${NC}"
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

az containerapp registry set \
  --name $BACKEND_APP \
  --resource-group $RESOURCE_GROUP \
  --server $ACR_NAME.azurecr.io \
  --username $ACR_USERNAME \
  --password $ACR_PASSWORD

az containerapp registry set \
  --name $FRONTEND_APP \
  --resource-group $RESOURCE_GROUP \
  --server $ACR_NAME.azurecr.io \
  --username $ACR_USERNAME \
  --password $ACR_PASSWORD
echo -e "${GREEN}✅ Registry access configured${NC}"
echo ""

echo -e "${GREEN}Step 7: Creating Service Principal for GitHub Actions...${NC}"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo -e "${YELLOW}⚠️  Copy the following JSON output for GitHub Secrets:${NC}"
echo ""
az ad sp create-for-rbac \
  --name "github-actions-rfpai-$(date +%s)" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth
echo ""
echo -e "${YELLOW}⚠️  Save this JSON as the AZURE_CREDENTIALS secret in GitHub${NC}"
echo ""

echo -e "${GREEN}Step 8: Getting Resource Information...${NC}"
echo ""
echo "================================================"
echo -e "${BLUE}📋 Azure Resources Created:${NC}"
echo "================================================"
echo ""
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo ""
echo "Container Registry:"
echo "  Name: $ACR_NAME"
echo "  Login Server: $ACR_NAME.azurecr.io"
echo "  Username: $ACR_USERNAME"
echo ""
echo "Backend Container App:"
echo "  Name: $BACKEND_APP"
BACKEND_URL=$(az containerapp show --name $BACKEND_APP --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
echo "  URL: https://$BACKEND_URL"
echo ""
echo "Frontend Container App:"
echo "  Name: $FRONTEND_APP"
FRONTEND_URL=$(az containerapp show --name $FRONTEND_APP --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
echo "  URL: https://$FRONTEND_URL"
echo ""
echo "================================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "================================================"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Add the AZURE_CREDENTIALS JSON to GitHub Secrets"
echo "2. Add other required secrets to GitHub:"
echo "   - AZURE_OPENAI_ENDPOINT"
echo "   - AZURE_OPENAI_API_KEY"
echo "   - AZURE_OPENAI_DEPLOYMENT_NAME"
echo "   - AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
echo "   - MONGO_URI"
echo "   - AZURE_STORAGE_CONNECTION_STRING"
echo "   - AZURE_STORAGE_CONTAINER_NAME"
echo ""
echo "3. Push code to GitHub main branch to trigger deployment"
echo "4. Monitor deployment in GitHub Actions"
echo ""
echo "For detailed instructions, see: CI_CD_SETUP_GUIDE.md"
echo ""

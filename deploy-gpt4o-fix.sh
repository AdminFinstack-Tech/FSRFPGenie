#!/bin/bash
set -e

echo "🚀 Building and deploying RFP RAG with GPT-4o fix..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="rfpragreg.azurecr.io"
BACKEND_IMAGE="$REGISTRY/rfprag-backend:latest"
FRONTEND_IMAGE="$REGISTRY/rfprag-frontend:latest"

echo -e "${BLUE}📦 Step 1: Building backend image...${NC}"
docker build --platform linux/amd64 \
  -t $BACKEND_IMAGE \
  -f backend/Dockerfile backend/

echo -e "${GREEN}✅ Backend image built${NC}"
echo ""

echo -e "${BLUE}📦 Step 2: Building frontend image...${NC}"
docker build --platform linux/amd64 \
  -t $FRONTEND_IMAGE \
  -f frontend/Dockerfile frontend/

echo -e "${GREEN}✅ Frontend image built${NC}"
echo ""

echo -e "${BLUE}🔐 Step 3: Pushing backend to Azure Container Registry...${NC}"
docker push $BACKEND_IMAGE

echo -e "${GREEN}✅ Backend pushed${NC}"
echo ""

echo -e "${BLUE}🔐 Step 4: Pushing frontend to Azure Container Registry...${NC}"
docker push $FRONTEND_IMAGE

echo -e "${GREEN}✅ Frontend pushed${NC}"
echo ""

echo -e "${YELLOW}⚠️  Manual step required:${NC}"
echo "Run the following commands to restart the container apps:"
echo ""
echo "az containerapp update \\"
echo "  --name rfprag-backend \\"
echo "  --resource-group rfprag-rg \\"
echo "  --image $BACKEND_IMAGE"
echo ""
echo "az containerapp update \\"
echo "  --name rfprag-frontend \\"
echo "  --resource-group rfprag-rg \\"
echo "  --image $FRONTEND_IMAGE"
echo ""
echo -e "${GREEN}🎉 Build and push complete!${NC}"
echo ""
echo "What changed:"
echo "✅ Search button now calls POST /api/search/ask (GPT-4o RAG)"
echo "✅ AI-generated answers with confidence scores"
echo "✅ Professional formatting with markdown support"
echo "✅ Source document citations"
echo ""
echo "See SEARCH_BUTTON_FIX.md for details"

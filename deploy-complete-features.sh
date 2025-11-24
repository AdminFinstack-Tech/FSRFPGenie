#!/bin/bash

# SearchProfessional.vue Complete Feature Deployment
# Date: November 21, 2025
# All 8 feature categories implemented

echo "🚀 Deploying SearchProfessional.vue with ALL Features"
echo "=================================================="
echo ""

echo "📋 Features Included:"
echo "  ✅ Follow-up Questions (AI-generated suggestions)"
echo "  ✅ Copy to Clipboard (Answer + Results)"
echo "  ✅ Export Functionality (TXT, CSV)"
echo "  ✅ Bookmarks System (LocalStorage)"
echo "  ✅ Result Selection & Bulk Actions"
echo "  ✅ Advanced Filters (Product, Category, Bank)"
echo "  ✅ Search History (Last 20 searches)"
echo "  ✅ Visual Polish (Animations, Skeleton, Sticky Summary)"
echo ""

# Build backend
echo "📦 Building backend Docker image..."
docker build --platform linux/amd64 -t rfpragreg.azurecr.io/rfprag-backend:latest -f backend/Dockerfile .
if [ $? -ne 0 ]; then
    echo "❌ Backend build failed"
    exit 1
fi
echo "✅ Backend image built"
echo ""

# Build frontend
echo "📦 Building frontend Docker image..."
docker build --platform linux/amd64 -t rfpragreg.azurecr.io/rfprag-frontend:latest -f frontend/Dockerfile .
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed"
    exit 1
fi
echo "✅ Frontend image built"
echo ""

# Push backend
echo "🚀 Pushing backend to Azure Container Registry..."
docker push rfpragreg.azurecr.io/rfprag-backend:latest
if [ $? -ne 0 ]; then
    echo "❌ Backend push failed"
    exit 1
fi
echo "✅ Backend pushed"
echo ""

# Push frontend
echo "🚀 Pushing frontend to Azure Container Registry..."
docker push rfpragreg.azurecr.io/rfprag-frontend:latest
if [ $? -ne 0 ]; then
    echo "❌ Frontend push failed"
    exit 1
fi
echo "✅ Frontend pushed"
echo ""

echo "=================================================="
echo "✅ Docker images deployed successfully!"
echo ""
echo "📝 Next Steps:"
echo "1. Update Azure Container Apps:"
echo ""
echo "   az containerapp update --name rfprag-backend \\"
echo "     --resource-group rfprag-rg \\"
echo "     --image rfpragreg.azurecr.io/rfprag-backend:latest"
echo ""
echo "   az containerapp update --name rfprag-frontend \\"
echo "     --resource-group rfprag-rg \\"
echo "     --image rfpragreg.azurecr.io/rfprag-frontend:latest"
echo ""
echo "2. Or restart the apps:"
echo "   az containerapp restart --name rfprag-backend --resource-group rfprag-rg"
echo "   az containerapp restart --name rfprag-frontend --resource-group rfprag-rg"
echo ""
echo "3. Access the application:"
echo "   Frontend: https://rfprag-frontend.orangedesert-75e85877.eastus.azurecontainerapps.io"
echo "   Backend:  https://rfprag-backend.orangedesert-75e85877.eastus.azurecontainerapps.io"
echo ""
echo "=================================================="
echo "🎉 Deployment Complete!"
echo ""
echo "🆕 NEW FEATURES AVAILABLE:"
echo "  • Click AI answer for follow-up questions"
echo "  • Copy buttons on answer and results"
echo "  • Export to TXT/CSV"
echo "  • Bookmark answers and results"
echo "  • Select multiple results for bulk export"
echo "  • Filter by Product, Category, Bank"
echo "  • View search history dropdown"
echo "  • Smooth animations and loading states"
echo ""

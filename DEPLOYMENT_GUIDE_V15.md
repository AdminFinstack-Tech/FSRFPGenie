# 🚀 RFP RAG v15 - Deployment Guide

## Quick Summary of Changes

### Backend (v15)
- ✅ **Fixed Document Processing** - Changed from async to synchronous processing
- ✅ **Added DELETE Endpoint** - Full document deletion with cascading cleanup
- ✅ **AI Metadata Extraction** - GPT-4o powered intelligent filename analysis
- ✅ **Improved Error Handling** - Comprehensive logging and user feedback

### Frontend (v15)
- ✅ **Fixed Delete Functionality** - Properly calls backend DELETE endpoint
- ✅ **Premium Color Scheme** - Emerald/Gold/Navy branding with Poppins font
- ✅ **Enhanced UX** - Immediate feedback and confirmation dialogs

---

## 🐳 Step 1: Build Docker Images

### Backend:
```bash
cd /Users/ilyasashu/RFPAI/backend

# Build image
docker build -t rfpragreg.azurecr.io/rfprag-backend:v15 .

# Verify build
docker images | grep rfprag-backend
```

### Frontend:
```bash
cd /Users/ilyasashu/RFPAI/frontend

# Build production bundle first
npm run build

# Build Docker image
docker build -t rfpragreg.azurecr.io/rfprag-frontend:v15 .

# Verify build
docker images | grep rfprag-frontend
```

---

## ☁️ Step 2: Push to Azure Container Registry

### Login to ACR:
```bash
az acr login --name rfpragreg
```

### Push Images:
```bash
# Backend
docker push rfpragreg.azurecr.io/rfprag-backend:v15

# Frontend
docker push rfpragreg.azurecr.io/rfprag-frontend:v15
```

---

## 🔄 Step 3: Update Container Apps

### Backend Deployment:
```bash
az containerapp update \
  --name rfprag-backend \
  --resource-group rfprag-rg \
  --image rfpragreg.azurecr.io/rfprag-backend:v15

# Check deployment status
az containerapp show \
  --name rfprag-backend \
  --resource-group rfprag-rg \
  --query "properties.latestRevisionName" -o tsv
```

### Frontend Deployment:
```bash
az containerapp update \
  --name rfprag-frontend \
  --resource-group rfprag-rg \
  --image rfpragreg.azurecr.io/rfprag-frontend:v15

# Check deployment status
az containerapp show \
  --name rfprag-frontend \
  --resource-group rfprag-rg \
  --query "properties.latestRevisionName" -o tsv
```

---

## 🔧 Step 4: Verify Deployment

### Check Backend Logs:
```bash
az containerapp logs show \
  --name rfprag-backend \
  --resource-group rfprag-rg \
  --tail 50
```

### Test Health Endpoint:
```bash
curl https://rfprag-backend.orangedesert-75e85877.eastus.azurecontainerapps.io/api/health
```

Expected Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-19T...",
  "version": "1.0.0",
  "database": "mongodb"
}
```

### Test Frontend:
Open in browser:
```
https://rfprag-frontend.orangedesert-75e85877.eastus.azurecontainerapps.io
```

Verify:
- ✅ Emerald gradient logo with gold hover
- ✅ Poppins font on brand title
- ✅ Navy gradient app bar
- ✅ Gold subtitle text
- ✅ Emerald/gold button hover effects

---

## 📝 Step 5: Reprocess Failed Documents

Run the reprocess script to fix the 14 failed documents:

```bash
cd /Users/ilyasashu/RFPAI
./reprocess_failed_documents.sh
```

This will:
1. Call `POST /api/documents/<id>/process` for each failed document
2. Display success/failure status for each
3. Show final summary with updated statuses

Expected Output:
```
=====================================
Reprocessing Failed Documents
=====================================

Processing document: 69144fd724395ba32ce26ac4
  ✅ SUCCESS

Processing document: 69144fe3cdc63f1c1b09e36c
  ✅ SUCCESS

...

=====================================
Reprocessing Complete
=====================================
✅ Successful: 14
❌ Failed: 0
```

---

## 🧪 Step 6: Testing Checklist

### Upload & Processing Test:
```bash
# 1. Navigate to Upload page
# 2. Select "RFP Document"
# 3. Choose "Simple Mode"
# 4. Upload: Afreximbank_RFP_Test.xlsx
# 5. Verify immediate feedback (no async wait)
# 6. Check metadata auto-extracted:
#    - Bank Name: "Afreximbank"
#    - Product: "Trade Finance"
#    - RFP Name: "Afreximbank RFP Test"
# 7. Verify status: "completed" (not "processing")
# 8. Verify records_processed > 0
```

### Delete Functionality Test:
```bash
# 1. Navigate to Documents page
# 2. Click ⋮ menu on any document
# 3. Click "Delete"
# 4. Verify confirmation dialog appears
# 5. Confirm deletion
# 6. Verify success toast message
# 7. Verify document removed from list
# 8. Refresh page - document should still be gone
```

### API Endpoint Tests:
```bash
API_URL="https://rfprag-backend.orangedesert-75e85877.eastus.azurecontainerapps.io/api"

# Test upload with metadata
curl -X POST "$API_URL/documents/upload" \
  -F "file=@test.xlsx" \
  -F "document_type=RFP" \
  -F "processing_mode=simple"

# Test delete
curl -X DELETE "$API_URL/documents/<document_id>"

# Test manual process
curl -X POST "$API_URL/documents/<document_id>/process"
```

---

## 🔍 Step 7: Troubleshooting

### If uploads still fail:

1. **Check backend logs for errors:**
   ```bash
   az containerapp logs show \
     --name rfprag-backend \
     --resource-group rfprag-rg \
     --tail 200 | grep -i "error\|processing"
   ```

2. **Verify environment variables:**
   ```bash
   az containerapp show \
     --name rfprag-backend \
     --resource-group rfprag-rg \
     --query "properties.template.containers[0].env[].{name:name,value:value}" -o table
   ```

   Required vars:
   - `AZURE_STORAGE_CONNECTION_STRING`
   - `AZURE_OPENAI_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `MONGO_URI`

3. **Test blob storage connectivity:**
   ```bash
   # SSH into container
   az containerapp exec \
     --name rfprag-backend \
     --resource-group rfprag-rg
   
   # Inside container:
   python3 -c "from services import get_blob_service_client; print(get_blob_service_client())"
   ```

### If delete fails:

1. **Check backend logs:**
   ```bash
   az containerapp logs show \
     --name rfprag-backend \
     --resource-group rfprag-rg \
     --tail 100 | grep -i "delete"
   ```

2. **Test delete endpoint directly:**
   ```bash
   curl -v -X DELETE "$API_URL/documents/<document_id>"
   ```

3. **Verify CORS settings:**
   ```bash
   curl -H "Origin: https://rfprag-frontend.orangedesert-75e85877.eastus.azurecontainerapps.io" \
     -H "Access-Control-Request-Method: DELETE" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS "$API_URL/documents/<document_id>"
   ```

### If metadata extraction not working:

1. **Check Azure OpenAI configuration:**
   ```bash
   az containerapp logs show \
     --name rfprag-backend \
     --resource-group rfprag-rg \
     --tail 100 | grep -i "openai\|metadata"
   ```

2. **Verify GPT-4o deployment:**
   - Model: `gpt-4o`
   - Deployment name: Should be in `AZURE_OPENAI_CHAT_DEPLOYMENT` env var

3. **Test manually:**
   ```python
   from services import get_azure_client
   client = get_azure_client()
   response = client.chat.completions.create(
       model="gpt-4o",
       messages=[{"role": "user", "content": "Test"}]
   )
   print(response)
   ```

---

## 📊 Step 8: Monitor System Health

### Set up monitoring:
```bash
# Watch backend logs in real-time
az containerapp logs show \
  --name rfprag-backend \
  --resource-group rfprag-rg \
  --follow

# Check resource usage
az containerapp show \
  --name rfprag-backend \
  --resource-group rfprag-rg \
  --query "properties.template.containers[0].resources"
```

### Key Metrics to Monitor:
- **Upload Success Rate**: Should be 100%
- **Average Processing Time**: 10-30 seconds for Excel files
- **Delete Success Rate**: Should be 100%
- **Metadata Extraction Rate**: Should be 95%+ (falls back gracefully)

---

## 🎯 Success Criteria

Deployment is successful when:
- ✅ All 14 failed documents reprocessed successfully
- ✅ New uploads complete immediately with "completed" status
- ✅ Delete functionality works end-to-end
- ✅ Metadata auto-extracted from filenames
- ✅ UI shows premium emerald/gold/navy color scheme
- ✅ No errors in backend logs for normal operations
- ✅ Response times under 30 seconds for uploads

---

## 📞 Support

### Backend Logs:
```bash
az containerapp logs show --name rfprag-backend --resource-group rfprag-rg --tail 200
```

### Database Check:
```bash
# Connect to Cosmos DB and query
mongo "mongodb://rfprag-cosmos:...@rfprag-cosmos.mongo.cosmos.azure.com:10255/?ssl=true"

# Count documents by status
db.documents.aggregate([
  { $group: { _id: "$status", count: { $sum: 1 } } }
])
```

### Rollback (if needed):
```bash
# Rollback to v14
az containerapp update \
  --name rfprag-backend \
  --resource-group rfprag-rg \
  --image rfpragreg.azurecr.io/rfprag-backend:v14
```

---

## 🚀 Next Steps

After successful deployment:

1. **Test Upload System**
   - Upload 3-5 test documents in Simple mode
   - Verify all complete successfully
   - Check metadata extraction accuracy

2. **Clean Up Failed Documents**
   - Run reprocess script
   - Or manually delete failed documents using new DELETE endpoint

3. **User Acceptance Testing**
   - Test all upload scenarios
   - Test all delete scenarios
   - Verify color scheme matches requirements
   - Get feedback on metadata accuracy

4. **Documentation**
   - Update user guide with new features
   - Document metadata extraction capabilities
   - Add troubleshooting guide for common issues

5. **Performance Optimization** (future)
   - Consider re-enabling Celery with proper Redis setup
   - Add upload progress indicators
   - Implement batch operations
   - Add document reprocessing UI

---

**Deployment Version:** v15  
**Last Updated:** November 19, 2025  
**Deploy Time:** ~30 minutes  
**Rollback Time:** ~5 minutes

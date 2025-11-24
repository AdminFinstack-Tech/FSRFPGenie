# RFP Genie API Endpoints Reference

## Base URL
```
Production: https://rfprag-backend.orangedesert-75e85877.eastus.azurecontainerapps.io/api
Local Dev:  http://localhost:5000/api
```

---

## 📄 Document Management

### **1. Upload Document**
```http
POST /api/documents/upload
Content-Type: multipart/form-data

Form Data:
  file: <binary>              # Required
  bank_name: <string>         # Optional
  product: <string>           # Optional
  rfp_name: <string>          # Optional

Response 200:
{
  "document_id": "691431800598c2070bd0ca8e",
  "message": "Document uploaded successfully",
  "status": "processing"
}
```

### **2. List Documents**
```http
GET /api/documents

Query Parameters:
  page: 1                     # Page number (default: 1)
  limit: 50                   # Results per page (default: 50)
  sort_by: created_at         # Sort field
  sort_order: desc            # asc or desc

Response 200:
{
  "documents": [
    {
      "id": "691431800598c2070bd0ca8e",
      "file_name": "rfp_document.xlsx",
      "file_size": 114575,
      "status": "completed",
      "created_at": "2025-11-12T07:04:32.136000",
      "bank_name": "Example Bank",
      "product": "Trade Finance",
      "rfp_name": "Trade Finance RFP 2024",
      "records_processed": 163,
      "total_records": 163
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 50
}
```

### **3. Get Document Details**
```http
GET /api/documents/{document_id}

Response 200:
{
  "id": "691431800598c2070bd0ca8e",
  "file_name": "rfp_document.xlsx",
  "status": "completed",
  "created_at": "2025-11-12T07:04:32.136000",
  "blob_url": "https://...",
  "metadata": {...}
}
```

### **4. Delete Document**
```http
DELETE /api/documents/{document_id}

Response 200:
{
  "message": "Document deleted successfully",
  "document_id": "691431800598c2070bd0ca8e"
}
```

---

## 🔍 Search & Query

### **5. Search RFPs**
```http
GET /api/search

Query Parameters:
  query: <string>             # Required: search text
  document_id: <string>       # Optional: filter by document
  limit: 50                   # Optional: max results

Response 200:
{
  "results": [
    {
      "id": "...",
      "document_id": "...",
      "document_name": "rfp_document.xlsx",
      "requirement": "Bank must support ISO 20022 messaging",
      "response": "Yes, our system supports ISO 20022...",
      "section": "Technical Requirements",
      "similarity_score": 0.95,
      "bank_name": "Example Bank",
      "product": "Trade Finance"
    }
  ],
  "total": 42
}
```

### **6. Intelligent Q&A**
```http
POST /api/intelligent-qa
Content-Type: application/json

Request Body:
{
  "question": "What are the security requirements?",
  "document_id": "691431800598c2070bd0ca8e"  # Optional
}

Response 200:
{
  "answer": "The RFP specifies the following security requirements...",
  "confidence": 0.92,
  "sources": [
    {
      "document_id": "...",
      "section": "Security Requirements",
      "text": "..."
    }
  ]
}
```

---

## 🏥 Health & Status

### **7. Health Check**
```http
GET /api/health

Response 200:
{
  "status": "healthy",
  "database": "mongodb",
  "version": "1.0.0",
  "timestamp": "2025-11-19T12:00:00.000000"
}
```

---

## 📋 Templates

### **8. List Templates**
```http
GET /api/templates

Response 200:
{
  "templates": [
    {
      "id": "...",
      "name": "Trade Finance Standard Response",
      "description": "...",
      "category": "Trade Finance",
      "created_at": "..."
    }
  ]
}
```

### **9. Get Template**
```http
GET /api/templates/{template_id}

Response 200:
{
  "id": "...",
  "name": "Trade Finance Standard Response",
  "content": "...",
  "variables": [...]
}
```

---

## 🗺️ Column Mapping

### **10. Get Column Mapping**
```http
GET /api/documents/{document_id}/mapping

Response 200:
{
  "document_id": "...",
  "mapping": {
    "requirement": "Column A",
    "response": "Column B",
    "section": "Column C"
  }
}
```

### **11. Save Column Mapping**
```http
POST /api/documents/{document_id}/mapping
Content-Type: application/json

Request Body:
{
  "mapping": {
    "requirement": "Column A",
    "response": "Column B",
    "section": "Column C"
  }
}

Response 200:
{
  "message": "Mapping saved successfully"
}
```

---

## ❌ Error Responses

### **400 Bad Request**
```json
{
  "error": "No file provided"
}
```

### **404 Not Found**
```json
{
  "error": "Document not found"
}
```

### **500 Internal Server Error**
```json
{
  "error": "Internal server error: <details>"
}
```

---

## 🔐 CORS Configuration

**Allowed Origins**:
- `http://localhost:3000` (development)
- `https://rfprag-frontend.orangedesert-75e85877.eastus.azurecontainerapps.io` (production)

---

## 📝 Request Headers

### **Common Headers**:
```http
Content-Type: application/json           # For JSON requests
Content-Type: multipart/form-data        # For file uploads
Accept: application/json                 # Expected response format
```

---

## 🎯 Frontend Implementation Examples

### **Upload File (JavaScript)**:
```javascript
const formData = new FormData()
formData.append('file', file)
formData.append('bank_name', 'Example Bank')
formData.append('product', 'Trade Finance')

const response = await axios.post(
  `${API_URL}/documents/upload`,
  formData,
  { headers: { 'Content-Type': 'multipart/form-data' } }
)
```

### **Delete Document (JavaScript)**:
```javascript
const response = await axios.delete(
  `${API_URL}/documents/${documentId}`
)
```

### **Search (JavaScript)**:
```javascript
const response = await axios.get(
  `${API_URL}/search`,
  { params: { query: 'security requirements', limit: 50 } }
)
```

### **List Documents (JavaScript)**:
```javascript
const response = await axios.get(
  `${API_URL}/documents`,
  { params: { page: 1, limit: 50, sort_order: 'desc' } }
)
```

---

## 🧪 Testing with curl

### **Test Health**:
```bash
curl https://rfprag-backend.orangedesert-75e85877.eastus.azurecontainerapps.io/api/health
```

### **Test List Documents**:
```bash
curl "https://rfprag-backend.orangedesert-75e85877.eastus.azurecontainerapps.io/api/documents?limit=5"
```

### **Test Delete**:
```bash
curl -X DELETE "https://rfprag-backend.orangedesert-75e85877.eastus.azurecontainerapps.io/api/documents/691431800598c2070bd0ca8e"
```

### **Test Search**:
```bash
curl "https://rfprag-backend.orangedesert-75e85877.eastus.azurecontainerapps.io/api/search?query=security&limit=5"
```

---

## 📊 Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal error |

---

## 🔄 Document Processing Status

| Status | Description |
|--------|-------------|
| `processing` | Document is being processed |
| `completed` | Processing finished successfully |
| `failed` | Processing failed |
| `awaiting_mapping` | Waiting for column mapping |

---

## 📦 Backend Version

**Current**: v16  
**Image**: `rfpragreg.azurecr.io/rfprag-backend:v16`  
**Health**: Healthy ✅

---

## 🎨 Frontend Version

**Current**: v18  
**Image**: `rfpragreg.azurecr.io/rfprag-frontend:v18`  
**Health**: Healthy ✅

---

## 🆘 Troubleshooting

### **404 Errors**:
- Check endpoint URL matches this documentation
- Verify document ID is valid ObjectId format
- Confirm API base URL includes `/api`

### **500 Errors**:
- Check backend logs: `az containerapp logs show --name rfprag-backend`
- Verify MongoDB connection
- Check Azure Blob Storage credentials

### **CORS Errors**:
- Verify origin is in allowed list
- Check browser console for exact error
- Confirm request headers are correct

---

## 📚 Related Documentation

- **Design System**: `PROFESSIONAL_DESIGN_SYSTEM.md`
- **API Fixes**: `API_FIXES_v18.md`
- **Redesign Summary**: `PROFESSIONAL_REDESIGN_COMPLETE.md`

---

Last Updated: November 19, 2025  
Backend Version: v16  
Frontend Version: v18

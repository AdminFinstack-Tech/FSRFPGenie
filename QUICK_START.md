# 🚀 Quick Start Guide - Intelligent RFP Q&A System

## Access the Application

**Frontend**: http://localhost:8080
**Backend API**: http://localhost:5000

## 1️⃣ Upload a Document

1. Go to http://localhost:8080/upload
2. Choose **Processing Mode**:
   - **Simple Mode** ⚡: One-click processing, auto-extracts all content
   - **Professional Mode** 💼: Column mapping, structured extraction

### Simple Mode (Recommended for Quick Start)
1. Select "Simple Mode"
2. Upload your Excel RFP file
3. Click "Upload & Process"
4. Wait ~30 seconds for processing
5. Automatically redirected to Search

### Professional Mode (For Advanced Users)
1. Select "Professional Mode"
2. Upload your Excel RFP file
3. Click "Upload & Map Columns"
4. Review auto-suggested column mappings
5. Adjust mappings if needed (Auto/Manual toggle)
6. Click "Process Document"
7. Wait for processing to complete

## 2️⃣ Search & Ask Questions

Go to http://localhost:8080/search

### AI Answer Mode (🤖 Intelligent)

**Best for**: Getting specific answers to questions

**Example Questions**:
```
What are the fraud detection requirements?
List all third-party integrations needed
What security and compliance requirements are mentioned?
Summarize the performance requirements
Compare MLC and EPLC features
What AI/ML capabilities are required?
```

**What you get**:
- Natural language answer from GPT-4o
- Confidence score (0-100%)
- Source documents with citations
- Ability to ask follow-up questions

**Controls**:
- **Creativity**: 0 (focused) to 1 (creative)
- **Context Docs**: 3-10 documents to analyze
- **Answer Length**: 500-2000 tokens

### Vector Search Mode (🔍 Search)

**Best for**: Browsing and exploring documents

**What you get**:
- Ranked list of relevant documents
- Relevance scores
- Full document details
- Export capabilities

## 3️⃣ Use Filters (Optional)

Click "Show Filters" to narrow results:
- **Products**: MLC, EPLC, Integration, etc.
- **Response Category**: Readily Available, Configuration, etc.
- **Requirement Category**: Functional, Technical, Security, etc.

## 4️⃣ Ask Follow-up Questions

After getting an AI answer:
1. Type your follow-up in the input below the answer
2. System remembers conversation context
3. Get more specific information

**Example conversation**:
```
Q1: "What are the fraud detection requirements?"
A1: [GPT-4o provides summary]

Q2: "Can you be more specific about the ML requirements?"
A2: [GPT-4o provides detailed ML requirements, remembering Q1]

Q3: "What technologies are suggested for this?"
A3: [GPT-4o provides technology recommendations]
```

## 5️⃣ Export Results

- **Copy Answer**: Click "Copy Answer" button
- **Export Answer**: Download as JSON with sources
- **Export Search Results**: Download search results

## 📊 System Status Indicators

### Confidence Badges
- 🟢 **Green (80-100%)**: High confidence
- 🟡 **Yellow (60-79%)**: Medium confidence
- 🔴 **Red (<60%)**: Low confidence

### Mode Badges
- 🟢 **intelligent**: GPT-4o answer with Azure embeddings
- 🟡 **search-only**: Vector search only (GPT-4o unavailable)
- 🔴 **no-results**: No relevant documents found
- 🔴 **error**: System error

## ⚙️ Advanced Settings

### AI Settings (Show AI Settings button)

**Temperature** (Default: 0.3)
- `0.0`: Very focused, factual, conservative
- `0.3`: Balanced (recommended)
- `0.5`: More creative
- `1.0`: Most creative, expansive

**Context Documents** (Default: 5)
- `3`: Faster, more focused
- `5`: Balanced (recommended)
- `10`: More comprehensive, slower

**Answer Length** (Default: 1000)
- `500`: Brief answers
- `1000`: Standard (recommended)
- `2000`: Detailed, comprehensive

## 🔧 Troubleshooting

### Backend not responding
```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Frontend not loading
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Azure OpenAI not working
System automatically falls back to:
1. **Embeddings**: Local SentenceTransformer (384D instead of 3072D)
2. **Q&A**: Search-only mode (returns formatted search results)

Check logs for:
```
⚠️ Azure OpenAI embeddings failed, using local model
⚠️ GPT-4o initialization failed
```

### Processing stuck
```bash
# Check Celery worker
docker-compose logs celery

# Restart Celery
docker-compose restart celery
```

## 📈 Performance Tips

### For Best Answers
1. Be specific in questions
2. Use domain terminology (SLA, fraud detection, integration, etc.)
3. Ask one thing at a time
4. Use follow-ups for details

### For Faster Processing
1. Use Simple Mode for quick uploads
2. Reduce "Context Documents" to 3
3. Reduce "Answer Length" to 500
4. Use filters to narrow search space

### For Better Accuracy
1. Increase "Context Documents" to 10
2. Use temperature 0.1-0.3
3. Ask specific, well-formed questions
4. Review source documents for verification

## 🎯 Sample Workflows

### Workflow 1: Quick RFP Analysis
1. Upload document (Simple Mode)
2. Wait for processing
3. Ask: "What are the main requirements?"
4. Ask: "What are the most critical items?"
5. Ask: "What third-party integrations are needed?"
6. Export all answers

### Workflow 2: Detailed Feature Comparison
1. Upload multiple RFP documents
2. Filter by product (e.g., "MLC")
3. Ask: "Compare MLC features across all RFPs"
4. Review source documents
5. Ask follow-up for specific features
6. Export comparison

### Workflow 3: Compliance Check
1. Upload RFP document
2. Filter by category ("Security" + "Compliance")
3. Ask: "List all security and compliance requirements"
4. Ask: "What certifications are required?"
5. Ask: "What data protection measures are needed?"
6. Export compliance checklist

## 🆘 Getting Help

### Check Documentation
- `README.md` - General setup
- `INTELLIGENT_QA_SYSTEM.md` - Detailed architecture
- `MONGODB_MIGRATION.md` - Database info

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f frontend
```

### Restart Everything
```bash
docker-compose down
docker-compose up -d
```

### Reset Database
```bash
# WARNING: Deletes all data
docker-compose down -v
docker-compose up -d
```

## 🎉 Success Checklist

After deployment, verify:

✅ Frontend accessible at http://localhost:8080
✅ Backend API at http://localhost:5000/api/health returns OK
✅ MongoDB running (port 27018)
✅ Redis running (port 6380)
✅ Qdrant running (port 6333)
✅ Can upload documents
✅ Processing completes successfully
✅ Search returns results
✅ AI answers are generated
✅ Confidence scores shown
✅ Source citations displayed

---

**🚀 Ready to go! Start at**: http://localhost:8080/upload

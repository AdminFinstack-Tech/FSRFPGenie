# 🔍 API Endpoint Analysis - /ask vs /query

## Overview
Your application has **two search endpoints** with different capabilities:

---

## 1️⃣ `/api/query` - **Basic Vector Search (RAG without LLM)**

### **Endpoint Details**
- **Route**: `POST /api/query`
- **Function**: `query_rag()`
- **Line**: 575-593 in `app.py`

### **What It Does**
✅ **Vector search ONLY** - Returns matching documents without LLM generation
- Uses Azure OpenAI embeddings for semantic search
- Returns raw RFP entries that match the query
- No natural language answer generation

### **Request Format**
```json
{
  "query": "user search query",
  "top_n": 10,
  "filters": {
    "product": "Trade Finance",
    "document_id": "optional"
  }
}
```

### **Response Format**
```json
{
  "query": "user query",
  "total_results": 10,
  "returned_results": 10,
  "results": [
    {
      "record_id": "...",
      "product": "Trade Finance",
      "requirement": "The system shall...",
      "requirement_category": "Must Have",
      "relevance_score": 0.85,
      "bank_name": "ABC Bank",
      "rfp_name": "Trade Finance RFP"
    }
  ]
}
```

### **Technology Stack**
- ✅ Azure OpenAI Embeddings (text-embedding-3-large)
- ✅ MongoDB vector search (cosine similarity)
- ❌ NO GPT-4o (no answer generation)

### **Use Case**
- Quick document retrieval
- When you want raw RFP requirements without AI interpretation
- Building your own UI with custom answer formatting

---

## 2️⃣ `/api/search/ask` - **Full RAG with LLM (Intelligent Q&A)**

### **Endpoint Details**
- **Route**: `POST /api/search/ask`
- **Function**: `intelligent_ask()`
- **Line**: 632-675 in `app.py`
- **Service**: `IntelligentQAService.ask_question()`

### **What It Does**
✅ **Complete RAG Pipeline** - Vector search + GPT-4o answer generation
1. **Retrieves** relevant documents using vector search
2. **Generates** natural language answer using GPT-4o
3. **Cites** source documents in the response
4. **Falls back** to simple text search if vector DB unavailable

### **Request Format**
```json
{
  "question": "What are the alert management requirements?",
  "filters": {
    "product": "Trade Finance",
    "bank_name": "ABC Bank"
  },
  "max_context_docs": 5,
  "temperature": 0.7,
  "max_answer_length": 500
}
```

### **Response Format**
```json
{
  "answer": "Based on the RFP requirements, the alert management system must include:\n\n1. Real-time notifications [Document 1]\n2. Configurable alert thresholds [Document 2]\n...",
  "sources": [
    {
      "record_id": "...",
      "product": "Trade Finance",
      "requirement": "The system shall provide...",
      "relevance_score": 0.92,
      "file_name": "ABC_Bank_RFP.xlsx"
    }
  ],
  "mode": "intelligent",
  "confidence": 0.95,
  "model": "gpt-4o",
  "total_sources": 5,
  "sources_analyzed": 5
}
```

### **Technology Stack**
- ✅ Azure OpenAI Embeddings (text-embedding-3-large)
- ✅ GPT-4o (answer generation)
- ✅ MongoDB vector search
- ✅ Intelligent fallback to text search
- ✅ Source citation and confidence scoring

### **Fallback Modes**
The endpoint has **3 operating modes**:

#### **Mode 1: Intelligent (Full RAG)**
- Vector search + GPT-4o generation
- Best accuracy and natural language answers
- Requires: Azure OpenAI API + Vector embeddings

#### **Mode 2: Simple Search (Fallback)**
- Regex-based MongoDB text search
- Basic keyword matching
- Returns structured answer without LLM
- Used when: Vector DB unavailable or connection error

#### **Mode 3: Error**
- Database connection failed
- Returns error message with helpful context

### **Use Case**
- Natural language Q&A
- When you want human-readable answers with citations
- Complex queries requiring interpretation
- Best user experience

---

## 🔄 Flow Comparison

### `/api/query` Flow
```
User Query 
  → Vector Search (Embeddings)
  → Return Raw Documents
  → END
```

### `/api/search/ask` Flow
```
User Question
  → Vector Search (Embeddings)
  → Prepare Context from Top Documents
  → GPT-4o Generation (with system prompt)
  → Format Answer with Citations
  → Return Natural Language Response
  → END
```

**Fallback Path:**
```
User Question
  → Vector Search FAILS
  → Regex Text Search (MongoDB)
  → Format Simple Answer
  → Return with "simple-search" mode
  → END
```

---

## 📊 Feature Comparison

| Feature | `/api/query` | `/api/search/ask` |
|---------|-------------|-------------------|
| **Vector Search** | ✅ Yes | ✅ Yes |
| **LLM Generation** | ❌ No | ✅ GPT-4o |
| **Natural Language Answer** | ❌ No | ✅ Yes |
| **Source Citations** | Partial | ✅ Full |
| **Confidence Score** | ❌ No | ✅ Yes |
| **Fallback Search** | ❌ No | ✅ Regex search |
| **Response Format** | List of docs | Conversational |
| **Cost** | Lower (embeddings only) | Higher (embeddings + GPT-4o) |
| **Speed** | Faster | Slower |
| **Accuracy** | Good | Excellent |

---

## 🔧 Current Configuration Status

### Checking Your Setup
Based on the code analysis:

```python
# From services.py and intelligent_qa.py
AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')  # ✅ Configured
AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')  # ✅ Configured
AZURE_EMBEDDING_MODEL = 'text-embedding-3-large'  # ✅ Set
AZURE_DEPLOYMENT_NAME = 'gpt-4o'  # ✅ Set
USE_AZURE_EMBEDDINGS = True  # ✅ Enabled
```

### From your `.env.azure`:
```bash
OPENAI_API_KEY=1h36ydp0nY0qVt... ✅
AZURE_OPENAI_ENDPOINT=https://newfinaiapp.openai.azure.com ✅
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o ✅
```

### Service Initialization Status
```python
# From app.py (lines 69-80)
if db is not None:
    qa_service = IntelligentQAService(db)  # ✅ Initialized if DB connected
    vector_service = VectorSearchService(db)  # ✅ Initialized if DB connected
else:
    qa_service = None  # ⚠️ Falls back to simple search
    vector_service = None  # ⚠️ Endpoint returns 503
```

---

## ⚠️ Issues Found

### 1. **Missing Service Check in `/api/query`**
**Problem**: Line 587 doesn't check if `vector_service` is None before calling `.search()`

```python
# Current code (Line 587)
results = vector_service.search(query, top_n, filters)  # ❌ Can crash if None
```

**Fix Applied**: Line 613 already has proper check:
```python
if vector_service is None:
    return jsonify({'error': 'Search service not available'}), 503
```

But `/api/query` needs the same protection!

### 2. **Inconsistent Error Handling**
- `/api/search/ask` gracefully falls back to simple search ✅
- `/api/query` will crash with AttributeError if vector_service is None ❌

---

## 🎯 Recommendations

### For `/api/query` Endpoint
Add null check before using vector_service:

```python
@app.route('/api/query', methods=['POST'])
def query_rag():
    """Query the RAG system"""
    data = request.get_json()
    query = data.get('query')
    top_n = data.get('top_n', 10)
    filters = data.get('filters', {})
    
    if not query or len(query) < 3:
        return jsonify({'error': 'Query must be at least 3 characters'}), 400
    
    # ADD THIS CHECK
    if vector_service is None:
        return jsonify({'error': 'Vector search service not available'}), 503
    
    # Perform vector search
    results = vector_service.search(query, top_n, filters)
    
    return jsonify({
        'query': query,
        'total_results': len(results),
        'returned_results': len(results[:top_n]),
        'results': results[:top_n]
    })
```

### For Better User Experience
1. **Use `/api/search/ask` for end users** - Better UX, natural language answers
2. **Use `/api/query` for developers** - Quick access to raw documents
3. **Monitor the `mode` field** in responses to detect fallback scenarios

### For Production
1. **Ensure vector embeddings are generated** for all uploaded documents
2. **Monitor Azure OpenAI quota** - Both endpoints use it
3. **Set up proper error alerting** for service failures

---

## 🚀 Quick Test

### Test Vector Search (Basic)
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "alert management",
    "top_n": 5
  }'
```

### Test Intelligent Q&A (Full RAG)
```bash
curl -X POST http://localhost:5000/api/search/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the requirements for alert management?",
    "max_context_docs": 5,
    "temperature": 0.7
  }'
```

---

## 📈 Performance Comparison

| Metric | `/api/query` | `/api/search/ask` |
|--------|-------------|-------------------|
| **Average Latency** | ~200-500ms | ~2-5 seconds |
| **Token Usage** | ~100-500 (embeddings only) | ~1000-3000 (embeddings + generation) |
| **Cost per Request** | $0.0001-0.0005 | $0.005-0.02 |
| **Rate Limits** | Embeddings limit | Embeddings + GPT-4o limit |

---

## ✅ Summary

### `/api/query` (Vector Search Only)
- **Purpose**: Fast document retrieval without LLM
- **Best for**: Developers, raw data access, cost-sensitive use cases
- **Returns**: List of matching documents
- **Status**: ✅ Configured, ⚠️ Needs null check

### `/api/search/ask` (Full RAG with LLM)
- **Purpose**: Intelligent Q&A with natural language answers
- **Best for**: End users, complex queries, best UX
- **Returns**: Conversational answer + cited sources
- **Status**: ✅ Fully configured with fallback

**Recommendation**: Use `/api/search/ask` for your main search feature! 🎯

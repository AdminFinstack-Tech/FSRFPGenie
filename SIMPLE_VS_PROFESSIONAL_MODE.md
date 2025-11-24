# Simple vs Professional Mode - Implementation Plan

## Mode Comparison

### 🌟 Simple Mode (One-Click Processing)
**Target Users**: Quick analysis, non-technical users, rapid prototyping

**Workflow**:
1. Upload document (PDF, Excel, Word)
2. **Automatic processing** - No column mapping needed
3. System automatically:
   - Detects document structure
   - Extracts all text content
   - Creates embeddings for entire document chunks
   - Indexes in vector database
4. Ready to search immediately!

**Features**:
- ✅ Zero configuration
- ✅ Processes entire document as-is
- ✅ Chunk-based embedding (500 words per chunk)
- ✅ Fast setup (< 1 minute)
- ❌ Less structured data
- ❌ No field categorization

### 🎯 Professional Mode (Current System)
**Target Users**: Structured analysis, data categorization, advanced filtering

**Workflow**:
1. Upload Excel/RFP document
2. **Manual column mapping** - Map Excel columns to fields
3. Row-by-row processing:
   - Extract structured data
   - Categorize by Product, Priority, etc.
   - Create embeddings per requirement
   - Index with rich metadata
4. Advanced search with filters

**Features**:
- ✅ Structured data extraction
- ✅ Field-level filtering (Product, Category, etc.)
- ✅ Fine-grained search control
- ✅ Template support
- ❌ Requires configuration
- ❌ Slower setup (5-10 minutes)

## Implementation Changes

### Backend Changes
1. Add mode selection to document metadata
2. Create `process_simple_mode()` function
3. Auto-detect document type and extract text
4. Chunk large documents (500 words/chunk)
5. Embed and index each chunk

### Frontend Changes
1. Add mode selector on Upload page
2. Skip Column Mapping for Simple mode
3. Show different processing status
4. Unified search interface for both modes

### Database Schema
```javascript
// Document
{
  mode: 'simple' | 'professional',
  chunks: [  // For simple mode only
    {
      chunk_id: '...',
      text: '...',
      page: 1,
      position: 0
    }
  ]
}
```

## Current Model Information

**Embedding Model**: `all-MiniLM-L6-v2`
- Type: Sentence Transformer
- Vector Dimension: 384
- Speed: ~1000 sentences/second
- Quality: Good for semantic search
- License: Apache 2.0
- Size: ~80MB

**Upgrade Options** (Future):
- `all-mpnet-base-v2` (768D) - Better quality, slower
- `paraphrase-multilingual-MiniLM-L12-v2` - Multilingual support
- Custom fine-tuned model - Domain-specific

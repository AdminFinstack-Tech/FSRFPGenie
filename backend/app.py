from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from bson import ObjectId
from bson.json_util import dumps
import json
from azure.storage.blob import BlobServiceClient
import io

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=app.config['CORS_ORIGINS'])

# Initialize MongoDB
try:
    # Debug logging
    mongo_uri = app.config.get('MONGO_URI')
    app.logger.info(f"Attempting MongoDB connection to: {mongo_uri[:50] if mongo_uri else 'None'}...")
    
    # Initialize PyMongo with explicit database name
    if mongo_uri:
        mongo = PyMongo(app)
        db = mongo.db
        
        # Test the connection
        if db is not None:
            # Try to ping the database
            db.command('ping')
            collections = db.list_collection_names()
            app.logger.info(f"Successfully connected to MongoDB! Collections: {collections}")
        else:
            app.logger.error("MongoDB initialization failed: db is None")
            app.logger.error(f"PyMongo app config: MONGO_URI={app.config.get('MONGO_URI')[:50] if app.config.get('MONGO_URI') else 'None'}")
            db = None
    else:
        app.logger.error("MONGO_URI is not set in configuration")
        db = None
except Exception as e:
    app.logger.error(f"MongoDB connection error: {str(e)}")
    app.logger.exception("Full traceback:")
    db = None

# Import services after app initialization
from services import DocumentService, VectorSearchService, FileProcessingService
from intelligent_qa import IntelligentQAService
import time

# Allow time for dependent services to start
if os.environ.get('FLASK_ENV') != 'development':
    time.sleep(5)

# Initialize Azure Blob Storage
blob_service_client = None
try:
    storage_connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    if storage_connection_string:
        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
        app.logger.info("Azure Blob Storage initialized successfully")
    else:
        app.logger.warning("AZURE_STORAGE_CONNECTION_STRING not set, file uploads will fail")
except Exception as e:
    app.logger.error(f"Failed to initialize Azure Blob Storage: {str(e)}")
    blob_service_client = None

# Initialize services only if db is available
if db is not None:
    doc_service = DocumentService(db)
    vector_service = VectorSearchService(db)
    file_service = FileProcessingService(db)
    qa_service = IntelligentQAService(db)
else:
    app.logger.warning("Services not initialized due to database connection failure")
    doc_service = None
    vector_service = None
    file_service = None
    qa_service = None

# Helper functions for Azure Blob Storage
def upload_to_blob(file, filename):
    """Upload file to Azure Blob Storage and return blob URL"""
    if not blob_service_client:
        raise Exception("Blob storage not configured")
    
    try:
        blob_client = blob_service_client.get_blob_client(container="uploads", blob=filename)
        file.seek(0)  # Reset file pointer
        blob_client.upload_blob(file.read(), overwrite=True)
        return blob_client.url
    except Exception as e:
        app.logger.error(f"Failed to upload to blob storage: {str(e)}")
        raise

def download_from_blob(filename):
    """Download file from Azure Blob Storage and return as bytes"""
    if not blob_service_client:
        raise Exception("Blob storage not configured")
    
    try:
        blob_client = blob_service_client.get_blob_client(container="uploads", blob=filename)
        stream = io.BytesIO()
        blob_client.download_blob().readinto(stream)
        stream.seek(0)
        return stream
    except Exception as e:
        app.logger.error(f"Failed to download from blob storage: {str(e)}")
        raise

def delete_from_blob(filename):
    """Delete file from Azure Blob Storage"""
    if not blob_service_client:
        return
    
    try:
        blob_client = blob_service_client.get_blob_client(container="uploads", blob=filename)
        blob_client.delete_blob()
    except Exception as e:
        app.logger.warning(f"Failed to delete from blob storage: {str(e)}")

# Helper function to serialize MongoDB documents
def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc:
        doc['_id'] = str(doc['_id'])
        if 'document_id' in doc:
            doc['document_id'] = str(doc['document_id'])
        if 'created_at' in doc and isinstance(doc['created_at'], datetime):
            doc['created_at'] = doc['created_at'].isoformat()
        if 'completed_at' in doc and isinstance(doc['completed_at'], datetime):
            doc['completed_at'] = doc['completed_at'].isoformat()
        if 'last_modified' in doc and isinstance(doc['last_modified'], datetime):
            doc['last_modified'] = doc['last_modified'].isoformat()
        if 'date' in doc and hasattr(doc['date'], 'isoformat'):
            doc['date'] = doc['date'].isoformat()
    return doc

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'database': 'mongodb'
    })

def extract_metadata_from_filename(filename):
    """Use Azure OpenAI to extract metadata from filename"""
    try:
        from services import get_azure_client
        
        client = get_azure_client()
        if not client:
            app.logger.warning("Azure OpenAI client not available for metadata extraction")
            return {}
        
        # Remove file extension for analysis
        name_without_ext = os.path.splitext(filename)[0]
        
        prompt = f"""Extract the following information from this document filename and return as JSON:
        
Filename: {name_without_ext}

Please identify:
1. bank_name: The name of the bank or financial institution (if present)
2. product: The product or system type (e.g., "Trade Finance", "Payment System", "Core Banking")
3. rfp_name: A descriptive name for the RFP or project

Guidelines:
- Use proper capitalization and formatting
- If bank name unclear, infer from context or use empty string
- For product, look for keywords like "Trade", "Payment", "Core Banking", "Loan", etc.
- For rfp_name, create a concise, professional name based on the filename
- Return valid JSON only, no explanation

Example output:
{{
    "bank_name": "ABC Bank",
    "product": "Trade Finance System",
    "rfp_name": "Trade Finance Platform RFP"
}}"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=150
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response (handle markdown code blocks)
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0].strip()
        
        metadata = json.loads(result_text)
        app.logger.info(f"Extracted metadata from filename: {metadata}")
        return metadata
        
    except Exception as e:
        app.logger.error(f"Metadata extraction failed: {str(e)}")
        return {}

@app.route('/api/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document and all associated data"""
    try:
        doc_id = ObjectId(document_id)
        
        # Get document to find blob name
        document = db.documents.find_one({'_id': doc_id})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Delete from database collections
        db.rfp_entries.delete_many({'document_id': doc_id})
        db.vector_embeddings.delete_many({'document_id': str(doc_id)})
        db.documents.delete_one({'_id': doc_id})
        
        # Delete blob from Azure Storage
        if 'blob_name' in document:
            try:
                delete_from_blob(document['blob_name'])
                app.logger.info(f"Deleted blob: {document['blob_name']}")
            except Exception as e:
                app.logger.warning(f"Failed to delete blob: {e}")
        
        return jsonify({
            'message': 'Document deleted successfully',
            'document_id': document_id
        }), 200
        
    except Exception as e:
        app.logger.error(f"Delete error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Upload RFP or documentation file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        document_type = request.form.get('document_type')
        if document_type not in ['RFP', 'Documentation']:
            return jsonify({'error': 'Invalid document type'}), 400
        
        # Upload file to Azure Blob Storage
        filename = secure_filename(file.filename)
        file_id = ObjectId()
        blob_filename = f"{str(file_id)}_{filename}"
        
        # Upload to blob storage
        blob_url = upload_to_blob(file, blob_filename)
        
        # Calculate file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        # Create document record with intelligent metadata extraction
        user_metadata = json.loads(request.form.get('metadata', '{}'))
        processing_mode = request.form.get('processing_mode', 'professional')  # Get processing mode
        
        # Extract metadata from filename using AI
        auto_metadata = extract_metadata_from_filename(filename)
        
        # Merge user-provided metadata with auto-extracted (user takes precedence)
        metadata = {
            'bank_name': user_metadata.get('bank_name') or auto_metadata.get('bank_name', ''),
            'product': user_metadata.get('product') or auto_metadata.get('product', ''),
            'rfp_name': user_metadata.get('rfp_name') or auto_metadata.get('rfp_name', filename)
        }
        
        document = {
            '_id': file_id,
            'document_type': document_type,
            'file_name': filename,
            'blob_name': blob_filename,  # Store blob name instead of file_path
            'blob_url': blob_url,  # Store blob URL
            'file_size': file_size,
            'metadata': metadata,
            'auto_extracted_metadata': auto_metadata,  # Store for reference
            'processing_mode': processing_mode,  # Store processing mode
            'status': 'processing',
            'created_at': datetime.utcnow(),
            'uploaded_by': request.form.get('uploaded_by', 'anonymous')
        }
        
        db.documents.insert_one(document)
        
        # Process file SYNCHRONOUSLY (Celery/async disabled for reliability)
        if file_service is not None:
            try:
                # Always process synchronously for immediate feedback
                app.logger.info(f"Starting synchronous processing for document: {str(file_id)}")
                file_service.process_document(str(file_id))
                app.logger.info(f"Successfully processed document: {str(file_id)}")
                
                return jsonify({
                    'document_id': str(file_id),
                    'status': 'completed',
                    'processing_mode': processing_mode,
                    'metadata': metadata,
                    'message': f'Document uploaded and processed successfully ({processing_mode} mode)'
                }), 200
                
            except Exception as sync_error:
                app.logger.error(f"Processing failed: {str(sync_error)}")
                app.logger.exception("Full traceback:")
                # Update document status to failed
                db.documents.update_one(
                    {'_id': file_id},
                    {'$set': {'status': 'failed', 'error': str(sync_error)}}
                )
                
                return jsonify({
                    'document_id': str(file_id),
                    'status': 'failed',
                    'error': str(sync_error),
                    'message': 'Document uploaded but processing failed'
                }), 500
        else:
            app.logger.warning("File service not available, document uploaded but not processed")
            # Update document status
            db.documents.update_one(
                {'_id': file_id},
                {'$set': {'status': 'uploaded', 'note': 'Processing service unavailable'}}
            )
            
            return jsonify({
                'document_id': str(file_id),
                'status': 'uploaded',
                'processing_mode': processing_mode,
                'message': 'Document uploaded but processing service unavailable'
            }), 503
        
    except Exception as e:
        app.logger.error(f"Upload error: {str(e)}")
        app.logger.exception("Full traceback:")
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<document_id>/process', methods=['POST'])
def process_document_manually(document_id):
    """Manually trigger document processing (synchronous)"""
    try:
        if not file_service:
            return jsonify({'error': 'File processing service not available'}), 503
        
        # Get document
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Update status to processing
        db.documents.update_one(
            {'_id': ObjectId(document_id)},
            {'$set': {'status': 'processing'}}
        )
        
        # Process synchronously (not using Celery)
        try:
            processing_mode = document.get('processing_mode', 'professional')
            
            if processing_mode == 'simple':
                if document.get('document_type') == 'RFP':
                    file_service._process_simple_rfp(document)
                else:
                    file_service._process_documentation(document)
            else:
                # Professional mode requires column mapping
                return jsonify({
                    'error': 'Professional mode requires column mapping',
                    'message': 'Please use the column mapping interface to process this document'
                }), 400
            
            # Update status to completed
            db.documents.update_one(
                {'_id': ObjectId(document_id)},
                {'$set': {
                    'status': 'completed',
                    'completed_at': datetime.utcnow()
                }}
            )
            
            return jsonify({
                'message': 'Document processed successfully',
                'document_id': document_id,
                'status': 'completed'
            })
            
        except Exception as process_error:
            # Update status to failed
            db.documents.update_one(
                {'_id': ObjectId(document_id)},
                {'$set': {
                    'status': 'failed',
                    'error': str(process_error)
                }}
            )
            raise process_error
            
    except Exception as e:
        app.logger.error(f"Processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """Get list of all documents with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        skip = (page - 1) * limit
        
        # Get total count
        total = db.documents.count_documents({})
        
        # Get documents (Cosmos DB may not have index for created_at)
        try:
            # Try to sort by creation date if index exists
            documents = list(db.documents.find()
                            .sort('created_at', -1)
                            .skip(skip)
                            .limit(limit))
        except Exception as sort_error:
            # Fallback: get documents without sorting if index doesn't exist
            app.logger.warning(f"Sort failed, fetching without sort: {str(sort_error)}")
            documents = list(db.documents.find()
                            .skip(skip)
                            .limit(limit))
        
        # Serialize documents
        serialized_docs = []
        for doc in documents:
            # Get record count for this document
            record_count = db.rfp_entries.count_documents({'document_id': doc['_id']})
            
            serialized_docs.append({
                'id': str(doc['_id']),
                'document_id': str(doc['_id']),
                'file_name': doc.get('file_name', 'Unknown'),
                'document_type': doc.get('document_type', 'RFP'),
                'status': doc.get('status', 'unknown'),
                'file_size': doc.get('file_size', 0),
                'processing_mode': doc.get('processing_mode', 'professional'),
                'records_processed': record_count,
                'total_records': doc.get('total_records'),
                'created_at': doc.get('created_at').isoformat() if doc.get('created_at') else None,
                'uploaded_by': doc.get('uploaded_by', 'anonymous'),
                'metadata': doc.get('metadata', {})
            })
        
        return jsonify({
            'total': total,
            'page': page,
            'limit': limit,
            'documents': serialized_docs
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<document_id>/status', methods=['GET'])
def get_document_status(document_id):
    """Get document processing status"""
    try:
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'document_id': str(document['_id']),
            'status': document.get('status', 'unknown'),
            'records_processed': document.get('records_processed', 0),
            'total_records': document.get('total_records', 0),
            'errors': document.get('error_details', []),
            'completed_at': document.get('completed_at').isoformat() if document.get('completed_at') else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/documents/<document_id>/analyze', methods=['GET'])
def analyze_document(document_id):
    """Analyze Excel document and return column information"""
    try:
        import pandas as pd
        
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        if document.get('document_type') != 'RFP':
            return jsonify({'error': 'Only RFP documents can be analyzed'}), 400
        
        # Read Excel file
        file_path = document['file_path']
        df = pd.read_excel(file_path)
        
        # Get column names
        columns = [str(col) for col in df.columns]
        
        # Get preview data (first 5 rows)
        preview_data = []
        for idx, row in df.head(5).iterrows():
            row_data = {}
            for col in df.columns:
                val = row[col]
                # Handle NaN and None values
                if pd.isna(val) or val is None:
                    row_data[str(col)] = ''
                else:
                    row_data[str(col)] = str(val)[:200]  # Truncate long values
            preview_data.append(row_data)
        
        return jsonify({
            'document_id': str(document['_id']),
            'file_name': document['file_name'],
            'total_rows': len(df),
            'total_columns': len(columns),
            'columns': columns,
            'preview_data': preview_data
        })
    except Exception as e:
        import traceback
        print(f"Error analyzing document: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to analyze document: {str(e)}'}), 500

@app.route('/api/documents/<document_id>/mapping', methods=['POST'])
def submit_column_mapping(document_id):
    """Submit column mapping for RFP document"""
    try:
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        if document.get('document_type') != 'RFP':
            return jsonify({'error': 'Column mapping only applicable for RFP documents'}), 400
        
        data = request.get_json()
        mappings = data.get('mappings')
        save_template = data.get('save_template', False)
        template_name = data.get('template_name')
        
        # Save template if requested
        if save_template and template_name:
            template = {
                '_id': ObjectId(),
                'name': template_name,
                'mappings': mappings,
                'created_at': datetime.utcnow(),
                'created_by': data.get('created_by', 'anonymous')
            }
            db.templates.insert_one(template)
        
        # Apply mapping and process
        file_service.apply_mapping_and_process.delay(str(document_id), mappings)
        
        return jsonify({
            'status': 'processing',
            'message': 'Column mapping applied. Processing records...'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/query', methods=['POST'])
def query_rag():
    """Query the RAG system"""
    data = request.get_json()
    query = data.get('query')
    top_n = data.get('top_n', 10)
    filters = data.get('filters', {})
    
    if not query or len(query) < 3:
        return jsonify({'error': 'Query must be at least 3 characters'}), 400
    
    # Check if vector service is available
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

@app.route('/api/search', methods=['GET', 'POST'])
def search_documents():
    """Simple keyword search in documents (supports both GET and POST)"""
    try:
        # Handle both GET and POST requests
        if request.method == 'POST':
            data = request.get_json()
            query = data.get('query', '').strip()
            limit = int(data.get('top_n', data.get('limit', 50)))
            filters = data.get('filters', {})
            document_id = filters.get('document_id', '')
        else:
            # GET request
            query = request.args.get('query', '').strip()
            limit = int(request.args.get('limit', 50))
            document_id = request.args.get('document_id', '')
            filters = {}
            if document_id:
                filters['document_id'] = document_id
        
        # Return empty results for short queries instead of error
        if not query or len(query) < 2:
            return jsonify({
                'query': query,
                'total_results': 0,
                'results': []
            })
        
        if vector_service is None:
            return jsonify({'error': 'Search service not available'}), 503
        
        # Perform vector search
        results = vector_service.search(query, limit, filters)
        
        return jsonify({
            'query': query,
            'total_results': len(results),
            'results': results
        })
    except Exception as e:
        app.logger.error(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/ask', methods=['POST'])
def intelligent_ask():
    """Ask an intelligent question using GPT-4o RAG or fallback to simple search"""
    try:
        data = request.get_json()
        question = data.get('question')
        filters = data.get('filters', {})
        max_context_docs = data.get('max_context_docs', 5)
        temperature = data.get('temperature', 0.7)
        max_answer_length = data.get('max_answer_length', 500)
        
        if not question or len(question) < 3:
            return jsonify({'error': 'Question must be at least 3 characters'}), 400
        
        # Try intelligent search first if QA service is available
        if qa_service is not None:
            result = qa_service.ask_question(
                question=question,
                filters=filters,
                top_n=max_context_docs,
                temperature=temperature,
                max_tokens=max_answer_length
            )
            
            # If intelligent search fails, fall back to simple text search
            if result.get('mode') == 'error' and result.get('error_type') == 'connection_error':
                return jsonify(_simple_text_search(question, max_context_docs))
            
            return jsonify(result)
        else:
            # Fallback to simple text search if QA service not available
            return jsonify(_simple_text_search(question, max_context_docs))
            
    except Exception as e:
        app.logger.error(f"Search error: {str(e)}")
        # Fallback to simple search on error
        try:
            return jsonify(_simple_text_search(question, max_context_docs))
        except Exception as fallback_error:
            return jsonify({'error': str(e)}), 500

def _simple_text_search(question: str, limit: int = 5) -> dict:
    """Simple keyword-based search in RFP entries as fallback"""
    try:
        if db is None:
            return {
                'answer': 'Database is not connected. Cannot perform search.',
                'sources': [],
                'mode': 'error',
                'confidence': 0.0
            }
        
        # Perform case-insensitive text search on requirement field
        search_terms = question.lower().split()
        
        # Build regex query for MongoDB
        regex_patterns = [{'requirement': {'$regex': term, '$options': 'i'}} for term in search_terms if len(term) > 2]
        
        if not regex_patterns:
            return {
                'answer': 'Please provide more specific search terms (at least 3 characters each).',
                'sources': [],
                'mode': 'no-results',
                'confidence': 0.0
            }
        
        # Search in rfp_entries collection
        results = list(db.rfp_entries.find(
            {'$or': regex_patterns}
        ).limit(limit))
        
        if not results:
            return {
                'answer': f'No RFP entries found matching "{question}". Try different keywords or check if documents have been uploaded and processed.',
                'sources': [],
                'mode': 'no-results',
                'confidence': 0.0
            }
        
        # Format results
        sources = []
        answer_parts = []
        for idx, result in enumerate(results, 1):
            source = {
                'record_id': str(result.get('_id')),
                'product': result.get('product', 'N/A'),
                'requirement': result.get('requirement', 'N/A')[:200],
                'category': result.get('requirement_category', 'N/A'),
                'response_category': result.get('response_category', 'N/A'),
                'sheet_name': result.get('sheet_name', 'N/A'),
                'file_name': result.get('file_name', 'N/A'),
                'rfp_name': result.get('rfp_name', 'N/A'),
                'bank_name': result.get('bank_name', 'N/A')
            }
            sources.append(source)
            answer_parts.append(f"{idx}. [{result.get('product', 'N/A')}] {result.get('requirement', 'N/A')[:150]}...")
        
        answer = f"Found {len(results)} relevant RFP entries (simple text search):\n\n" + "\n\n".join(answer_parts)
        
        return {
            'answer': answer,
            'sources': sources,
            'mode': 'simple-search',
            'confidence': 0.5,
            'note': 'Using simple keyword search. For better results, AI-powered semantic search requires vector database configuration.'
        }
    except Exception as e:
        app.logger.error(f"Simple search error: {str(e)}")
        return {
            'answer': f'Search failed: {str(e)}',
            'sources': [],
            'mode': 'error',
            'confidence': 0.0
        }

@app.route('/api/search/follow-up', methods=['POST'])
def intelligent_follow_up():
    """Ask a follow-up question with conversation history"""
    try:
        data = request.get_json()
        question = data.get('question')
        conversation_history = data.get('conversation_history', [])
        filters = data.get('filters', {})
        
        if not question or len(question) < 3:
            return jsonify({'error': 'Question must be at least 3 characters'}), 400
        
        result = qa_service.ask_follow_up(
            question=question,
            conversation_history=conversation_history,
            filters=filters
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search/suggestions', methods=['GET'])
def get_question_suggestions():
    """Get suggested questions based on available documents"""
    try:
        result = qa_service.suggest_questions()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/templates', methods=['GET'])
def get_templates():
    """Get all column mapping templates"""
    templates = list(db.templates.find())
    
    return jsonify([{
        'template_id': str(t['_id']),
        'template_name': t['name'],
        'created_at': t['created_at'].isoformat(),
        'mappings': t['mappings']
    } for t in templates])

@app.route('/api/documents/<document_id>/records', methods=['GET'])
def get_document_records(document_id):
    """Get processed records from a document"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    skip = (page - 1) * limit
    
    if document_id == 'recent':
        # Get recent records across all documents
        total = db.rfp_entries.count_documents({})
        records = list(db.rfp_entries.find().sort('created_at', -1).skip(skip).limit(limit))
    else:
        # Get records for specific document
        query = {'document_id': ObjectId(document_id)}
        total = db.rfp_entries.count_documents(query)
        records = list(db.rfp_entries.find(query).skip(skip).limit(limit))
    
    return jsonify({
        'total': total,
        'page': page,
        'limit': limit,
        'records': [{
            'record_id': str(r['_id']),
            'product': r.get('product', 'General'),
            'requirement': r.get('requirement', ''),
            'requirement_category': r.get('requirement_category', ''),
            'response_category': r.get('response_category', ''),
            'effort_required': r.get('effort_required'),
            'comments': r.get('comments'),
            'rfp_name': r.get('rfp_name', ''),
            'bank_name': r.get('bank_name', ''),
            'date': r.get('date').isoformat() if r.get('date') else None
        } for r in records]
    })

@app.route('/api/documents/extract-metadata', methods=['POST'])
def extract_document_metadata():
    """Extract metadata from filename using AI"""
    try:
        data = request.get_json()
        filename = data.get('filename', '')
        
        if not filename:
            return jsonify({'error': 'Filename is required'}), 400
        
        # Use simple pattern matching for now (can be enhanced with AI later)
        metadata = {
            'rfp_name': '',
            'bank_name': '',
            'product': ''
        }
        
        # Remove file extension
        name_without_ext = filename.rsplit('.', 1)[0]
        
        # Common patterns
        # Replace underscores and hyphens with spaces
        clean_name = name_without_ext.replace('_', ' ').replace('-', ' ')
        
        # Try to extract bank name (usually at the beginning)
        parts = clean_name.split()
        
        # Look for common indicators
        indicators = {
            'bank': ['Bank', 'Banking'],
            'finance': ['Finance', 'Financial'],
            'product': ['MLC', 'EPLC', 'LC', 'Trade', 'Integration', 'Frontend', 'Backend']
        }
        
        # Extract potential bank name (first 1-3 words before RFP)
        if 'RFP' in clean_name or 'rfp' in clean_name.lower():
            rfp_index = clean_name.lower().index('rfp')
            before_rfp = clean_name[:rfp_index].strip()
            
            # Bank name is likely at the start
            bank_words = before_rfp.split()[:3]
            metadata['bank_name'] = ' '.join(bank_words) if bank_words else ''
            
            # RFP name could be the whole thing
            metadata['rfp_name'] = clean_name
        else:
            # If no RFP in name, use first few words as bank name
            metadata['bank_name'] = ' '.join(parts[:2]) if len(parts) >= 2 else parts[0] if parts else ''
            metadata['rfp_name'] = clean_name
        
        # Extract product
        for word in parts:
            word_upper = word.upper()
            if word_upper in ['MLC', 'EPLC', 'LC', 'INTEGRATION', 'FRONTEND', 'BACKEND']:
                metadata['product'] = word_upper
                break
        
        # If product still empty, look for trade finance indicators
        if not metadata['product']:
            if any(word in clean_name.lower() for word in ['trade', 'finance', 'transaction']):
                metadata['product'] = 'Trade Finance'
        
        return jsonify(metadata), 200
        
    except Exception as e:
        app.logger.error(f"Error extracting metadata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        # Check if database is available
        if db is None:
            return jsonify({
                'total_documents': 0,
                'total_records': 0,
                'product_distribution': {},
                'last_upload': None,
                'error': 'Database not connected'
            }), 200
        
        # Get counts
        total_documents = db.documents.count_documents({})
        total_records = db.rfp_entries.count_documents({})
        
        # Get product distribution using aggregation
        pipeline = [
            {'$group': {
                '_id': '$product',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        
        product_stats = list(db.rfp_entries.aggregate(pipeline))
        product_distribution = {stat['_id']: stat['count'] for stat in product_stats}
        
        # Get last upload (handle Cosmos DB indexing limitation)
        try:
            last_doc = db.documents.find_one(sort=[('created_at', -1)])
        except Exception:
            # Fallback: get any document if sort fails
            last_doc = db.documents.find_one()
        
        return jsonify({
            'total_documents': total_documents,
            'total_records': total_records,
            'product_distribution': product_distribution,
            'last_upload': last_doc['created_at'].isoformat() if (last_doc and 'created_at' in last_doc) else None
        })
    except Exception as e:
        app.logger.error(f"Error in get_stats: {str(e)}")
        return jsonify({
            'total_documents': 0,
            'total_records': 0,
            'product_distribution': {},
            'last_upload': None,
            'error': str(e)
        }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import numpy as np
from celery import Celery
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import json
from bson import ObjectId
from pymongo import MongoClient
from openai import AzureOpenAI  # Azure OpenAI client
from azure.storage.blob import BlobServiceClient
import io
import tempfile

# Initialize Celery
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
celery = Celery('tasks', broker=redis_url, backend=redis_url)

# MongoDB connection for Celery tasks
def get_db():
    """Get MongoDB connection for Celery tasks"""
    mongo_uri = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/rfprag'
    client = MongoClient(mongo_uri)
    return client.get_database()

# Azure OpenAI configuration
# Support multiple environment variable names for flexibility
AZURE_OPENAI_API_KEY = (
    os.environ.get('AZURE_OPENAI_API_KEY') or 
    os.environ.get('AZURE_OPENAI_KEY') or
    os.environ.get('OPENAI_API_KEY')
)
AZURE_OPENAI_ENDPOINT = (
    os.environ.get('AZURE_OPENAI_ENDPOINT') or
    os.environ.get('AZURE_OPENAI_API_BASE') or
    os.environ.get('AZURE_EMBEDDING_ENDPOINT')
)
AZURE_OPENAI_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION', '2024-02-01')
AZURE_EMBEDDING_MODEL = os.environ.get('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-3-large')
USE_AZURE_EMBEDDINGS = os.environ.get('USE_AZURE_EMBEDDINGS', 'true').lower() == 'true'  # Changed default to 'true'

print(f"🔧 Vector Search Configuration:")
print(f"   API Key: {'✅ Set' if AZURE_OPENAI_API_KEY else '❌ Missing'}")
print(f"   Endpoint: {AZURE_OPENAI_ENDPOINT if AZURE_OPENAI_ENDPOINT else '❌ Missing'}")
print(f"   Embedding Model: {AZURE_EMBEDDING_MODEL}")
print(f"   USE_AZURE_EMBEDDINGS: {USE_AZURE_EMBEDDINGS}")

# Lazy loading of Azure client
_azure_client = None

def get_azure_client():
    """Get or initialize Azure OpenAI client"""
    global _azure_client
    if _azure_client is None and USE_AZURE_EMBEDDINGS:
        try:
            _azure_client = AzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                api_version=AZURE_OPENAI_API_VERSION,
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )
            print(f"✅ Azure OpenAI client initialized with {AZURE_EMBEDDING_MODEL}")
        except Exception as e:
            print(f"❌ Failed to initialize Azure OpenAI client: {e}")
            raise
    return _azure_client

# Initialize Azure Blob Storage
_blob_service_client = None

def get_blob_service_client():
    """Get or initialize Azure Blob Storage client"""
    global _blob_service_client
    if _blob_service_client is None:
        storage_connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        if storage_connection_string:
            try:
                _blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
                print("✅ Azure Blob Storage client initialized")
            except Exception as e:
                print(f"❌ Failed to initialize Blob Storage client: {e}")
                _blob_service_client = None
    return _blob_service_client

def download_blob_to_temp(blob_name: str) -> str:
    """Download blob to temporary file and return path"""
    blob_client = get_blob_service_client()
    if not blob_client:
        raise ValueError("Blob storage not configured")
    
    try:
        # Create temporary file
        suffix = os.path.splitext(blob_name)[1]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_path = temp_file.name
        temp_file.close()
        
        # Download blob to temp file
        blob = blob_client.get_blob_client(container="uploads", blob=blob_name)
        with open(temp_path, "wb") as f:
            f.write(blob.download_blob().readall())
        
        return temp_path
    except Exception as e:
        print(f"Failed to download blob {blob_name}: {e}")
        raise

class VectorSearchService:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()
        self.azure_client = get_azure_client() if USE_AZURE_EMBEDDINGS else None
        self.collection_name = "vector_embeddings"
        self.vector_size = 3072  # Azure OpenAI text-embedding-3-large dimension
        
        # Create index for vector search if it doesn't exist
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Create MongoDB index for efficient vector search"""
        try:
            # Create index on document_id for fast lookups
            self.db[self.collection_name].create_index("document_id")
            self.db[self.collection_name].create_index("entry_id")
            print(f"✅ MongoDB vector collection indexes created")
        except Exception as e:
            print(f"Index creation info: {e}")
    
    def embed_text(self, text: str) -> List[float]:
        """Convert text to embedding vector using Azure OpenAI"""
        if not USE_AZURE_EMBEDDINGS or not self.azure_client:
            raise Exception("Azure OpenAI embeddings not configured")
        
        try:
            # Use Azure OpenAI embeddings
            response = self.azure_client.embeddings.create(
                input=text,
                model=AZURE_EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Azure embedding failed: {e}")
            raise
    
    def index_document(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        """Add document embedding to MongoDB"""
        vector = self.embed_text(text)
        
        # Store vector in MongoDB
        vector_doc = {
            'entry_id': doc_id,
            'document_id': metadata.get('document_id'),
            'vector': vector,
            'metadata': metadata,
            'created_at': datetime.now()
        }
        
        # Upsert to MongoDB (replace if exists)
        self.db[self.collection_name].update_one(
            {'entry_id': doc_id},
            {'$set': vector_doc},
            upsert=True
        )
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        return float(np.dot(vec1_np, vec2_np) / (np.linalg.norm(vec1_np) * np.linalg.norm(vec2_np)))
    
    def search(self, query: str, top_n: int = 10, filters: Dict = None) -> List[Dict]:
        """Search for similar documents using MongoDB and cosine similarity"""
        try:
            query_vector = self.embed_text(query)
        except Exception as e:
            print(f"Failed to generate query embedding: {e}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")
        
        # Build MongoDB filter
        mongo_filter = {}
        if filters:
            if filters.get('products'):
                mongo_filter['metadata.product'] = {'$in': filters['products']}
            if filters.get('response_categories'):
                mongo_filter['metadata.response_category'] = {'$in': filters['response_categories']}
        
        # Get all vectors from MongoDB (with filters if any)
        try:
            vector_docs = list(self.db[self.collection_name].find(mongo_filter))
        except Exception as e:
            print(f"Failed to query vector database: {e}")
            raise Exception(f"Database query failed: {str(e)}")
        
        # Calculate cosine similarity for each document
        results = []
        for doc in vector_docs:
            similarity = self.cosine_similarity(query_vector, doc['vector'])
            metadata = doc.get('metadata', {})
            results.append({
                'record_id': doc['entry_id'],
                'relevance_score': similarity,
                'product': metadata.get('product'),
                'requirement': metadata.get('requirement'),
                'requirement_category': metadata.get('requirement_category'),
                'response_category': metadata.get('response_category'),
                'effort_required': metadata.get('effort_required'),
                'comments': metadata.get('comments'),
                'sheet_name': metadata.get('sheet_name'),  # Add sheet name
                'file_name': metadata.get('file_name'),  # Add file name
                'rfp_name': metadata.get('rfp_name'),
                'bank_name': metadata.get('bank_name'),
                'date': metadata.get('date'),
                'highlight': self._generate_highlight(query, metadata.get('requirement', ''))
            })
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top N results
        return results[:top_n]
    
    def _generate_highlight(self, query: str, text: str) -> str:
        """Generate highlighted snippet"""
        # Simple implementation - find query terms in text
        query_terms = query.lower().split()
        text_lower = text.lower()
        
        # Find best matching portion
        best_start = 0
        best_score = 0
        
        words = text.split()
        for i in range(len(words) - 5):
            window = ' '.join(words[i:i+10])
            score = sum(1 for term in query_terms if term in window.lower())
            if score > best_score:
                best_score = score
                best_start = i
        
        # Return highlighted portion
        if best_score > 0:
            snippet = ' '.join(words[best_start:best_start+20])
            for term in query_terms:
                snippet = snippet.replace(term, f"**{term}**")
            return f"...{snippet}..."
        
        return text[:200] + "..."

class FileProcessingService:
    def __init__(self, db):
        self.vector_service = VectorSearchService(db)
        self.db = db
    
    @staticmethod
    @celery.task(bind=True)
    def process_document(self, document_id: str):
        """Process uploaded document"""
        # Use direct MongoDB connection instead of importing from app
        db = get_db()
        
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            print(f"Document {document_id} not found")
            return
        
        try:
            # Check processing mode
            processing_mode = document.get('processing_mode', 'professional')
            
            if processing_mode == 'simple':
                # Simple mode: Auto-process without column mapping
                print(f"Processing document {document_id} in SIMPLE mode")
                file_processor = FileProcessingService(db)
                
                if document.get('document_type') == 'RFP':
                    # Process Excel as simple text chunks
                    file_processor._process_simple_rfp(document)
                else:
                    # Process PDF/DOCX as documentation
                    file_processor._process_documentation(document)
                
                db.documents.update_one(
                    {'_id': ObjectId(document_id)},
                    {
                        '$set': {
                            'status': 'completed',
                            'completed_at': datetime.now()
                        }
                    }
                )
                print(f"Document {document_id} processed successfully in simple mode")
                
            elif document.get('document_type') == 'RFP':
                # Professional mode: Wait for column mapping
                db.documents.update_one(
                    {'_id': ObjectId(document_id)},
                    {'$set': {'status': 'awaiting_mapping'}}
                )
                print(f"RFP document {document_id} awaiting mapping (Professional mode)")
            else:
                # For documentation in professional mode, process immediately
                file_processor = FileProcessingService(db)
                file_processor._process_documentation(document)
                db.documents.update_one(
                    {'_id': ObjectId(document_id)},
                    {
                        '$set': {
                            'status': 'completed',
                            'completed_at': datetime.now()
                        }
                    }
                )
                print(f"Documentation {document_id} processed successfully")
            
        except Exception as e:
            print(f"Error processing document {document_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            db.documents.update_one(
                {'_id': ObjectId(document_id)},
                {
                    '$set': {
                        'status': 'failed',
                        'error_details': [{'error': str(e)}]
                    }
                }
            )
    
    @staticmethod
    @celery.task(bind=True)
    def apply_mapping_and_process(self, document_id: str, mappings: Dict[str, str]):
        """Apply column mapping and process RFP"""
        # Use direct MongoDB connection instead of importing from app
        db = get_db()
        
        document = db.documents.find_one({'_id': ObjectId(document_id)})
        if not document:
            print(f"Document {document_id} not found")
            return
        
        vector_service = VectorSearchService()
        
        try:
            print(f"Processing RFP document {document_id} with mappings: {mappings}")
            
            # Download file from blob storage if needed
            temp_file_path = None
            if 'blob_name' in document:
                # New: file in blob storage
                temp_file_path = download_blob_to_temp(document['blob_name'])
                file_path = temp_file_path
            else:
                # Old: file on local filesystem (backward compatibility)
                file_path = document.get('file_path')
                if not file_path or not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read Excel file - handle multiple sheets
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            print(f"Found {len(sheet_names)} sheet(s): {sheet_names}")
            
            # Get first sheet (or specific sheet if specified)
            sheet_name = sheet_names[0] if sheet_names else None
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            total_records = len(df)
            
            # Debug: Print column names
            print(f"Excel columns found: {list(df.columns)}")
            print(f"Mapped requirement column: '{mappings.get('requirement', '')}'")
            print(f"Column exists in DataFrame: {mappings.get('requirement', '') in df.columns}")
            
            # Print first row data
            if len(df) > 0:
                first_row = df.iloc[0]
                print(f"First row data: {dict(first_row)}")
                req_col = mappings.get('requirement', '')
                if req_col in df.columns:
                    print(f"First row requirement value: {repr(first_row[req_col])}")
                else:
                    print(f"ERROR: Required column '{req_col}' not found in DataFrame!")
            
            db.documents.update_one(
                {'_id': ObjectId(document_id)},
                {'$set': {
                    'total_records': total_records, 
                    'status': 'processing',
                    'sheet_name': sheet_name  # Store sheet name
                }}
            )
            
            errors = []
            processed = 0
            
            for idx, row in df.iterrows():
                try:
                    # Extract data based on mapping with proper handling
                    product_val = row.get(mappings.get('product', ''), 'General')
                    requirement_val = row.get(mappings.get('requirement', ''), '')
                    req_category_val = row.get(mappings.get('requirement_category', ''), 'Must Have')
                    resp_category_val = row.get(mappings.get('response_category', ''), 'Readily Available')
                    effort_val = row.get(mappings.get('effort_required', ''), '') if mappings.get('effort_required') else None
                    comments_val = row.get(mappings.get('comments', ''), '') if mappings.get('comments') else None
                    
                    # Convert to string and handle NaN/None
                    def clean_value(val, default=''):
                        if pd.isna(val) or val is None:
                            return default
                        return str(val).strip()
                    
                    # Debug: Log the raw values for first 3 rows
                    if idx < 3:
                        print(f"Row {idx + 1} DEBUG:")
                        print(f"  Mappings: {mappings}")
                        print(f"  Available columns: {list(row.keys())}")
                        print(f"  requirement column name: '{mappings.get('requirement', '')}'")
                        print(f"  requirement raw value: {repr(requirement_val)}")
                        print(f"  requirement cleaned: '{clean_value(requirement_val)}'")
                    
                    entry = {
                        '_id': ObjectId(),
                        'document_id': ObjectId(document_id),
                        'product': clean_value(product_val, 'General'),
                        'requirement': clean_value(requirement_val, ''),
                        'requirement_category': clean_value(req_category_val, 'Must Have'),
                        'response_category': clean_value(resp_category_val, 'Readily Available'),
                        'effort_required': clean_value(effort_val, None) if effort_val is not None else None,
                        'comments': clean_value(comments_val, None) if comments_val is not None else None,
                        'sheet_name': sheet_name,  # Add sheet name
                        'file_name': document['file_name'],  # Add file name
                        'rfp_name': document.get('metadata', {}).get('rfp_name', 'Unknown RFP'),
                        'bank_name': document.get('metadata', {}).get('bank_name', 'Unknown Bank'),
                        'date': datetime.now(),
                        'created_at': datetime.now(),
                        'last_modified': datetime.now()
                    }
                    
                    # Skip if requirement is empty or too short
                    if not entry['requirement'] or len(entry['requirement']) < 3:
                        print(f"Skipping row {idx + 1}: Empty or too short requirement (value: '{entry['requirement']}')")
                        continue
                    
                    # Insert into MongoDB
                    db.rfp_entries.insert_one(entry)
                    
                    # Index in vector database
                    try:
                        vector_service.index_document(
                            doc_id=str(entry['_id']),
                            text=entry['requirement'],
                            metadata={
                                'product': entry['product'],
                                'requirement': entry['requirement'],
                                'requirement_category': entry['requirement_category'],
                                'response_category': entry['response_category'],
                                'effort_required': entry['effort_required'] or '',
                                'comments': entry['comments'] or '',
                                'sheet_name': sheet_name,  # Add sheet name to vector metadata
                                'file_name': document['file_name'],  # Add file name
                                'rfp_name': entry['rfp_name'],
                                'bank_name': entry['bank_name'],
                                'date': entry['date'].isoformat()
                            }
                        )
                    except Exception as e:
                        print(f"Warning: Failed to index entry in vector DB: {str(e)}")
                    
                    processed += 1
                    
                    # Update progress every 100 records
                    if processed % 100 == 0:
                        db.documents.update_one(
                            {'_id': ObjectId(document_id)},
                            {'$set': {'records_processed': processed}}
                        )
                        print(f"Processed {processed}/{total_records} records")
                    
                except Exception as e:
                    error_msg = f"Row {idx + 1}: {str(e)}"
                    errors.append({'row': idx + 1, 'error': str(e)})
                    print(f"Error processing row {idx + 1}: {str(e)}")
            
            # Update document status
            db.documents.update_one(
                {'_id': ObjectId(document_id)},
                {
                    '$set': {
                        'records_processed': processed,
                        'error_details': errors,
                        'status': 'completed' if not errors else 'partial',
                        'completed_at': datetime.now()
                    }
                }
            )
            
            print(f"Successfully processed {processed}/{total_records} records. Errors: {len(errors)}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Fatal error processing document {document_id}: {error_msg}")
            db.documents.update_one(
                {'_id': ObjectId(document_id)},
                {
                    '$set': {
                        'status': 'failed',
                        'error_details': [{'error': error_msg}]
                    }
                }
            )
        finally:
            # Clean up temporary file if it was created
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    print(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as cleanup_error:
                    print(f"Warning: Failed to clean up temp file: {cleanup_error}")
    
    def _process_simple_rfp(self, document: Dict):
        """Process RFP Excel file in simple mode (no column mapping)"""
        print(f"Processing RFP in Simple mode: {document['file_name']}")
        
        temp_file_path = None
        try:
            # Download file from blob storage if needed
            if 'blob_name' in document:
                # New: file in blob storage
                temp_file_path = download_blob_to_temp(document['blob_name'])
                file_path = temp_file_path
            else:
                # Old: file on local filesystem (backward compatibility)
                file_path = document.get('file_path')
                if not file_path or not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read Excel file - handle multiple sheets
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            print(f"Found {len(sheet_names)} sheet(s): {sheet_names}")
            
            # Get first sheet (or specific sheet if specified)
            sheet_name = sheet_names[0] if sheet_names else None
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            total_rows = len(df)
            
            print(f"Found {total_rows} rows with columns: {list(df.columns)}")
            print(f"Processing sheet: {sheet_name}")
            
            # Update status
            self.db.documents.update_one(
                {'_id': document['_id']},
                {'$set': {
                    'total_records': total_rows, 
                    'status': 'processing',
                    'sheet_name': sheet_name  # Store sheet name
                }}
            )
            
            processed = 0
            
            # Process each row
            for idx, row in df.iterrows():
                try:
                    # Convert entire row to text (all columns combined)
                    row_text_parts = []
                    for col_name in df.columns:
                        value = row[col_name]
                        if pd.notna(value) and str(value).strip():
                            # Include column name for context
                            row_text_parts.append(f"{col_name}: {str(value).strip()}")
                    
                    row_text = " | ".join(row_text_parts)
                    
                    # Skip empty rows
                    if not row_text or len(row_text) < 10:
                        continue
                    
                    # Create entry with minimal structure
                    entry = {
                        '_id': ObjectId(),
                        'document_id': document['_id'],
                        'requirement': row_text,
                        'product': 'General',  # Default for simple mode
                        'requirement_category': 'Auto-Processed',
                        'response_category': 'Pending Review',
                        'processing_mode': 'simple',
                        'row_number': idx + 1,
                        'sheet_name': sheet_name,  # Add sheet name
                        'file_name': document['file_name'],  # Add file name
                        'rfp_name': document.get('metadata', {}).get('rfp_name', 'Unknown RFP'),
                        'bank_name': document.get('metadata', {}).get('bank_name', 'Unknown Bank'),
                        'created_at': datetime.now(),
                        'last_modified': datetime.now()
                    }
                    
                    # Insert into MongoDB
                    self.db.rfp_entries.insert_one(entry)
                    
                    # Index in vector database
                    try:
                        self.vector_service.index_document(
                            doc_id=str(entry['_id']),
                            text=row_text,
                            metadata={
                                'document_id': str(document['_id']),
                                'requirement': row_text[:500],  # Truncate for metadata
                                'product': 'General',
                                'requirement_category': 'Auto-Processed',
                                'response_category': 'Pending Review',
                                'processing_mode': 'simple',
                                'row_number': idx + 1,
                                'sheet_name': sheet_name,  # Add sheet name to vector metadata
                                'file_name': document['file_name'],  # Add file name
                                'rfp_name': entry['rfp_name'],
                                'bank_name': entry['bank_name']
                            }
                        )
                    except Exception as e:
                        print(f"Warning: Failed to index entry in vector DB: {str(e)}")
                    
                    processed += 1
                    
                    # Update progress every 50 records
                    if processed % 50 == 0:
                        self.db.documents.update_one(
                            {'_id': document['_id']},
                            {'$set': {'records_processed': processed}}
                        )
                        print(f"Processed {processed}/{total_rows} rows in simple mode")
                
                except Exception as e:
                    print(f"Error processing row {idx + 1}: {str(e)}")
                    continue
            
            # Final update
            self.db.documents.update_one(
                {'_id': document['_id']},
                {
                    '$set': {
                        'records_processed': processed,
                        'status': 'completed',
                        'completed_at': datetime.now()
                    }
                }
            )
            
            print(f"Simple mode processing complete: {processed}/{total_rows} rows processed")
            
        except Exception as e:
            print(f"Error in simple RFP processing: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            # Clean up temporary file if it was created
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    print(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as cleanup_error:
                    print(f"Warning: Failed to clean up temp file: {cleanup_error}")
    
    def _process_documentation(self, document: Dict):
        """Process documentation file"""
        file_ext = document['file_name'].split('.')[-1].lower()
        
        temp_file_path = None
        try:
            # Download file from blob storage if needed
            if 'blob_name' in document:
                # New: file in blob storage
                temp_file_path = download_blob_to_temp(document['blob_name'])
                file_path = temp_file_path
            else:
                # Old: file on local filesystem (backward compatibility)
                file_path = document.get('file_path')
                if not file_path or not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
            
            if file_ext == 'pdf':
                text = self._extract_pdf_text(file_path)
            elif file_ext == 'docx':
                text = self._extract_docx_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Chunk text and index
            chunks = self._chunk_text(text)
            metadata = document.get('metadata', {})
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document['_id']}_chunk_{i}"
                self.vector_service.index_document(
                    doc_id=chunk_id,
                    text=chunk,
                    metadata={
                        'document_id': str(document['_id']),
                        'document_name': metadata.get('document_name', document['file_name']),
                        'related_product': metadata.get('related_product', 'General'),
                        'submodule': metadata.get('submodule', ''),
                        'document_category': metadata.get('document_category', 'Documentation'),
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                )
            
            # Update document with processed count
            self.db.documents.update_one(
                {'_id': document['_id']},
                {'$set': {'records_processed': len(chunks)}}
            )
        finally:
            # Clean up temporary file if it was created
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    print(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as cleanup_error:
                    print(f"Warning: Failed to clean up temp file: {cleanup_error}")
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = DocxDocument(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks

class DocumentService:
    """Service for document operations"""
    
    def __init__(self, db):
        self.db = db
    
    def get_preview_data(self, file_path: str, num_rows: int = 5) -> Dict[str, Any]:
        """Get preview of Excel file"""
        try:
            df = pd.read_excel(file_path, nrows=num_rows)
            return {
                'columns': df.columns.tolist(),
                'data': df.to_dict('records'),
                'total_rows': len(pd.read_excel(file_path))
            }
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")
"""
Generate Embeddings for All RFP Entries
This script generates Azure OpenAI embeddings for all RFP entries in MongoDB
"""

import os
import sys
from pymongo import MongoClient
from openai import AzureOpenAI
from datetime import datetime

# Configuration from environment variables
MONGO_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/rfp_db')
AZURE_OPENAI_KEY = os.environ.get('AZURE_OPENAI_KEY')
AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT', 'https://newfinai-app.openai.azure.com/')
AZURE_EMBEDDING_MODEL = os.environ.get('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-3-large')
AZURE_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION', '2025-01-01-preview')

def generate_embeddings():
    """Generate embeddings for all RFP entries"""
    
    print("="*80)
    print("🚀 Starting Embedding Generation")
    print("="*80)
    
    # 1. Connect to MongoDB
    print("\n📦 Connecting to MongoDB...")
    try:
        client = MongoClient(MONGO_URI)
        db = client.get_database()
        print(f"✅ Connected to database: {db.name}")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False
    
    # 2. Initialize Azure OpenAI
    print("\n🤖 Initializing Azure OpenAI...")
    if not AZURE_OPENAI_KEY:
        print("❌ AZURE_OPENAI_KEY not set in environment")
        return False
    
    try:
        azure_client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version=AZURE_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        print(f"✅ Azure OpenAI client initialized")
        print(f"   Endpoint: {AZURE_OPENAI_ENDPOINT}")
        print(f"   Model: {AZURE_EMBEDDING_MODEL}")
        print(f"   API Version: {AZURE_API_VERSION}")
    except Exception as e:
        print(f"❌ Failed to initialize Azure OpenAI: {e}")
        return False
    
    # 3. Get all RFP entries
    print("\n📄 Fetching RFP entries...")
    try:
        total_entries = db.rfp_entries.count_documents({})
        print(f"✅ Found {total_entries} RFP entries")
        
        if total_entries == 0:
            print("⚠️  No RFP entries found. Upload and process documents first.")
            return False
    except Exception as e:
        print(f"❌ Failed to fetch entries: {e}")
        return False
    
    # 4. Generate embeddings for each entry
    print("\n🔄 Generating embeddings...")
    print(f"   This will take approximately {int(total_entries * 2)} seconds...")
    print()
    
    entries = db.rfp_entries.find({})
    processed = 0
    skipped = 0
    errors = 0
    
    for entry in entries:
        entry_id = str(entry['_id'])
        
        try:
            # Check if embedding already exists
            existing = db.vector_embeddings.find_one({'entry_id': entry_id})
            if existing:
                skipped += 1
                if skipped % 10 == 0:
                    print(f"   ⏭️  Skipped {skipped} (already have embeddings)")
                continue
            
            # Prepare text for embedding
            requirement = entry.get('requirement', '')
            product = entry.get('product', '')
            category = entry.get('requirement_category', '')
            
            # Combine fields for better semantic search
            text_to_embed = f"{product} {category}: {requirement}"
            
            # Generate embedding
            response = azure_client.embeddings.create(
                input=text_to_embed,
                model=AZURE_EMBEDDING_MODEL
            )
            vector = response.data[0].embedding
            
            # Store in MongoDB
            vector_doc = {
                'entry_id': entry_id,
                'document_id': entry.get('document_id'),
                'vector': vector,
                'metadata': {
                    'product': entry.get('product'),
                    'requirement': entry.get('requirement'),
                    'requirement_category': entry.get('requirement_category'),
                    'response_category': entry.get('response_category'),
                    'effort_required': entry.get('effort_required'),
                    'comments': entry.get('comments'),
                    'sheet_name': entry.get('sheet_name'),
                    'file_name': entry.get('file_name'),
                    'rfp_name': entry.get('rfp_name'),
                    'bank_name': entry.get('bank_name'),
                    'date': entry.get('date')
                },
                'created_at': datetime.now()
            }
            
            db.vector_embeddings.upsert_one(
                {'entry_id': entry_id},
                {'$set': vector_doc},
                upsert=True
            )
            
            processed += 1
            
            if processed % 10 == 0:
                progress = (processed / total_entries) * 100
                print(f"   📊 Progress: {processed}/{total_entries} ({progress:.1f}%)")
        
        except Exception as e:
            errors += 1
            print(f"   ❌ Error processing entry {entry_id}: {e}")
            if errors > 10:
                print("   ⚠️  Too many errors, stopping...")
                return False
    
    # 5. Summary
    print("\n" + "="*80)
    print("✅ Embedding Generation Complete!")
    print("="*80)
    print(f"   Total Entries: {total_entries}")
    print(f"   ✅ Processed: {processed}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   ❌ Errors: {errors}")
    print()
    
    # 6. Verify embeddings
    print("🔍 Verifying embeddings...")
    embedding_count = db.vector_embeddings.count_documents({})
    print(f"   Vector embeddings in database: {embedding_count}")
    
    if embedding_count >= total_entries:
        print("   ✅ All entries have embeddings!")
        print("\n🎉 You can now use intelligent search with GPT-4o!")
        return True
    else:
        print(f"   ⚠️  Missing embeddings for {total_entries - embedding_count} entries")
        return False

if __name__ == "__main__":
    success = generate_embeddings()
    sys.exit(0 if success else 1)

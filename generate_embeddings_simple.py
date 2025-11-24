"""
Quick script to generate embeddings for all RFP entries
"""

import os
from pymongo import MongoClient
from openai import AzureOpenAI
from datetime import datetime

# Configuration - Use environment variables for security
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-large")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

# Validate required environment variables
if not AZURE_OPENAI_KEY or not AZURE_OPENAI_ENDPOINT:
    print("❌ Error: Required environment variables not set!")
    print("   Please set: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT")
    print("   Optional: MONGO_URI, AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME, AZURE_OPENAI_API_VERSION")
    exit(1)

print("="*80)
print("🚀 Generating Embeddings for RFP Search")
print("="*80)

# Connect to MongoDB
print("\n📦 Connecting to Cosmos DB...")
client = MongoClient(MONGO_URI)
db = client.rfp_db
print(f"✅ Connected to database: {db.name}")

# Initialize Azure OpenAI
print("\n🤖 Initializing Azure OpenAI...")
azure_client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)
print(f"✅ Azure OpenAI initialized")
print(f"   Endpoint: {AZURE_OPENAI_ENDPOINT}")
print(f"   Model: {AZURE_EMBEDDING_MODEL}")

# Get all RFP entries
print("\n📄 Fetching RFP entries...")
total_entries = db.rfp_entries.count_documents({})
print(f"✅ Found {total_entries} RFP entries")

if total_entries == 0:
    print("⚠️  No RFP entries found!")
    exit(1)

# Check existing embeddings
existing_count = db.vector_embeddings.count_documents({})
print(f"   Currently have {existing_count} embeddings")

# Generate embeddings
print(f"\n🔄 Generating embeddings (this will take ~{int(total_entries * 2)} seconds)...")
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
            if skipped % 20 == 0:
                print(f"   ⏭️  Skipped {skipped} (already exist)")
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
        
        db.vector_embeddings.update_one(
            {'entry_id': entry_id},
            {'$set': vector_doc},
            upsert=True
        )
        
        processed += 1
        
        if processed % 20 == 0:
            progress = (processed + skipped) / total_entries * 100
            print(f"   📊 Progress: {processed + skipped}/{total_entries} ({progress:.1f}%) - Generated: {processed}, Skipped: {skipped}")
    
    except Exception as e:
        errors += 1
        print(f"   ❌ Error processing entry {entry_id}: {e}")
        if errors > 10:
            print("   ⚠️  Too many errors, stopping...")
            break

# Final summary
final_count = db.vector_embeddings.count_documents({})
print("\n" + "="*80)
print("✅ COMPLETE!")
print("="*80)
print(f"   Total Entries: {total_entries}")
print(f"   Generated: {processed}")
print(f"   Skipped: {skipped}")
print(f"   Errors: {errors}")
print(f"   Final Embedding Count: {final_count}")
print()
print("🎉 You can now use intelligent search with GPT-4o!")
print("="*80)

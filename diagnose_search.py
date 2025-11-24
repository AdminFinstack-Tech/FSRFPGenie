#!/usr/bin/env python3
"""
RFP Search Diagnostic Tool
Checks database status and helps troubleshoot search issues
"""

import pymongo
import os
from datetime import datetime

def check_mongodb_connection():
    """Test MongoDB connection"""
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.server_info()  # Force connection
        return client['rfp_system'], "✅ Connected"
    except Exception as e:
        return None, f"❌ Failed: {str(e)}"

def check_azure_config():
    """Check Azure OpenAI configuration"""
    api_key = os.environ.get('AZURE_OPENAI_API_KEY')
    endpoint = os.environ.get('AZURE_OPENAI_API_BASE')
    deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o')
    embedding = os.environ.get('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-3-large')
    use_embeddings = os.environ.get('USE_AZURE_EMBEDDINGS', 'false')
    
    return {
        'api_key_set': bool(api_key),
        'endpoint_set': bool(endpoint),
        'deployment': deployment,
        'embedding': embedding,
        'use_embeddings': use_embeddings,
        'status': '✅ Configured' if api_key and endpoint else '❌ Missing configuration'
    }

def check_documents(db):
    """Check uploaded documents"""
    try:
        count = db.documents.count_documents({})
        docs = list(db.documents.find().sort('uploaded_at', -1).limit(10))
        
        return {
            'total': count,
            'recent': [{
                'filename': doc.get('filename'),
                'rfp_name': doc.get('rfp_name'),
                'status': doc.get('status'),
                'type': doc.get('document_type'),
                'uploaded': doc.get('uploaded_at')
            } for doc in docs],
            'status': '✅ Documents found' if count > 0 else '⚠️ No documents uploaded'
        }
    except Exception as e:
        return {'total': 0, 'recent': [], 'status': f'❌ Error: {str(e)}'}

def check_vector_embeddings(db):
    """Check vector embeddings"""
    try:
        count = db.vector_embeddings.count_documents({})
        
        # Get sample
        sample = db.vector_embeddings.find_one({})
        
        # Check for specific keywords
        alert_count = db.vector_embeddings.count_documents({
            'metadata.requirement': {'$regex': 'alert|email|sms|notification', '$options': 'i'}
        })
        
        return {
            'total': count,
            'has_alert_keywords': alert_count,
            'sample_metadata': list(sample.get('metadata', {}).keys()) if sample else [],
            'status': '✅ Embeddings exist' if count > 0 else '❌ No embeddings - upload files!'
        }
    except Exception as e:
        return {'total': 0, 'has_alert_keywords': 0, 'sample_metadata': [], 'status': f'❌ Error: {str(e)}'}

def search_for_alerts(db):
    """Search for alert-related requirements"""
    try:
        results = list(db.vector_embeddings.find({
            '$or': [
                {'metadata.requirement': {'$regex': 'alert', '$options': 'i'}},
                {'metadata.requirement': {'$regex': 'email', '$options': 'i'}},
                {'metadata.requirement': {'$regex': 'sms', '$options': 'i'}},
                {'metadata.requirement': {'$regex': 'notification', '$options': 'i'}}
            ]
        }).limit(5))
        
        return {
            'found': len(results),
            'requirements': [{
                'record_id': str(result.get('entry_id')),
                'requirement': result.get('metadata', {}).get('requirement', 'N/A')[:100] + '...',
                'product': result.get('metadata', {}).get('product'),
                'sheet_name': result.get('metadata', {}).get('sheet_name')
            } for result in results],
            'status': '✅ Found alert requirements' if results else '❌ No alert requirements found'
        }
    except Exception as e:
        return {'found': 0, 'requirements': [], 'status': f'❌ Error: {str(e)}'}

def print_report(db, azure_config):
    """Print diagnostic report"""
    print("=" * 80)
    print("🔍 RFP SEARCH SYSTEM DIAGNOSTIC REPORT")
    print("=" * 80)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # MongoDB Status
    print("📊 MONGODB STATUS")
    print("-" * 80)
    print(f"Connection: ✅ Connected to rfp_system database")
    print()
    
    # Azure Configuration
    print("☁️  AZURE OPENAI CONFIGURATION")
    print("-" * 80)
    print(f"Status: {azure_config['status']}")
    print(f"API Key: {'✅ Set' if azure_config['api_key_set'] else '❌ Missing'}")
    print(f"Endpoint: {'✅ Set' if azure_config['endpoint_set'] else '❌ Missing'}")
    print(f"GPT Model: {azure_config['deployment']}")
    print(f"Embedding Model: {azure_config['embedding']}")
    print(f"Use Embeddings: {azure_config['use_embeddings']}")
    print()
    
    # Documents
    docs_info = check_documents(db)
    print("📁 UPLOADED DOCUMENTS")
    print("-" * 80)
    print(f"Status: {docs_info['status']}")
    print(f"Total Documents: {docs_info['total']}")
    if docs_info['recent']:
        print("\nRecent uploads:")
        for doc in docs_info['recent'][:5]:
            print(f"  📄 {doc['filename']}")
            print(f"     RFP: {doc['rfp_name']}, Status: {doc['status']}, Type: {doc['type']}")
    print()
    
    # Vector Embeddings
    embeddings_info = check_vector_embeddings(db)
    print("🔢 VECTOR EMBEDDINGS")
    print("-" * 80)
    print(f"Status: {embeddings_info['status']}")
    print(f"Total Embeddings: {embeddings_info['total']}")
    print(f"Alert-related: {embeddings_info['has_alert_keywords']}")
    if embeddings_info['sample_metadata']:
        print(f"Metadata fields: {', '.join(embeddings_info['sample_metadata'])}")
    print()
    
    # Alert Search
    alert_search = search_for_alerts(db)
    print("🔔 ALERT/EMAIL/SMS REQUIREMENTS")
    print("-" * 80)
    print(f"Status: {alert_search['status']}")
    print(f"Found: {alert_search['found']} requirements")
    if alert_search['requirements']:
        print("\nMatching requirements:")
        for req in alert_search['requirements']:
            print(f"  📝 ID: {req['record_id']}")
            print(f"     Product: {req['product']}")
            print(f"     Sheet: {req['sheet_name']}")
            print(f"     Text: {req['requirement']}")
            print()
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS")
    print("-" * 80)
    
    if not azure_config['api_key_set'] or not azure_config['endpoint_set']:
        print("❌ Azure OpenAI not configured!")
        print("   → Set AZURE_OPENAI_API_KEY and AZURE_OPENAI_API_BASE in docker-compose.yml")
        print("   → Restart services: docker-compose restart backend")
        print()
    
    if docs_info['total'] == 0:
        print("⚠️  No documents uploaded!")
        print("   → Go to http://localhost:8080/upload")
        print("   → Upload your Excel files with RFP requirements")
        print()
    
    if embeddings_info['total'] == 0:
        print("❌ No vector embeddings created!")
        print("   → Upload documents first")
        print("   → Check document processing status")
        print("   → Verify Azure OpenAI is configured")
        print()
    
    if alert_search['found'] == 0 and embeddings_info['total'] > 0:
        print("⚠️  No alert/email/SMS requirements found in database!")
        print("   → Upload the Excel file containing alert notification requirements")
        print("   → Requirement example: 'Any transaction...alert should be generated by e-mail or SMS'")
        print("   → Check file: Annex_2_Detailed_Requirements_Update2.xlsx or similar")
        print()
    
    if alert_search['found'] > 0:
        print("✅ All systems operational!")
        print("   → Documents uploaded")
        print("   → Embeddings created")
        print("   → Alert requirements indexed")
        print("   → Search should work correctly")
        print()
    
    print("=" * 80)
    print("📚 For more help, see: HOW_TO_FIX_SEARCH_RESULTS.md")
    print("=" * 80)

def main():
    """Run diagnostics"""
    # Check MongoDB
    db, mongo_status = check_mongodb_connection()
    
    if db is None:
        print(f"❌ Cannot connect to MongoDB: {mongo_status}")
        print("   → Make sure MongoDB container is running: docker-compose ps")
        return
    
    # Check Azure
    azure_config = check_azure_config()
    
    # Print full report
    print_report(db, azure_config)

if __name__ == "__main__":
    main()

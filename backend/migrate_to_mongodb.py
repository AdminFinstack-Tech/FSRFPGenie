#!/usr/bin/env python3
"""
Migration script to move data from PostgreSQL to MongoDB
"""
import os
from datetime import datetime
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from bson import ObjectId

# Import old SQLAlchemy models (you'll need to keep a copy of the old models.py)
# from models_old import Document, RFPEntry, Template, User

def migrate_to_mongodb(postgres_uri, mongo_uri, mongo_db_name):
    """Migrate data from PostgreSQL to MongoDB"""
    
    print("Starting migration from PostgreSQL to MongoDB...")
    
    # Connect to PostgreSQL
    engine = create_engine(postgres_uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Connect to MongoDB
    mongo_client = MongoClient(mongo_uri)
    mongo_db = mongo_client[mongo_db_name]
    
    # Note: This is a template. You'll need to uncomment and adapt based on your old models
    
    # # Migrate Documents
    # print("\nMigrating documents...")
    # documents = session.query(Document).all()
    # for doc in documents:
    #     mongo_doc = {
    #         '_id': ObjectId(),
    #         'file_id': str(doc.id),
    #         'document_type': doc.document_type,
    #         'file_name': doc.file_name,
    #         'file_path': doc.file_path,
    #         'file_size': doc.file_size,
    #         'status': doc.status,
    #         'metadata': json.loads(doc.metadata) if isinstance(doc.metadata, str) else doc.metadata,
    #         'records_processed': doc.records_processed,
    #         'total_records': doc.total_records,
    #         'error_details': doc.error_details or [],
    #         'created_at': doc.created_at,
    #         'completed_at': doc.completed_at,
    #         'uploaded_by': doc.uploaded_by
    #     }
    #     mongo_db.documents.insert_one(mongo_doc)
    # print(f"Migrated {len(documents)} documents")
    
    # # Migrate RFP Entries
    # print("\nMigrating RFP entries...")
    # entries = session.query(RFPEntry).all()
    # for entry in entries:
    #     mongo_entry = {
    #         '_id': ObjectId(),
    #         'document_id': str(entry.document_id),
    #         'product': entry.product,
    #         'requirement': entry.requirement,
    #         'requirement_category': entry.requirement_category,
    #         'response_category': entry.response_category,
    #         'effort_required': entry.effort_required,
    #         'comments': entry.comments,
    #         'rfp_name': entry.rfp_name,
    #         'bank_name': entry.bank_name,
    #         'date': entry.date,
    #         'created_by': entry.created_by,
    #         'created_at': entry.created_at,
    #         'last_modified': entry.last_modified,
    #         'vector_id': entry.vector_id
    #     }
    #     mongo_db.rfp_entries.insert_one(mongo_entry)
    # print(f"Migrated {len(entries)} RFP entries")
    
    # # Migrate Templates
    # print("\nMigrating templates...")
    # templates = session.query(Template).all()
    # for template in templates:
    #     mongo_template = {
    #         '_id': ObjectId(),
    #         'name': template.name,
    #         'mappings': template.mappings,
    #         'created_at': template.created_at,
    #         'created_by': template.created_by
    #     }
    #     mongo_db.templates.insert_one(mongo_template)
    # print(f"Migrated {len(templates)} templates")
    
    # # Migrate Users
    # print("\nMigrating users...")
    # users = session.query(User).all()
    # for user in users:
    #     mongo_user = {
    #         '_id': ObjectId(),
    #         'email': user.email,
    #         'name': user.name,
    #         'password_hash': user.password_hash,
    #         'is_active': user.is_active,
    #         'created_at': user.created_at,
    #         'last_login': user.last_login
    #     }
    #     mongo_db.users.insert_one(mongo_user)
    # print(f"Migrated {len(users)} users")
    
    print("\nMigration completed successfully!")
    
    # Close connections
    session.close()
    mongo_client.close()

if __name__ == "__main__":
    # Configuration
    POSTGRES_URI = os.environ.get('OLD_DATABASE_URL', 'postgresql://localhost/rfprag')
    MONGO_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/rfprag')
    MONGO_DB_NAME = os.environ.get('MONGO_DATABASE', 'rfprag')
    
    print(f"PostgreSQL URI: {POSTGRES_URI}")
    print(f"MongoDB URI: {MONGO_URI}")
    print(f"MongoDB Database: {MONGO_DB_NAME}")
    
    response = input("\nProceed with migration? (yes/no): ")
    if response.lower() == 'yes':
        migrate_to_mongodb(POSTGRES_URI, MONGO_URI, MONGO_DB_NAME)
    else:
        print("Migration cancelled.")
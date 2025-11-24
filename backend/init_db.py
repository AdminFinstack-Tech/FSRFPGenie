#!/usr/bin/env python3
"""
Initialize MongoDB database with required collections and indexes
"""

from pymongo import MongoClient
from models import INDEXES, create_indexes
from config import Config
import sys

def init_database():
    """Initialize MongoDB database"""
    try:
        # Connect to MongoDB
        client = MongoClient(Config.MONGO_URI)
        db = client[Config.MONGO_DATABASE]
        
        print(f"Connected to MongoDB database: {Config.MONGO_DATABASE}")
        
        # Create collections if they don't exist
        collections = ['documents', 'rfp_entries', 'templates', 'users']
        
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"Created collection: {collection_name}")
            else:
                print(f"Collection already exists: {collection_name}")
        
        # Create indexes
        print("\nCreating indexes...")
        create_indexes(db)
        
        # Print index information
        for collection_name in collections:
            if collection_name in INDEXES:
                collection = db[collection_name]
                indexes = list(collection.list_indexes())
                print(f"\nIndexes for {collection_name}:")
                for index in indexes:
                    print(f"  - {index['name']}: {index['key']}")
        
        print("\n✅ Database initialization completed successfully!")
        
        # Print connection string for reference
        print(f"\nConnection string: {Config.MONGO_URI}")
        print(f"Database name: {Config.MONGO_DATABASE}")
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
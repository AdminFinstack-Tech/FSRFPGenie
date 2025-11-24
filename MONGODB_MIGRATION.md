# MongoDB Migration Guide

## Overview

This RFP RAG system has been updated to use MongoDB instead of PostgreSQL. MongoDB provides better flexibility for document-oriented data and simplifies the schema for RFP entries and documents.

## Key Changes

### 1. Database Technology
- **Before**: PostgreSQL (Relational Database)
- **After**: MongoDB (NoSQL Document Database)

### 2. Dependencies Updated
- Removed: `psycopg2-binary`, `SQLAlchemy`, `Flask-SQLAlchemy`, `Flask-Migrate`
- Added: `pymongo`, `Flask-PyMongo`, `mongomock` (for testing)

### 3. Data Models
- Converted from SQLAlchemy ORM models to Pydantic models
- Using MongoDB ObjectId instead of UUID
- Document-based structure instead of relational tables

### 4. Connection Configuration
- **Before**: `DATABASE_URL=postgresql://...`
- **After**: `MONGO_URI=mongodb://localhost:27017/rfprag`

## Benefits of MongoDB for RFP System

1. **Flexible Schema**: Easy to add new fields to documents without migrations
2. **Natural Document Structure**: RFP entries and metadata fit well in document format
3. **Better Performance**: No joins needed for querying related data
4. **Scalability**: Easier horizontal scaling with sharding
5. **JSON Native**: Direct compatibility with API responses

## Database Structure

### Collections

1. **documents**
   - Stores uploaded file metadata
   - Tracks processing status
   - Contains file information and metadata

2. **rfp_entries**
   - Individual RFP requirements
   - Links to parent document via document_id
   - Indexed for fast queries

3. **templates**
   - Column mapping templates
   - Reusable configurations

4. **users**
   - User authentication data
   - Profile information

### Indexes

Optimized indexes for common queries:
- `documents`: created_at, status, document_type
- `rfp_entries`: document_id, product, response_category, date, vector_id
- `templates`: name, created_at
- `users`: email (unique)

## Migration Steps from PostgreSQL

If migrating from an existing PostgreSQL installation:

### 1. Export PostgreSQL Data
```python
# migrate_from_postgres.py
import psycopg2
import pymongo
from datetime import datetime

# Connect to PostgreSQL
pg_conn = psycopg2.connect("postgresql://...")
pg_cursor = pg_conn.cursor()

# Connect to MongoDB
mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["rfprag"]

# Migrate documents
pg_cursor.execute("SELECT * FROM documents")
documents = pg_cursor.fetchall()
for doc in documents:
    mongo_doc = {
        "_id": doc["id"],  # Preserve original ID
        "document_type": doc["document_type"],
        "file_name": doc["file_name"],
        # ... map other fields
        "created_at": doc["created_at"]
    }
    mongo_db.documents.insert_one(mongo_doc)

# Repeat for other tables...
```

### 2. Update Application Code
- Replace SQLAlchemy queries with PyMongo operations
- Update model imports
- Adjust ID handling (ObjectId vs UUID)

### 3. Test Migration
```bash
# Initialize MongoDB
python init_db.py

# Run tests
pytest

# Verify data integrity
python verify_migration.py
```

## Common Query Conversions

### PostgreSQL to MongoDB

**Find by ID:**
```python
# PostgreSQL
document = Document.query.get(id)

# MongoDB
document = db.documents.find_one({"_id": ObjectId(id)})
```

**Filter records:**
```python
# PostgreSQL
records = RFPEntry.query.filter_by(product="MLC").all()

# MongoDB
records = list(db.rfp_entries.find({"product": "MLC"}))
```

**Count documents:**
```python
# PostgreSQL
count = Document.query.count()

# MongoDB
count = db.documents.count_documents({})
```

**Aggregation:**
```python
# PostgreSQL
result = db.session.query(
    RFPEntry.product, 
    func.count(RFPEntry.id)
).group_by(RFPEntry.product).all()

# MongoDB
pipeline = [
    {"$group": {
        "_id": "$product",
        "count": {"$sum": 1}
    }}
]
result = list(db.rfp_entries.aggregate(pipeline))
```

## Development Tips

1. **Use MongoDB Compass** for visual database exploration
2. **Enable MongoDB profiling** during development to optimize queries
3. **Use compound indexes** for queries with multiple fields
4. **Consider TTL indexes** for automatic document expiration
5. **Use MongoDB transactions** for critical operations

## Docker Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:6.0
    container_name: rfprag_mongodb
    environment:
      MONGO_INITDB_DATABASE: rfprag
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: adminpass
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
      - ./mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro

volumes:
  mongo_data:
```

## Backup and Restore

### Backup
```bash
mongodump --uri="mongodb://localhost:27017/rfprag" --out=backup/
```

### Restore
```bash
mongorestore --uri="mongodb://localhost:27017/rfprag" backup/rfprag/
```

## Performance Optimization

1. **Index Usage**: Ensure queries use indexes with `explain()`
2. **Projection**: Only retrieve needed fields
3. **Batch Operations**: Use `insert_many()` for bulk inserts
4. **Connection Pooling**: PyMongo handles this automatically

## Troubleshooting

### Connection Issues
- Verify MongoDB is running: `systemctl status mongod`
- Check connection string format
- Ensure authentication is configured

### Performance Issues
- Check index usage: `db.collection.getIndexes()`
- Monitor with: `db.currentOp()`
- Profile slow queries: `db.setProfilingLevel(1, { slowms: 100 })`

### Data Migration Issues
- Validate data types match Pydantic models
- Handle ObjectId conversions properly
- Check for unique constraint violations
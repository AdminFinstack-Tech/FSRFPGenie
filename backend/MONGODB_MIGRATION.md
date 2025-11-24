# MongoDB Migration Guide

This guide explains how to set up and use MongoDB for the RFPRAG backend, which has been migrated from PostgreSQL.

## Prerequisites

1. MongoDB installed and running (version 4.4 or higher recommended)
2. Python 3.8+ with pip

## Installation

1. Install the updated dependencies:
```bash
pip install -r requirements.txt
```

2. Set up MongoDB connection (optional, defaults to localhost):
```bash
export MONGODB_URI="mongodb://localhost:27017/rfprag"
export MONGO_DATABASE="rfprag"
```

## Database Initialization

Initialize the MongoDB database with required collections and indexes:

```bash
python init_db.py
```

To drop and recreate the database (WARNING: This will delete all data):
```bash
python init_db.py --drop
```

## Configuration

Update your environment variables or `.env` file:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/rfprag
MONGO_DATABASE=rfprag

# If using MongoDB Atlas or remote MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/rfprag?retryWrites=true&w=majority
```

## Key Changes from PostgreSQL

### 1. Document Structure
- Tables are now collections
- Rows are now documents
- Primary keys use MongoDB ObjectId instead of UUID
- Foreign keys are stored as string references

### 2. Collections
- `documents` - Uploaded RFP and documentation files
- `rfp_entries` - Individual RFP requirement entries
- `templates` - Column mapping templates
- `users` - User accounts

### 3. Indexes
The following indexes are automatically created:
- documents: file_id (unique), status, created_at, document_type
- rfp_entries: product, response_category, date, document_id, created_at, vector_id
- templates: name (unique)
- users: email (unique)

### 4. API Changes
The API remains the same, but internally:
- Uses PyMongo instead of SQLAlchemy
- Document IDs are ObjectId strings
- Queries use MongoDB syntax
- Aggregations use MongoDB pipeline

## Migration from PostgreSQL

If you have existing data in PostgreSQL:

1. Keep a copy of your old `models.py` as `models_old.py`
2. Update the migration script `migrate_to_mongodb.py`
3. Run the migration:
```bash
python migrate_to_mongodb.py
```

## Development Tips

### MongoDB Shell Commands
```bash
# Connect to MongoDB
mongo rfprag

# Show collections
show collections

# Count documents
db.documents.countDocuments()
db.rfp_entries.countDocuments()

# Find documents
db.documents.find({status: "completed"}).limit(5)

# Create indexes manually if needed
db.rfp_entries.createIndex({product: 1})
```

### Using MongoDB Compass
MongoDB Compass provides a GUI for:
- Viewing and editing documents
- Running queries
- Monitoring performance
- Managing indexes

## Testing

The application includes `mongomock` for testing without a real MongoDB instance:

```python
import mongomock

# In tests
mongo_client = mongomock.MongoClient()
```

## Performance Considerations

1. **Indexing**: Ensure all frequently queried fields are indexed
2. **Aggregations**: Use MongoDB aggregation pipeline for complex queries
3. **Pagination**: Use skip() and limit() for efficient pagination
4. **Projections**: Only fetch required fields to reduce data transfer

## Troubleshooting

### Connection Issues
```bash
# Test MongoDB connection
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); print(client.server_info())"
```

### Index Issues
```bash
# Recreate indexes
python init_db.py
```

### Performance Issues
- Check slow queries in MongoDB logs
- Use explain() to analyze query performance
- Consider adding compound indexes for complex queries

## Backup and Restore

### Backup
```bash
mongodump --db rfprag --out backup/
```

### Restore
```bash
mongorestore --db rfprag backup/rfprag/
```

## Docker Support

For containerized deployment:
```yaml
version: '3.8'
services:
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: rfprag

volumes:
  mongodb_data:
```
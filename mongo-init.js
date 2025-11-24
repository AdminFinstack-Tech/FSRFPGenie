db = db.getSiblingDB('rfpai_db');

db.createUser({
  user: 'rfpai_user',
  pwd: 'rfpai_password',
  roles: [
    {
      role: 'readWrite',
      db: 'rfpai_db'
    }
  ]
});

// Create collections
db.createCollection('documents');
db.createCollection('templates');
db.createCollection('mappings');

// Create indexes
db.documents.createIndex({ filename: 1 });
db.documents.createIndex({ upload_date: -1 });
db.templates.createIndex({ name: 1 });
db.templates.createIndex({ created_at: -1 });
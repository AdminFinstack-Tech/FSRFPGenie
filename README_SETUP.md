# RFP RAG System - Setup Instructions

## Overview
A modern RFP (Request for Proposal) management system with RAG (Retrieval-Augmented Generation) capabilities, built with Flask backend and Vue.js frontend using Vuetify and Tailwind CSS.

## Prerequisites

- Python 3.11+
- Node.js 16+
- MongoDB 5.0+ (NoSQL database)
- Redis (for task queue)
- Qdrant vector database (or alternative like Pinecone/Weaviate)

## Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env file with your configuration
```

### 5. Set up MongoDB database
```bash
# Start MongoDB service
# On macOS with Homebrew:
brew services start mongodb-community

# On Ubuntu/Debian:
sudo systemctl start mongod

# On Windows:
# Start MongoDB from Services or run mongod.exe
```

### 6. Initialize database collections and indexes
```bash
python init_db.py
```

### 7. Start Redis (for Celery)
```bash
redis-server
```

### 8. Start Celery worker (in a new terminal)
```bash
cd backend
source venv/bin/activate
celery -A services.celery worker --loglevel=info
```

### 9. Start Qdrant vector database
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 10. Run Flask application
```bash
flask run
```

The backend will be available at `http://localhost:5000`

## Frontend Setup

### 1. Navigate to frontend directory
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Set up environment variables
```bash
echo "VUE_APP_API_URL=http://localhost:5000/api" > .env.local
```

### 4. Run development server
```bash
npm run serve
```

The frontend will be available at `http://localhost:8080`

## Quick Start with Docker (Alternative)

### 1. Create docker-compose.yml
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:6.0
    environment:
      MONGO_INITDB_DATABASE: rfprag
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: adminpass
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      MONGO_URI: mongodb://admin:adminpass@mongodb:27017/rfprag?authSource=admin
      REDIS_URL: redis://redis:6379/0
      VECTOR_DB_URL: http://qdrant:6333
    depends_on:
      - mongodb
      - redis
      - qdrant
    volumes:
      - ./backend/uploads:/app/uploads

  celery:
    build: ./backend
    command: celery -A services.celery worker --loglevel=info
    environment:
      MONGO_URI: mongodb://admin:adminpass@mongodb:27017/rfprag?authSource=admin
      REDIS_URL: redis://redis:6379/0
      VECTOR_DB_URL: http://qdrant:6333
    depends_on:
      - mongodb
      - redis
      - qdrant

  frontend:
    build: ./frontend
    ports:
      - "8080:8080"
    environment:
      VUE_APP_API_URL: http://localhost:5000/api
    depends_on:
      - backend

volumes:
  mongo_data:
  qdrant_data:
```

### 2. Create Dockerfiles

**backend/Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

**frontend/Dockerfile:**
```dockerfile
FROM node:16-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

### 3. Run with Docker Compose
```bash
docker-compose up -d
```

## Features

1. **Document Upload**
   - Support for Excel (RFP) and PDF/DOCX (Documentation)
   - Intelligent column mapping for RFP files
   - Metadata tagging and categorization

2. **Semantic Search**
   - Natural language queries
   - Vector-based similarity matching
   - Advanced filtering options

3. **Beautiful UI/UX**
   - Modern Material Design with Vuetify
   - Responsive layout with Tailwind CSS
   - Smooth animations and transitions
   - Dark mode support (theme switching)

4. **Column Mapping**
   - Visual mapping interface
   - Template saving for reuse
   - Data preview before processing

5. **Dashboard**
   - Real-time statistics
   - Product distribution charts
   - Recent activity tracking

## Development Tips

### Backend Development
```bash
# Run with auto-reload
flask run --debug

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

### Frontend Development
```bash
# Run with hot-reload
npm run serve

# Build for production
npm run build

# Run linter
npm run lint
```

## Production Deployment

1. Set proper environment variables
2. Use production database
3. Configure proper CORS origins
4. Set up SSL certificates
5. Use production-grade servers (Gunicorn/uWSGI for Flask, Nginx for static files)
6. Set up monitoring (Prometheus, Grafana)
7. Configure backups

## Troubleshooting

### Common Issues

1. **Database connection errors**
   - Check MongoDB is running
   - Verify MONGO_URI in .env
   - Ensure MongoDB authentication is properly configured

2. **Vector search not working**
   - Ensure Qdrant is running
   - Check VECTOR_DB_URL configuration

3. **File upload fails**
   - Check upload folder permissions
   - Verify MAX_CONTENT_LENGTH setting

4. **CORS errors**
   - Update CORS_ORIGINS in backend config
   - Check proxy settings in vue.config.js

## Support

For issues or questions:
- Check the logs in backend/logs/
- Review error messages in browser console
- Ensure all services are running

## License

This project is proprietary and confidential.
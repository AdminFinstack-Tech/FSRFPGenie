# Docker Setup for RFPAI

This guide explains how to run the RFPAI application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- At least 4GB of available RAM

## Quick Start

1. **Clone the repository** (if you haven't already)

2. **Run all services together:**
   ```bash
   docker-compose up --build -d
   ```

3. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:5000
   - MongoDB: mongodb://localhost:27017

## Individual Service Management

### MongoDB Only

To run just MongoDB:
```bash
docker-compose -f docker-compose.mongodb.yml up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Stop services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (data will be lost)
docker-compose down -v
```

## Configuration

### MongoDB Credentials
Default credentials are set in `docker-compose.yml`:
- Root Username: `admin`
- Root Password: `adminpassword`
- Database: `rfpai_db`
- App User: `rfpai_user`
- App Password: `rfpai_password`

**Important:** Change these credentials in production!

### Backend Configuration
The backend uses environment variables defined in `docker-compose.yml`:
- `MONGODB_URI`: Connection string for MongoDB
- `UPLOAD_FOLDER`: Directory for file uploads

### Frontend Configuration
The frontend is configured to proxy API requests to the backend through Nginx.

## Troubleshooting

### Build Errors
If you encounter build errors:
1. Make sure all required files are present
2. Check that ports 80, 5000, and 27017 are not in use
3. Rebuild without cache: `docker-compose build --no-cache`

### Connection Issues
- Ensure all services are running: `docker-compose ps`
- Check service logs: `docker-compose logs [service-name]`
- Verify network connectivity: `docker network ls`

### Data Persistence
MongoDB data is stored in a Docker volume. To backup:
```bash
docker-compose exec mongodb mongodump --out /data/backup
docker cp rfpai_mongodb:/data/backup ./mongodb-backup
```

## Development

To run in development mode with hot-reloading:

1. Comment out the frontend service in `docker-compose.yml`
2. Run MongoDB and backend: `docker-compose up -d mongodb backend`
3. Run frontend locally: `cd frontend && npm run serve`

## Production Considerations

1. Use environment-specific `.env` files
2. Enable HTTPS in Nginx configuration
3. Use strong passwords for MongoDB
4. Set up proper backup strategies
5. Configure resource limits in docker-compose.yml
6. Use a reverse proxy for the frontend in production
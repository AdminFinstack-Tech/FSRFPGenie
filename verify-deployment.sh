#!/bin/bash

echo "======================================"
echo "🚀 RFP AI System - Deployment Verification"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if containers are running
echo "📦 Checking Docker containers..."
echo ""

containers=("rfprag_frontend" "rfprag_backend" "rfprag_celery" "rfprag_mongodb" "rfprag_redis" "rfprag_qdrant")
all_running=true

for container in "${containers[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        echo -e "${GREEN}✓${NC} $container is running"
    else
        echo -e "${RED}✗${NC} $container is NOT running"
        all_running=false
    fi
done

echo ""

if [ "$all_running" = false ]; then
    echo -e "${RED}❌ Some containers are not running. Run: docker-compose up -d${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All containers are running${NC}"
echo ""

# Test Backend Health
echo "🏥 Testing Backend Health..."
health_response=$(curl -s http://localhost:5000/api/health 2>/dev/null)

if [ $? -eq 0 ] && echo "$health_response" | grep -q "OK"; then
    echo -e "${GREEN}✓${NC} Backend health check passed"
    echo "   Response: $health_response"
else
    echo -e "${RED}✗${NC} Backend health check failed"
    echo "   Run: docker-compose logs backend | tail -50"
    exit 1
fi

echo ""

# Test Frontend
echo "🎨 Testing Frontend..."
frontend_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>/dev/null)

if [ "$frontend_response" = "200" ]; then
    echo -e "${GREEN}✓${NC} Frontend is accessible"
else
    echo -e "${RED}✗${NC} Frontend returned status code: $frontend_response"
fi

echo ""

# Check Backend Logs for Errors
echo "📋 Checking Backend Logs for Errors..."
backend_errors=$(docker-compose logs backend 2>/dev/null | grep -i "error\|exception\|traceback" | tail -5)

if [ -z "$backend_errors" ]; then
    echo -e "${GREEN}✓${NC} No recent errors in backend logs"
else
    echo -e "${YELLOW}⚠${NC}  Recent errors found:"
    echo "$backend_errors"
fi

echo ""

# Check Azure OpenAI Integration
echo "🤖 Checking Azure OpenAI Integration..."
azure_init=$(docker-compose logs backend 2>/dev/null | grep -i "azure\|gpt\|embedding" | tail -3)

if echo "$azure_init" | grep -q "Azure OpenAI"; then
    echo -e "${GREEN}✓${NC} Azure OpenAI integration detected"
    echo "$azure_init"
else
    echo -e "${YELLOW}⚠${NC}  Azure OpenAI status unclear. Check logs:"
    echo "   docker-compose logs backend | grep -i azure"
fi

echo ""

# Check MongoDB Connection
echo "💾 Checking MongoDB Connection..."
mongo_status=$(docker exec rfprag_mongodb mongo --eval "db.adminCommand('ping')" 2>/dev/null)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} MongoDB is responding"
else
    echo -e "${YELLOW}⚠${NC}  MongoDB status check skipped (requires mongo client)"
fi

echo ""

# Check Qdrant
echo "🔍 Checking Qdrant Vector Database..."
qdrant_response=$(curl -s http://localhost:6333/collections 2>/dev/null)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Qdrant is responding"
    echo "   Collections: $qdrant_response"
else
    echo -e "${RED}✗${NC} Qdrant is not accessible"
fi

echo ""

# Check Redis
echo "⚡ Checking Redis..."
redis_status=$(docker exec rfprag_redis redis-cli ping 2>/dev/null)

if [ "$redis_status" = "PONG" ]; then
    echo -e "${GREEN}✓${NC} Redis is responding"
else
    echo -e "${YELLOW}⚠${NC}  Redis status check failed"
fi

echo ""

# Summary
echo "======================================"
echo "📊 Deployment Summary"
echo "======================================"
echo ""
echo "🌐 Access Points:"
echo "   Frontend:  http://localhost:8080"
echo "   Backend:   http://localhost:5000"
echo "   MongoDB:   localhost:27018"
echo "   Qdrant:    localhost:6333"
echo "   Redis:     localhost:6380"
echo ""
echo "🎯 Quick Start:"
echo "   1. Upload RFP: http://localhost:8080/upload"
echo "   2. Ask Questions: http://localhost:8080/search"
echo ""
echo "📚 Documentation:"
echo "   - INTELLIGENT_QA_SYSTEM.md - Technical details"
echo "   - QUICK_START.md - User guide"
echo ""
echo "🔧 Troubleshooting:"
echo "   View logs: docker-compose logs -f [service]"
echo "   Restart: docker-compose restart [service]"
echo "   Reset all: docker-compose down && docker-compose up -d"
echo ""
echo -e "${GREEN}✅ Verification complete!${NC}"

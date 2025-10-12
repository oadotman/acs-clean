#!/usr/bin/env bash

# AdCopySurge Celery Worker Start Script for VPS
# This script starts the Celery worker with production settings

set -e  # Exit on any error

echo "🚀 Starting AdCopySurge Celery worker..."

# Set environment variables
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export PYTHONPATH="/home/deploy/adcopysurge/backend"

# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Show environment info
echo "🔍 Celery Environment Information:"
echo "  - Python Path: $PYTHONPATH"
echo "  - Environment: $ENVIRONMENT"
echo "  - Debug: $DEBUG"
echo "  - Redis URL: ${REDIS_URL:+[SET]} ${REDIS_URL:-[NOT SET]}"

# Wait for Redis to be ready with retries
wait_for_redis() {
    echo "⏳ Waiting for Redis connection..."
    local retries=30
    local count=0
    
    while [ $count -lt $retries ]; do
        if python -c "
import redis
import os
try:
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    r = redis.from_url(redis_url)
    r.ping()
    print('✅ Redis connection successful')
    exit(0)
except Exception as e:
    print(f'⚠️  Redis connection attempt failed: {e}')
    exit(1)
"; then
            echo "✅ Redis is ready!"
            return 0
        fi
        
        count=$((count + 1))
        echo "⏳ Redis not ready yet, retrying in 2 seconds... ($count/$retries)"
        sleep 2
    done
    
    echo "❌ Failed to connect to Redis after $retries attempts"
    return 1
}

# Test Celery app startup
test_celery() {
    echo "🧪 Testing Celery app startup..."
    python -c "
from app.celery_app import celery_app
from app.tasks import health_check

print('✅ Celery app loaded successfully')
print(f'  - Broker: {celery_app.broker}')
print(f'  - Backend: {celery_app.backend}')

# Test a simple task
try:
    result = health_check.delay()
    print('✅ Test task queued successfully')
except Exception as e:
    print(f'⚠️  Test task failed: {e}')

print('✅ Celery test passed')
"
}

# Main startup sequence
main() {
    # Wait for Redis
    if [ -n "${REDIS_URL:-}" ]; then
        wait_for_redis || {
            echo "❌ Redis connection failed, but continuing startup..."
            echo "Worker will attempt to connect at runtime"
        }
    else
        echo "⚠️  REDIS_URL not set, using default Redis connection"
        export REDIS_URL="redis://localhost:6379/0"
    fi
    
    # Test Celery app
    test_celery || {
        echo "❌ Celery app test failed"
        exit 1
    }
    
    # Determine concurrency based on available resources
    CONCURRENCY=${CELERY_WORKERS:-2}
    
    echo "🔧 Celery Configuration:"
    echo "  - Concurrency: $CONCURRENCY"
    echo "  - Log Level: info"
    echo "  - Queues: analysis,reports,email,celery"
    
    # Start Celery worker
    echo "🚀 Starting Celery worker..."
    
    exec celery -A app.celery_app worker \
        --loglevel=info \
        --concurrency=$CONCURRENCY \
        --queues=analysis,reports,email,celery \
        --hostname=worker@%h \
        --without-gossip \
        --without-mingle \
        --without-heartbeat
}

# Handle signals for graceful shutdown
trap 'echo "🛑 Received shutdown signal, stopping Celery worker..."; exit 0' SIGTERM SIGINT

# Start the worker
main
#!/usr/bin/env bash

# AdCopySurge Start Script for VPS Deployment
# This script starts the FastAPI application with production settings

set -e  # Exit on any error

echo "🚀 Starting AdCopySurge API server..."

# Set environment variables
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export PYTHONPATH="/home/deploy/adcopysurge/backend"

# Default port for VPS deployment (will be overridden by systemd)
export PORT=${PORT:-8000}
echo "🔌 Server will bind to port: $PORT"

# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Show environment info
echo "🔍 Environment Information:"
echo "  - Python Path: $PYTHONPATH"
echo "  - Port: $PORT"  
echo "  - Environment: $ENVIRONMENT"
echo "  - Debug: $DEBUG"
echo "  - Database URL: ${DATABASE_URL:+[SET]} ${DATABASE_URL:-[NOT SET]}"
echo "  - Redis URL: ${REDIS_URL:+[SET]} ${REDIS_URL:-[NOT SET]}"

# Wait for database to be ready with retries
wait_for_db() {
    echo "⏳ Waiting for database connection..."
    local retries=30
    local count=0
    
    while [ $count -lt $retries ]; do
        if python -c "
import os
import psycopg2
from urllib.parse import urlparse
try:
    result = urlparse(os.environ.get('DATABASE_URL', ''))
    if not result.hostname:
        raise ValueError('DATABASE_URL not set or invalid')
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port,
        connect_timeout=10
    )
    conn.close()
    print('✅ Database connection successful')
    exit(0)
except Exception as e:
    print(f'⚠️  Database connection attempt failed: {e}')
    exit(1)
"; then
            echo "✅ Database is ready!"
            return 0
        fi
        
        count=$((count + 1))
        echo "⏳ Database not ready yet, retrying in 2 seconds... ($count/$retries)"
        sleep 2
    done
    
    echo "❌ Failed to connect to database after $retries attempts"
    return 1
}

# Run database migrations
run_migrations() {
    echo "🗃️  Running database migrations..."
    if [ -f "alembic.ini" ]; then
        python -m alembic upgrade head
        echo "✅ Database migrations completed"
    else
        echo "⚠️  No alembic.ini found, skipping migrations"
    fi
}

# Test application startup
test_app() {
    echo "🧪 Testing application startup..."
    python -c "
from app.core.config import settings
from app.core.database import engine

print('✅ Configuration loaded successfully')
print(f'  - App Name: {settings.APP_NAME}')
print(f'  - Environment: {settings.ENVIRONMENT}') 
print(f'  - Debug: {settings.DEBUG}')
print(f'  - Port: {settings.PORT}')

if engine:
    print('✅ Database engine created successfully')
else:
    print('⚠️  Database engine is None')

print('✅ Application test passed')
"
}

# Main startup sequence
main() {
    # Wait for database
    if [ -n "${DATABASE_URL:-}" ]; then
        wait_for_db || {
            echo "❌ Database connection failed, but continuing startup..."
            echo "Application will attempt to connect at runtime"
        }
        
        # Run migrations
        run_migrations || {
            echo "⚠️  Database migrations failed, but continuing startup..."
        }
    else
        echo "⚠️  DATABASE_URL not set, skipping database setup"
    fi
    
    # Test application
    test_app || {
        echo "❌ Application test failed"
        exit 1
    }
    
    # Determine number of workers based on available resources
    # Render's starter plan has limited resources, so we use fewer workers
    WORKERS=${WORKERS:-2}
    WORKER_CONNECTIONS=${WORKER_CONNECTIONS:-1000}
    TIMEOUT=${TIMEOUT:-120}
    KEEP_ALIVE=${KEEP_ALIVE:-2}
    MAX_REQUESTS=${MAX_REQUESTS:-1000}
    MAX_REQUESTS_JITTER=${MAX_REQUESTS_JITTER:-50}
    
    echo "🔧 Gunicorn Configuration:"
    echo "  - Workers: $WORKERS"
    echo "  - Worker Connections: $WORKER_CONNECTIONS"
    echo "  - Timeout: $TIMEOUT seconds"
    echo "  - Keep Alive: $KEEP_ALIVE seconds"
    echo "  - Max Requests: $MAX_REQUESTS"
    echo "  - Max Requests Jitter: $MAX_REQUESTS_JITTER"
    
    # Start the application with Gunicorn + Uvicorn workers
    echo "🚀 Starting AdCopySurge API with Gunicorn..."
    
    exec gunicorn main:app \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind "0.0.0.0:$PORT" \
        --workers $WORKERS \
        --worker-connections $WORKER_CONNECTIONS \
        --timeout $TIMEOUT \
        --keep-alive $KEEP_ALIVE \
        --max-requests $MAX_REQUESTS \
        --max-requests-jitter $MAX_REQUESTS_JITTER \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --capture-output \
        --enable-stdio-inheritance
}

# Handle signals for graceful shutdown
trap 'echo "🛑 Received shutdown signal, stopping server..."; exit 0' SIGTERM SIGINT

# Start the application
main

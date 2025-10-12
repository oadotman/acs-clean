#!/usr/bin/env bash

# AdCopySurge Build Script for Render
# This script prepares the application for deployment

set -e  # Exit on any error
set -u  # Exit on undefined variables

echo "🚀 Starting AdCopySurge build process..."

# Set environment variables
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export PYTHONPATH="/app/backend:/app"

# Install or upgrade Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements-production.txt -c constraints-py312.txt --no-cache-dir --prefer-binary

# Download required NLTK data for text analysis
echo "📚 Downloading NLTK data..."
python -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    print('✅ NLTK data downloaded successfully')
except Exception as e:
    print(f'⚠️  NLTK data download failed: {e}')
    print('Continuing without NLTK data...')
"

# Test imports to catch any dependency issues early
echo "🔍 Testing critical imports..."
python -c "
import sys
print(f'Python version: {sys.version}')

# Test core dependencies
try:
    import fastapi
    print('✅ FastAPI imported successfully')
except ImportError as e:
    print(f'❌ FastAPI import failed: {e}')
    sys.exit(1)

try:
    import sqlalchemy
    print('✅ SQLAlchemy imported successfully')
except ImportError as e:
    print(f'❌ SQLAlchemy import failed: {e}')
    sys.exit(1)

try:
    import psycopg2
    print('✅ psycopg2 imported successfully')
except ImportError as e:
    print(f'❌ psycopg2 import failed: {e}')
    sys.exit(1)

try:
    import uvicorn
    print('✅ Uvicorn imported successfully')
except ImportError as e:
    print(f'❌ Uvicorn import failed: {e}')
    sys.exit(1)

try:
    import gunicorn
    print('✅ Gunicorn imported successfully')
except ImportError as e:
    print(f'❌ Gunicorn import failed: {e}')
    sys.exit(1)

# Test AI dependencies (optional)
try:
    import openai
    print('✅ OpenAI imported successfully')
except ImportError:
    print('⚠️  OpenAI not available (optional dependency)')

try:
    import transformers
    print('✅ Transformers imported successfully')  
except ImportError:
    print('⚠️  Transformers not available (optional dependency)')
"

# Test database connection if DATABASE_URL is available
if [ -n "${DATABASE_URL:-}" ]; then
    echo "🔌 Testing database connection..."
    python -c "
import os
import psycopg2
from urllib.parse import urlparse

try:
    result = urlparse(os.environ['DATABASE_URL'])
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'⚠️  Database connection failed: {e}')
    print('This is expected during build phase - connection will be retried at startup')
"
else
    echo "⚠️  DATABASE_URL not set - skipping database connection test"
fi

# Run database migrations if Alembic is configured
if [ -f "alembic.ini" ] && [ -n "${DATABASE_URL:-}" ]; then
    echo "🗃️  Running database migrations..."
    python -m alembic upgrade head || {
        echo "⚠️  Database migrations failed - this may be expected during build"
        echo "Migrations will be retried during startup"
    }
else
    echo "⚠️  Skipping database migrations (alembic.ini not found or DATABASE_URL not set)"
fi

# Create required directories
echo "📁 Creating application directories..."
mkdir -p logs
mkdir -p temp
mkdir -p uploads

# Set proper permissions
chmod 755 logs temp uploads 2>/dev/null || echo "⚠️  Could not set directory permissions"

echo "✅ Build completed successfully!"
echo "🔗 Ready for startup with start.sh"

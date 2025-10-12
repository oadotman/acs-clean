#!/bin/sh

# AdCopySurge Frontend Startup Script for Fly.io
# Starts nginx with proper configuration

set -e

echo "🚀 Starting AdCopySurge Frontend..."

# Show environment info
echo "🔍 Environment Information:"
echo "  - Node Environment: $NODE_ENV"
echo "  - API Base URL: $REACT_APP_API_BASE_URL"

# Start nginx in the foreground
echo "🌐 Starting nginx server on port 3000..."
nginx -g "daemon off;"

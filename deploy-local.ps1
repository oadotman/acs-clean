# AdCopySurge Local Production Deployment Script
# This script builds and tests the production version locally

Write-Host "🚀 AdCopySurge Local Production Deployment" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

# Navigate to frontend directory
Set-Location "frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Clean previous build
if (Test-Path "build") {
    Write-Host "🧹 Cleaning previous build..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "build"
}

# Build for production
Write-Host "🔨 Building production version..." -ForegroundColor Yellow
Write-Host "   - Blog functionality: DISABLED" -ForegroundColor Red
Write-Host "   - Source maps: DISABLED" -ForegroundColor Red
Write-Host "   - Environment: PRODUCTION" -ForegroundColor Red

$env:NODE_ENV = "production"
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build successful!" -ForegroundColor Green

# Start local server to test
Write-Host "🌐 Starting local production server..." -ForegroundColor Yellow
Write-Host "   - URL: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   - Press Ctrl+C to stop" -ForegroundColor Cyan

# Install serve if not available
try {
    & npx serve --version *>$null
} catch {
    Write-Host "📦 Installing serve..." -ForegroundColor Yellow
    npm install -g serve
}

# Serve the production build
npx serve -s build -p 3000
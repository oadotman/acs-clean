# AdCopySurge Development Setup Script
# Run this script to set up your development environment

Write-Host "🚀 Setting up AdCopySurge development environment..." -ForegroundColor Cyan

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check PostgreSQL
try {
    $pgVersion = psql --version
    Write-Host "✅ PostgreSQL found: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️ PostgreSQL not found. You'll need to install PostgreSQL 15+" -ForegroundColor Orange
}

# Setup backend
Write-Host "📦 Setting up backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Gray
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Gray
& "venv\Scripts\Activate.ps1"

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Gray
pip install -r requirements.txt

# Return to root
Set-Location ..

# Setup frontend
Write-Host "🎨 Setting up frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Gray
npm install

# Return to root
Set-Location ..

# Create .env from example if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️ Please edit .env file with your configuration" -ForegroundColor Orange
}

# Final instructions
Write-Host "`n🎉 Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your API keys and database configuration"
Write-Host "2. Set up PostgreSQL database: createdb adcopysurge"
Write-Host "3. Start backend: cd backend && uvicorn main:app --reload"
Write-Host "4. Start frontend: cd frontend && npm start"
Write-Host "5. Visit http://localhost:3000 to see the app"
Write-Host "`nOr use Docker: docker-compose up -d" -ForegroundColor Yellow

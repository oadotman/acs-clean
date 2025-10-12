# AdCopySurge Production Secrets Generator
# This script generates secure production keys and updates the environment configuration
# Run this script on your production server or CI/CD environment

Write-Host "🚀 AdCopySurge Production Secrets Generator" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Function to generate secure random strings
function Generate-SecureString {
    param([int]$Length = 64)
    $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    $random = 1..$Length | ForEach-Object { Get-Random -Maximum $chars.length }
    return -join ($random | ForEach-Object { $chars[$_] })
}

# Function to generate hex strings
function Generate-HexString {
    param([int]$Length = 32)
    $bytes = New-Object byte[] ($Length)
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
    return [System.BitConverter]::ToString($bytes) -replace '-'
}

Write-Host "`n📋 Generating production secrets..." -ForegroundColor Yellow

# Generate all required secrets
$secrets = @{
    'SECRET_KEY' = Generate-HexString 32
    'SUPABASE_JWT_SECRET' = Generate-HexString 32
    'PADDLE_WEBHOOK_SECRET' = Generate-SecureString 64
    'DATABASE_PASSWORD' = Generate-SecureString 24
    'REDIS_PASSWORD' = Generate-SecureString 24
    'SMTP_PASSWORD_PLACEHOLDER' = "your-smtp-app-password"
}

Write-Host "✅ Generated secure secrets" -ForegroundColor Green

# Create the production .env file
$envContent = Get-Content ".env.local" -Raw

# Replace placeholders with generated values
foreach ($key in $secrets.Keys) {
    $placeholder = "{{GENERATE_256_BIT_SECRET_KEY}}"
    if ($key -eq 'SECRET_KEY') {
        $envContent = $envContent -replace [regex]::Escape($placeholder), $secrets[$key]
    }
}

# Create .env.production file
$productionEnv = @"
# ===========================================
# AdCopySurge Production Environment Configuration
# Generated on: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')
# ===========================================
# WARNING: This file contains sensitive information
# Never commit this file to version control
# ===========================================

# Environment Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=warning

# Application Settings
APP_NAME=AdCopySurge
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8000

# Security Configuration (GENERATED)
SECRET_KEY=$($secrets.SECRET_KEY)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database Configuration
# TODO: Replace with your production database URL
DATABASE_URL=postgresql://adcopysurge:$($secrets.DATABASE_PASSWORD)@localhost:5432/adcopysurge_prod

# Supabase Configuration
# TODO: Replace with your production Supabase project values
REACT_APP_SUPABASE_URL=https://your-production-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-production-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-production-service-role-key
SUPABASE_JWT_SECRET=$($secrets.SUPABASE_JWT_SECRET)

# CORS Configuration
CORS_ORIGINS=https://adcopysurge.com,https://www.adcopysurge.com,https://app.adcopysurge.com
ALLOWED_HOSTS=api.adcopysurge.com,adcopysurge.com

# AI Services Configuration
# TODO: Replace with your production OpenAI API key
OPENAI_API_KEY=your-production-openai-api-key
OPENAI_MAX_TOKENS=2000
OPENAI_RATE_LIMIT=100

# Optional AI Services
HUGGINGFACE_API_KEY=your-huggingface-api-key

# Redis Configuration  
REDIS_URL=redis://:$($secrets.REDIS_PASSWORD)@localhost:6379/0

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-production-email@gmail.com
SMTP_PASSWORD=$($secrets.SMTP_PASSWORD_PLACEHOLDER)
MAIL_FROM=noreply@adcopysurge.com
MAIL_FROM_NAME=AdCopySurge

# Paddle Billing Configuration
# TODO: Replace with your Paddle production credentials
PADDLE_VENDOR_ID=your-paddle-vendor-id
PADDLE_API_KEY=your-paddle-api-key
PADDLE_WEBHOOK_SECRET=$($secrets.PADDLE_WEBHOOK_SECRET)
PADDLE_ENVIRONMENT=production
PADDLE_API_URL=https://vendors.paddle.com/api

# Paddle Product IDs
# TODO: Configure these in your Paddle Dashboard
PADDLE_BASIC_MONTHLY_ID=basic-monthly-product-id
PADDLE_PRO_MONTHLY_ID=pro-monthly-product-id
PADDLE_BASIC_YEARLY_ID=basic-yearly-product-id
PADDLE_PRO_YEARLY_ID=pro-yearly-product-id

# Monitoring & Error Tracking
# TODO: Replace with your production Sentry DSN
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Performance & Scaling
WORKERS=4
KEEP_ALIVE=2
MAX_CONNECTIONS=100

# Security Headers
HSTS_MAX_AGE=31536000
CONTENT_SECURITY_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline' cdn.paddle.com; style-src 'self' 'unsafe-inline'

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_COMPETITOR_ANALYSIS=false
ENABLE_PDF_REPORTS=true
ENABLE_RATE_LIMITING=true

# Business Configuration
BASIC_PLAN_PRICE=49
PRO_PLAN_PRICE=99
FREE_TIER_LIMIT=5
BASIC_TIER_LIMIT=100
PRO_TIER_LIMIT=500
"@

# Write the production environment file
$productionEnv | Out-File -FilePath ".env.production" -Encoding UTF8

Write-Host "`n✅ Created .env.production with secure secrets" -ForegroundColor Green

# Create a secrets summary for secure storage
$secretsSummary = @"
# AdCopySurge Production Secrets Summary
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')
# Store these securely in your password manager or secrets vault

SECRET_KEY=$($secrets.SECRET_KEY)
SUPABASE_JWT_SECRET=$($secrets.SUPABASE_JWT_SECRET)  
PADDLE_WEBHOOK_SECRET=$($secrets.PADDLE_WEBHOOK_SECRET)
DATABASE_PASSWORD=$($secrets.DATABASE_PASSWORD)
REDIS_PASSWORD=$($secrets.REDIS_PASSWORD)

# Note: You still need to configure:
# - REACT_APP_SUPABASE_URL
# - REACT_APP_SUPABASE_ANON_KEY
# - SUPABASE_SERVICE_ROLE_KEY
# - OPENAI_API_KEY
# - PADDLE_VENDOR_ID
# - PADDLE_API_KEY
# - Paddle Product IDs
# - SENTRY_DSN
# - SMTP credentials
"@

$secretsSummary | Out-File -FilePath "secrets-summary.txt" -Encoding UTF8

Write-Host "📄 Created secrets-summary.txt - Store this securely!" -ForegroundColor Yellow

# Create frontend environment file
$frontendEnv = @"
# AdCopySurge Frontend Production Configuration

# API Configuration
REACT_APP_API_URL=https://api.adcopysurge.com
REACT_APP_APP_NAME=AdCopySurge

# Supabase Configuration (REQUIRED)
# TODO: Replace with your production Supabase project values
REACT_APP_SUPABASE_URL=https://your-production-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-production-anon-key

# Paddle Configuration (REQUIRED)
# TODO: Replace with your Paddle production credentials
REACT_APP_PADDLE_VENDOR_ID=your-paddle-vendor-id
REACT_APP_PADDLE_ENVIRONMENT=production

# Environment
NODE_ENV=production
GENERATE_SOURCEMAP=false
CI=false

# Feature Flags
REACT_APP_ENABLE_DEBUG=false
REACT_APP_ENABLE_MOCK_DATA=false
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_COMPETITOR_ANALYSIS=false
"@

$frontendEnv | Out-File -FilePath "frontend/.env.production" -Encoding UTF8

Write-Host "✅ Created frontend/.env.production" -ForegroundColor Green

Write-Host "`n🔒 SECURITY CHECKLIST:" -ForegroundColor Red
Write-Host "  1. ✅ Generated secure SECRET_KEY (256-bit)" -ForegroundColor Green
Write-Host "  2. ✅ Generated Supabase JWT secret" -ForegroundColor Green  
Write-Host "  3. ✅ Generated Paddle webhook secret" -ForegroundColor Green
Write-Host "  4. ✅ Generated database & Redis passwords" -ForegroundColor Green
Write-Host "  5. ⚠️  TODO: Configure Supabase production project" -ForegroundColor Yellow
Write-Host "  6. ⚠️  TODO: Configure Paddle production credentials" -ForegroundColor Yellow
Write-Host "  7. ⚠️  TODO: Configure OpenAI API key" -ForegroundColor Yellow
Write-Host "  8. ⚠️  TODO: Configure Sentry monitoring" -ForegroundColor Yellow
Write-Host "  9. ⚠️  TODO: Configure SMTP email credentials" -ForegroundColor Yellow

Write-Host "`n📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "  1. Review and complete .env.production configuration" -ForegroundColor White
Write-Host "  2. Securely store secrets-summary.txt in password manager" -ForegroundColor White
Write-Host "  3. Delete secrets-summary.txt from server after storing" -ForegroundColor White
Write-Host "  4. Configure production Supabase project" -ForegroundColor White
Write-Host "  5. Set up Paddle billing integration" -ForegroundColor White
Write-Host "  6. Test environment configuration" -ForegroundColor White

Write-Host "`n🚀 Production secrets generation complete!" -ForegroundColor Green

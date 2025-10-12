# AdCopySurge Production Secrets Generator
# This script generates secure production keys

Write-Host "AdCopySurge Production Secrets Generator" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

function Generate-SecureString {
    param([int]$Length = 64)
    $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    $random = 1..$Length | ForEach-Object { Get-Random -Maximum $chars.length }
    return -join ($random | ForEach-Object { $chars[$_] })
}

function Generate-HexString {
    param([int]$Length = 32)
    $bytes = New-Object byte[] ($Length)
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
    return [System.BitConverter]::ToString($bytes) -replace '-'
}

Write-Host ""
Write-Host "Generating production secrets..." -ForegroundColor Yellow

# Generate all required secrets
$secretKey = Generate-HexString 32
$supabaseJwtSecret = Generate-HexString 32  
$paddleWebhookSecret = Generate-SecureString 64
$dbPassword = Generate-SecureString 24
$redisPassword = Generate-SecureString 24

Write-Host "Generated secure secrets successfully" -ForegroundColor Green

# Create secrets summary
$secretsContent = @"
# AdCopySurge Production Secrets Summary
# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')
# Store these securely in your password manager

SECRET_KEY=$secretKey
SUPABASE_JWT_SECRET=$supabaseJwtSecret
PADDLE_WEBHOOK_SECRET=$paddleWebhookSecret
DATABASE_PASSWORD=$dbPassword
REDIS_PASSWORD=$redisPassword

# IMPORTANT: You still need to configure:
# - REACT_APP_SUPABASE_URL (from your Supabase project)
# - REACT_APP_SUPABASE_ANON_KEY (from your Supabase project)
# - SUPABASE_SERVICE_ROLE_KEY (from your Supabase project)
# - OPENAI_API_KEY (from OpenAI dashboard)
# - PADDLE_VENDOR_ID (from Paddle dashboard)
# - PADDLE_API_KEY (from Paddle dashboard)
# - SENTRY_DSN (from Sentry project)
"@

$secretsContent | Out-File -FilePath "secrets-summary.txt" -Encoding UTF8

# Display next steps
Write-Host ""
Write-Host "SECURITY CHECKLIST:" -ForegroundColor Red
Write-Host "1. Generated secure SECRET_KEY (256-bit)" -ForegroundColor Green
Write-Host "2. Generated Supabase JWT secret" -ForegroundColor Green  
Write-Host "3. Generated Paddle webhook secret" -ForegroundColor Green
Write-Host "4. Generated database & Redis passwords" -ForegroundColor Green
Write-Host "5. TODO: Configure Supabase production project" -ForegroundColor Yellow
Write-Host "6. TODO: Configure Paddle production credentials" -ForegroundColor Yellow
Write-Host "7. TODO: Configure OpenAI API key" -ForegroundColor Yellow

Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Check secrets-summary.txt for generated values" -ForegroundColor White
Write-Host "2. Update .env.local with the SECRET_KEY value" -ForegroundColor White
Write-Host "3. Store secrets securely in password manager" -ForegroundColor White
Write-Host "4. Delete secrets-summary.txt after storing" -ForegroundColor White
Write-Host "5. Configure external services (Supabase, Paddle, OpenAI)" -ForegroundColor White

Write-Host ""
Write-Host "Production secrets generation complete!" -ForegroundColor Green

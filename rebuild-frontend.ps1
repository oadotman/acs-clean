# Frontend Rebuild Script
# This script rebuilds the frontend with cache clearing

Write-Host "🔨 Rebuilding Frontend with Cache Clearing" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to frontend directory
Set-Location -Path "frontend"

Write-Host "1️⃣  Cleaning build artifacts..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Path "build" -Recurse -Force
    Write-Host "   ✅ Removed build directory" -ForegroundColor Green
}

if (Test-Path "node_modules/.cache") {
    Remove-Item -Path "node_modules/.cache" -Recurse -Force
    Write-Host "   ✅ Removed node cache" -ForegroundColor Green
}

Write-Host ""
Write-Host "2️⃣  Installing dependencies..." -ForegroundColor Yellow
npm install
Write-Host "   ✅ Dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "3️⃣  Building frontend..." -ForegroundColor Yellow
$env:GENERATE_SOURCEMAP = "false"
npm run build
Write-Host "   ✅ Frontend built successfully" -ForegroundColor Green

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Frontend rebuild complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Clear your browser cache (Ctrl+Shift+Delete)" -ForegroundColor White
Write-Host "2. Hard refresh the page (Ctrl+Shift+R or Ctrl+F5)" -ForegroundColor White
Write-Host "3. Test team invitations and support tickets" -ForegroundColor White
Write-Host ""

# Return to root
Set-Location -Path ".."

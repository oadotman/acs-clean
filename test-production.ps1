# AdCopySurge Production Test Script
# This script tests the production build locally

Write-Host "🧪 AdCopySurge Production Test" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

Set-Location "frontend"

# Check if build exists
if (-not (Test-Path "build")) {
    Write-Host "❌ No build found. Run deploy-local.ps1 first!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build directory exists" -ForegroundColor Green

# Check build contents
$buildFiles = Get-ChildItem "build" -Recurse | Measure-Object
Write-Host "📁 Build contains $($buildFiles.Count) files" -ForegroundColor Cyan

# Check for index.html
if (Test-Path "build/index.html") {
    Write-Host "✅ index.html exists" -ForegroundColor Green
} else {
    Write-Host "❌ index.html missing!" -ForegroundColor Red
    exit 1
}

# Check for static assets
if (Test-Path "build/static") {
    Write-Host "✅ Static assets directory exists" -ForegroundColor Green
} else {
    Write-Host "❌ Static assets missing!" -ForegroundColor Red
    exit 1
}

# Check index.html content for blog references
$indexContent = Get-Content "build/index.html" -Raw
if ($indexContent -like "*blog*" -and $indexContent -like "*error*") {
    Write-Host "⚠️  Warning: index.html might still contain blog error references" -ForegroundColor Yellow
} else {
    Write-Host "✅ No obvious blog errors in index.html" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎯 TEST RESULTS:" -ForegroundColor Yellow
Write-Host "✅ Build exists and contains required files" -ForegroundColor Green
Write-Host "✅ Ready for deployment" -ForegroundColor Green
Write-Host ""
Write-Host "💡 To test locally:" -ForegroundColor Cyan
Write-Host "   npx serve -s build -p 3000" -ForegroundColor White
Write-Host "   Then open: http://localhost:3000" -ForegroundColor White

Set-Location ".."
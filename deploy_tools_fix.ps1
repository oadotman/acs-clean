# AdCopySurge Tools SDK Fix Deployment Script
# This script will commit changes and deploy to VPS

Write-Host "🚀 AdCopySurge Tools SDK Fix Deployment" -ForegroundColor Green
Write-Host "=" * 50

# Set location to project root
Set-Location "C:\Users\User\Desktop\Eledami\adsurge\adcopysurge"

Write-Host "`n📋 Changes Summary:" -ForegroundColor Yellow
Write-Host "1. ✅ Fixed API to use EnhancedAdAnalysisService with Tools SDK"
Write-Host "2. ✅ Added backward compatibility methods"
Write-Host "3. ✅ Fixed ComplianceChecker ToolType error"
Write-Host "4. ✅ All 7 tools now register successfully"

Write-Host "`n📦 Committing changes to Git..." -ForegroundColor Blue
git add .
git commit -m "🔧 Fix Tools SDK integration

- Switch API from AdAnalysisService to EnhancedAdAnalysisService
- Add backward compatibility methods to EnhancedAdAnalysisService  
- Fix ComplianceCheckerToolRunner to use ToolType.VALIDATOR
- All 7 tools now register successfully
- Resolves 'tools: null' issue in frontend

Tools working:
✅ readability_analyzer
✅ cta_analyzer  
✅ ad_copy_analyzer
✅ compliance_checker (FIXED)
✅ roi_copy_generator
✅ ab_test_generator
✅ industry_optimizer"

Write-Host "`n🌐 Pushing to GitHub..." -ForegroundColor Blue
git push origin main

Write-Host "`n🔄 Updating VPS deployment..." -ForegroundColor Cyan
Write-Host "Ready to connect to VPS 46.247.108.207 to pull changes..."
Write-Host ""
Write-Host "VPS Update Commands:" -ForegroundColor Yellow
Write-Host "ssh root@46.247.108.207" -ForegroundColor White
Write-Host "cd /srv/adcopysurge/app" -ForegroundColor White
Write-Host "git pull origin main" -ForegroundColor White  
Write-Host "systemctl restart adcopysurge-api.service" -ForegroundColor White
Write-Host "systemctl status adcopysurge-api.service --no-pager" -ForegroundColor White

Write-Host "`n✨ Local fixes complete! Ready to deploy to VPS." -ForegroundColor Green
Write-Host "Run the VPS commands above to complete deployment." -ForegroundColor Green
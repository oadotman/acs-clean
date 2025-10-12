# PowerShell script to restart the React frontend development server
# This ensures all the new changes and environment variables are loaded

Write-Host "🔄 Restarting AdCopySurge Frontend..." -ForegroundColor Cyan

# Navigate to frontend directory
Push-Location "frontend"

try {
    # Kill any existing React development servers
    Write-Host "⏹️ Stopping any existing development servers..." -ForegroundColor Yellow
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*react-scripts*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Wait a moment for cleanup
    Start-Sleep -Seconds 2
    
    # Clear npm cache (optional, helps with certain issues)
    Write-Host "🧹 Clearing npm cache..." -ForegroundColor Yellow
    npm cache clean --force 2>$null
    
    # Install any new dependencies
    Write-Host "📦 Installing dependencies..." -ForegroundColor Green
    npm install
    
    # Start the development server
    Write-Host "🚀 Starting development server with updated configuration..." -ForegroundColor Green
    Write-Host "   ✅ Blog functionality: DISABLED (REACT_APP_BLOG_ENABLED=false)" -ForegroundColor Green
    Write-Host "   ✅ Navigation: Updated with ACCOUNT section and Agency submenu" -ForegroundColor Green
    Write-Host "   ✅ Agency routes: Available at /agency/*" -ForegroundColor Green
    Write-Host "   ✅ LegacyAppLayout: Removed from protected routes" -ForegroundColor Green
    Write-Host "   ✅ Toast errors: Fixed (replaced toast.info)" -ForegroundColor Green
    Write-Host "   ✅ Bulk analysis: Removed (focus on single analysis)" -ForegroundColor Green
    
    # Start the server
    npm start
}
catch {
    Write-Host "❌ Error occurred: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    # Return to original directory
    Pop-Location
}

Write-Host "✅ Frontend restart complete!" -ForegroundColor Green
#!/bin/bash

# AdCopy Surge - Deployment and Testing Script
# This script helps with building, testing, and deploying the application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AdCopy Surge - Deployment & Testing Script${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the frontend directory."
    exit 1
fi

# Parse command line arguments
COMMAND=${1:-"help"}

case $COMMAND in
    "build")
        echo -e "${BLUE}📦 Building application...${NC}"
        
        # Install dependencies if node_modules doesn't exist
        if [ ! -d "node_modules" ]; then
            print_warning "node_modules not found. Installing dependencies..."
            npm install
        fi
        
        # Build the application
        npm run build
        
        if [ $? -eq 0 ]; then
            print_status "Build completed successfully!"
            echo -e "${BLUE}📊 Build statistics:${NC}"
            if [ -d "build" ]; then
                du -sh build/
                find build -name "*.js" -o -name "*.css" | wc -l | xargs echo "Static files:"
            fi
        else
            print_error "Build failed!"
            exit 1
        fi
        ;;
        
    "test")
        echo -e "${BLUE}🧪 Running tests...${NC}"
        
        # Run lint check
        echo "Running ESLint..."
        npm run lint --silent || print_warning "Linting issues found (non-blocking)"
        
        # Run tests if available
        if grep -q "\"test\":" package.json; then
            echo "Running unit tests..."
            npm test -- --watchAll=false --coverage || print_warning "Some tests failed (non-blocking)"
        else
            print_warning "No test script found in package.json"
        fi
        
        # Check for common issues
        echo -e "${BLUE}🔍 Checking for common issues...${NC}"
        
        # Check for console.log statements (except in debug files)
        if grep -r "console.log" src/ --exclude-dir=debug --exclude="*Debug*" > /dev/null 2>&1; then
            print_warning "console.log statements found in production code"
        fi
        
        # Check for TODO comments
        if grep -r "TODO\|FIXME" src/ > /dev/null 2>&1; then
            print_warning "TODO/FIXME comments found in code"
        fi
        
        print_status "Test phase completed!"
        ;;
        
    "analyze")
        echo -e "${BLUE}📈 Analyzing bundle size...${NC}"
        
        if [ ! -d "build" ]; then
            print_error "Build directory not found. Run 'build' command first."
            exit 1
        fi
        
        # Analyze bundle
        if command -v npx &> /dev/null; then
            echo "Installing and running bundle analyzer..."
            npx webpack-bundle-analyzer build/static/js/*.js --no-open || print_warning "Bundle analyzer failed"
        else
            print_warning "npx not available. Showing basic size info instead:"
            find build -name "*.js" -exec ls -lh {} \;
        fi
        ;;
        
    "deploy-prep")
        echo -e "${BLUE}🎯 Preparing for deployment...${NC}"
        
        # Build first
        echo "Step 1: Building application..."
        npm run build
        
        # Copy nginx configuration
        if [ -f "nginx-production.conf" ]; then
            print_status "Production nginx config found"
            echo "To deploy:"
            echo "1. Copy nginx-production.conf to your server"
            echo "2. Update server_name and SSL paths"
            echo "3. Copy build/ contents to /var/www/adcopysurge"
            echo "4. Restart nginx"
        fi
        
        # Create deployment archive
        if command -v tar &> /dev/null; then
            echo "Creating deployment archive..."
            tar -czf adcopysurge-deployment-$(date +%Y%m%d-%H%M%S).tar.gz build/ nginx-production.conf
            print_status "Deployment archive created"
        fi
        
        # SSL check reminder
        print_warning "Remember to:"
        echo "• Ensure SSL certificates are valid and not expired"
        echo "• Update nginx config with correct domain names"
        echo "• Test HTTPS redirects after deployment"
        echo "• Clear browser cache after deployment"
        ;;
        
    "ssl-check")
        echo -e "${BLUE}🔒 SSL Certificate Check${NC}"
        
        DOMAIN=${2:-"adcopysurge.com"}
        
        if command -v openssl &> /dev/null; then
            echo "Checking SSL certificate for $DOMAIN..."
            echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates
        else
            print_warning "openssl not available. Cannot check SSL certificates."
            echo "Manual check: Visit https://$DOMAIN in a browser"
        fi
        ;;
        
    "debug")
        echo -e "${BLUE}🔧 Debug Information${NC}"
        
        echo "Node version: $(node --version 2>/dev/null || echo 'Not found')"
        echo "NPM version: $(npm --version 2>/dev/null || echo 'Not found')"
        
        if [ -f "package.json" ]; then
            echo "Project dependencies:"
            grep -A 5 '"dependencies"' package.json || echo "No dependencies section found"
        fi
        
        if [ -d "build" ]; then
            echo "Build directory exists: Yes"
            echo "Build size: $(du -sh build/ | cut -f1)"
        else
            echo "Build directory exists: No"
        fi
        
        echo ""
        echo "For Supabase debugging, open browser console and run:"
        echo "• debugSupabase() - Full diagnostic"
        echo "• supabaseAuth() - Auth check"
        echo "• supabaseRLS() - RLS policies check"
        echo "• fixSupabaseAuth() - Attempt auth fix"
        ;;
        
    "help"|*)
        echo -e "${BLUE}AdCopy Surge Deployment Script${NC}"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  build        Build the application for production"
        echo "  test         Run linting and tests"
        echo "  analyze      Analyze bundle size"
        echo "  deploy-prep  Prepare deployment package"
        echo "  ssl-check    Check SSL certificate status [domain]"
        echo "  debug        Show debug information"
        echo "  help         Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 build"
        echo "  $0 test"
        echo "  $0 ssl-check adcopysurge.com"
        echo "  $0 deploy-prep"
        ;;
esac

echo ""
echo -e "${GREEN}✨ Script completed!${NC}"
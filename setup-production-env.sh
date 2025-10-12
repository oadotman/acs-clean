#!/bin/bash

# AdCopySurge Production Environment Setup Script
# This script helps you set up secure environment variables for deployment

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔒 AdCopySurge Production Environment Setup${NC}"
echo "================================================"
echo ""

# Function to generate secure secret
generate_secret() {
    python3 -c "import secrets; print(secrets.token_urlsafe(64))" 2>/dev/null || \
    openssl rand -base64 48 2>/dev/null || \
    head -c 48 /dev/urandom | base64 | tr -d '\n'
}

# Function to prompt for variable
prompt_for_var() {
    local var_name="$1"
    local description="$2"
    local current_value="${!var_name:-}"
    local is_secret="${3:-false}"
    
    echo -e "${YELLOW}$var_name${NC}: $description"
    if [[ -n "$current_value" ]]; then
        if [[ "$is_secret" == "true" ]]; then
            echo "Current value: [***HIDDEN***]"
        else
            echo "Current value: $current_value"
        fi
        read -p "Keep current value? (y/n): " keep_current
        if [[ "$keep_current" =~ ^[Yy]$ ]]; then
            return 0
        fi
    fi
    
    if [[ "$is_secret" == "true" ]]; then
        read -s -p "Enter $var_name: " new_value
        echo ""
    else
        read -p "Enter $var_name: " new_value
    fi
    
    if [[ -n "$new_value" ]]; then
        export "$var_name"="$new_value"
        echo -e "${GREEN}✅ $var_name set${NC}"
    else
        echo -e "${RED}❌ $var_name cannot be empty${NC}"
        exit 1
    fi
    echo ""
}

echo "Setting up production environment variables..."
echo "Press Ctrl+C at any time to cancel."
echo ""

# Generate SECRET_KEY if not set
if [[ -z "${SECRET_KEY:-}" ]]; then
    echo -e "${BLUE}Generating secure SECRET_KEY...${NC}"
    export SECRET_KEY=$(generate_secret)
    echo -e "${GREEN}✅ Generated secure SECRET_KEY${NC}"
    echo ""
fi

# Required variables
prompt_for_var "SECRET_KEY" "FastAPI secret key (minimum 32 characters)" "true"
prompt_for_var "DATABASE_URL" "PostgreSQL database URL (e.g., postgresql://user:pass@host:5432/dbname)"
prompt_for_var "SUPABASE_URL" "Supabase project URL (e.g., https://abc123.supabase.co)"
prompt_for_var "SUPABASE_ANON_KEY" "Supabase anonymous/public key" "true"
prompt_for_var "SUPABASE_SERVICE_ROLE_KEY" "Supabase service role key (admin access)" "true"
prompt_for_var "SUPABASE_JWT_SECRET" "Supabase JWT secret for token verification" "true"
prompt_for_var "OPENAI_API_KEY" "OpenAI API key (sk-...)" "true"

# Optional variables with defaults
export CORS_ORIGINS="${CORS_ORIGINS:-https://v44954.datalix.de,https://app.adcopysurge.com}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export REACT_APP_API_URL="${REACT_APP_API_URL:-http://46.247.108.207:8000/api}"
export REACT_APP_SITE_URL="${REACT_APP_SITE_URL:-https://v44954.datalix.de}"

echo -e "${BLUE}Optional Settings (using defaults if not changed):${NC}"
prompt_for_var "CORS_ORIGINS" "Allowed CORS origins (comma-separated)"
prompt_for_var "REDIS_URL" "Redis connection URL"
prompt_for_var "REACT_APP_API_URL" "Frontend API URL"
prompt_for_var "REACT_APP_SITE_URL" "Frontend site URL"

echo ""
echo -e "${GREEN}✅ Environment variables configured!${NC}"
echo ""
echo -e "${BLUE}Summary of configured variables:${NC}"
echo "- SECRET_KEY: [***HIDDEN***] (${#SECRET_KEY} characters)"
echo "- DATABASE_URL: ${DATABASE_URL}"
echo "- SUPABASE_URL: ${SUPABASE_URL}"
echo "- SUPABASE_ANON_KEY: [***HIDDEN***]"
echo "- SUPABASE_SERVICE_ROLE_KEY: [***HIDDEN***]"
echo "- SUPABASE_JWT_SECRET: [***HIDDEN***]"
echo "- OPENAI_API_KEY: [***HIDDEN***]"
echo "- CORS_ORIGINS: ${CORS_ORIGINS}"
echo "- REDIS_URL: ${REDIS_URL}"
echo "- REACT_APP_API_URL: ${REACT_APP_API_URL}"
echo "- REACT_APP_SITE_URL: ${REACT_APP_SITE_URL}"
echo ""

# Validate required variables
echo -e "${BLUE}Validating configuration...${NC}"

if [[ ${#SECRET_KEY} -lt 32 ]]; then
    echo -e "${RED}❌ SECRET_KEY must be at least 32 characters${NC}"
    exit 1
fi

if [[ ! "$DATABASE_URL" =~ ^postgresql:// ]]; then
    echo -e "${RED}❌ DATABASE_URL must be a PostgreSQL connection string${NC}"
    exit 1
fi

if [[ ! "$SUPABASE_URL" =~ ^https:// ]]; then
    echo -e "${RED}❌ SUPABASE_URL must be a valid HTTPS URL${NC}"
    exit 1
fi

if [[ ! "$OPENAI_API_KEY" =~ ^sk- ]]; then
    echo -e "${RED}❌ OPENAI_API_KEY must start with 'sk-'${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All validations passed!${NC}"
echo ""

# Save to export file
echo -e "${BLUE}Creating environment export file...${NC}"

cat > export-production-env.sh << 'EOF'
#!/bin/bash
# AdCopySurge Production Environment Variables
# Source this file before running deploy-secure.sh
# Usage: source export-production-env.sh

# SECURITY: These are production secrets - handle with care!
EOF

echo "export SECRET_KEY='$SECRET_KEY'" >> export-production-env.sh
echo "export DATABASE_URL='$DATABASE_URL'" >> export-production-env.sh  
echo "export SUPABASE_URL='$SUPABASE_URL'" >> export-production-env.sh
echo "export SUPABASE_ANON_KEY='$SUPABASE_ANON_KEY'" >> export-production-env.sh
echo "export SUPABASE_SERVICE_ROLE_KEY='$SUPABASE_SERVICE_ROLE_KEY'" >> export-production-env.sh
echo "export SUPABASE_JWT_SECRET='$SUPABASE_JWT_SECRET'" >> export-production-env.sh
echo "export OPENAI_API_KEY='$OPENAI_API_KEY'" >> export-production-env.sh
echo "export CORS_ORIGINS='$CORS_ORIGINS'" >> export-production-env.sh
echo "export REDIS_URL='$REDIS_URL'" >> export-production-env.sh
echo "export REACT_APP_API_URL='$REACT_APP_API_URL'" >> export-production-env.sh
echo "export REACT_APP_SITE_URL='$REACT_APP_SITE_URL'" >> export-production-env.sh

chmod 600 export-production-env.sh

echo -e "${GREEN}✅ Environment export file created: export-production-env.sh${NC}"
echo ""

echo -e "${YELLOW}⚠️  SECURITY WARNING:${NC}"
echo "- The file 'export-production-env.sh' contains production secrets"
echo "- Keep this file secure and never commit it to version control"
echo "- Delete it after successful deployment"
echo ""

echo -e "${BLUE}Next steps:${NC}"
echo "1. Transfer files to your VPS using rsync (as you mentioned):"
echo "   rsync -avz --progress \"/mnt/c/Users/User/Desktop/Eledami/adsurge/acs-clean/\" root@46.247.108.207:/root/acs-clean/"
echo ""
echo "2. On your VPS, run:"
echo "   cd /root/acs-clean"
echo "   source export-production-env.sh"
echo "   chmod +x deploy-secure.sh"
echo "   ./deploy-secure.sh"
echo ""
echo -e "${GREEN}🚀 Ready for secure deployment!${NC}"
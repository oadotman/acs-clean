#!/bin/bash

# AdCopySurge Secure Deployment Script
# This script implements secure deployment practices with proper secret management

set -euo pipefail  # Exit on error, undefined variables, and pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="adcopysurge"
PROJECT_DIR="/root/acs-clean"
BACKUP_DIR="/root/backups"
LOG_FILE="/var/log/${PROJECT_NAME}/deployment.log"
DOCKER_COMPOSE_FILE="docker-compose.production.yml"

# Functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Create necessary directories
setup_directories() {
    log "Setting up directories..."
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "/var/log/$PROJECT_NAME"
    mkdir -p "/etc/$PROJECT_NAME"
    
    # Secure permissions
    chmod 750 "/var/log/$PROJECT_NAME"
    chmod 700 "/etc/$PROJECT_NAME"
    
    log_success "Directories created with secure permissions"
}

# Backup current deployment
backup_current_deployment() {
    log "Creating backup of current deployment..."
    
    if [ -d "$PROJECT_DIR" ]; then
        BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
        tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$(dirname "$PROJECT_DIR")" "$(basename "$PROJECT_DIR")" 2>/dev/null || true
        log_success "Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
    else
        log_warning "No existing deployment found to backup"
    fi
}

# Validate environment variables
validate_environment() {
    log "Validating environment variables..."
    
    local required_vars=(
        "SECRET_KEY"
        "DATABASE_URL"
        "SUPABASE_URL"
        "SUPABASE_ANON_KEY"
        "SUPABASE_SERVICE_ROLE_KEY"
        "SUPABASE_JWT_SECRET"
        "OPENAI_API_KEY"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        log_error "Please set these variables before deployment"
        exit 1
    fi
    
    # Validate SECRET_KEY length
    if [[ ${#SECRET_KEY} -lt 32 ]]; then
        log_error "SECRET_KEY must be at least 32 characters long"
        exit 1
    fi
    
    log_success "Environment variables validated"
}

# Create secure environment file
create_secure_env() {
    log "Creating secure environment file..."
    
    local env_file="/etc/$PROJECT_NAME/production.env"
    
    cat > "$env_file" << EOF
# AdCopySurge Production Environment
# Generated: $(date)
# SECURITY: This file contains secrets - never commit to version control

# Environment
ENVIRONMENT=production
DEBUG=False
VPS_DEPLOYMENT=true
PRODUCTION_VPS=true

# Security
SECRET_KEY=${SECRET_KEY}
CORS_ORIGINS=${CORS_ORIGINS:-https://v44954.datalix.de,https://app.adcopysurge.com}

# Database
DATABASE_URL=${DATABASE_URL}

# Supabase
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
SUPABASE_JWT_SECRET=${SUPABASE_JWT_SECRET}

# AI Services
OPENAI_API_KEY=${OPENAI_API_KEY}

# Rate Limiting
RATE_LIMIT_ENABLED=true
ENABLE_RATE_LIMITING=true

# Redis (if available)
REDIS_URL=${REDIS_URL:-redis://localhost:6379/0}

# Frontend
REACT_APP_API_URL=${REACT_APP_API_URL:-http://46.247.108.207:8000/api}
REACT_APP_ENVIRONMENT=production
REACT_APP_SITE_URL=${REACT_APP_SITE_URL:-https://v44954.datalix.de}
REACT_APP_SUPABASE_URL=${SUPABASE_URL}
REACT_APP_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
EOF

    # Secure permissions
    chmod 600 "$env_file"
    chown root:root "$env_file"
    
    log_success "Secure environment file created at $env_file"
}

# Security pre-deployment checks
security_checks() {
    log "Running security checks..."
    
    # Check for hardcoded secrets in code
    if grep -r "SUPABASE_SERVICE_ROLE_KEY\|JWT_SECRET\|sk-[a-zA-Z0-9]" "$PROJECT_DIR" --exclude-dir=.git --exclude="*.log" --exclude="deploy-secure.sh" 2>/dev/null; then
        log_error "Found potential hardcoded secrets in code!"
        log_error "Please remove all hardcoded secrets before deployment"
        exit 1
    fi
    
    # Check Docker Compose file exists
    if [[ ! -f "$PROJECT_DIR/docker-compose.production.template.yml" ]]; then
        log_error "Docker Compose template not found"
        exit 1
    fi
    
    # Verify SSL certificates
    if command -v openssl >/dev/null 2>&1; then
        if ! openssl s_client -connect 46.247.108.207:443 -servername api.adcopysurge.com </dev/null 2>/dev/null | openssl x509 -noout -checkend 2592000 >/dev/null 2>&1; then
            log_warning "SSL certificate may expire within 30 days or is not configured"
        else
            log_success "SSL certificate is valid"
        fi
    fi
    
    log_success "Security checks passed"
}

# Create production Docker Compose file
create_docker_compose() {
    log "Creating production Docker Compose file..."
    
    # Copy template and set up environment variable substitution
    cp "$PROJECT_DIR/docker-compose.production.template.yml" "$PROJECT_DIR/$DOCKER_COMPOSE_FILE"
    
    # Add environment file reference
    cat >> "$PROJECT_DIR/$DOCKER_COMPOSE_FILE" << EOF

# Production environment file
env_file:
  - /etc/$PROJECT_NAME/production.env
EOF
    
    log_success "Production Docker Compose file created"
}

# Deploy application
deploy_application() {
    log "Deploying application..."
    
    cd "$PROJECT_DIR"
    
    # Pull latest images and build
    docker-compose -f "$DOCKER_COMPOSE_FILE" pull || log_warning "Could not pull some images"
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    # Stop existing containers
    docker-compose -f "$DOCKER_COMPOSE_FILE" down --remove-orphans
    
    # Start services
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    log_success "Application deployed"
}

# Health check
health_check() {
    log "Running health checks..."
    
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f -s "http://localhost:8000/health" >/dev/null 2>&1; then
            log_success "Backend health check passed"
            break
        fi
        
        attempt=$((attempt + 1))
        if [[ $attempt -eq $max_attempts ]]; then
            log_error "Backend health check failed after $max_attempts attempts"
            exit 1
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, retrying..."
        sleep 5
    done
    
    # Check frontend
    if curl -f -s "http://localhost:3000" >/dev/null 2>&1; then
        log_success "Frontend health check passed"
    else
        log_warning "Frontend health check failed"
    fi
}

# Setup monitoring
setup_monitoring() {
    log "Setting up monitoring..."
    
    # Create systemd service for monitoring
    cat > "/etc/systemd/system/${PROJECT_NAME}-monitor.service" << EOF
[Unit]
Description=AdCopySurge Monitoring
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/usr/bin/docker-compose -f $PROJECT_DIR/$DOCKER_COMPOSE_FILE ps
WorkingDirectory=$PROJECT_DIR

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    systemctl daemon-reload
    systemctl enable "${PROJECT_NAME}-monitor.timer"
    systemctl start "${PROJECT_NAME}-monitor.timer"
    
    log_success "Monitoring setup complete"
}

# Cleanup old backups
cleanup_backups() {
    log "Cleaning up old backups..."
    
    # Keep only last 7 days of backups
    find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete 2>/dev/null || true
    
    log_success "Old backups cleaned up"
}

# Post-deployment security hardening
post_deployment_security() {
    log "Applying post-deployment security measures..."
    
    # Remove any temporary files
    find "$PROJECT_DIR" -name "*.tmp" -delete 2>/dev/null || true
    find "$PROJECT_DIR" -name ".env*" -not -path "*/template*" -delete 2>/dev/null || true
    
    # Set secure permissions on project directory
    chown -R root:docker "$PROJECT_DIR" 2>/dev/null || chown -R root:root "$PROJECT_DIR"
    find "$PROJECT_DIR" -type d -exec chmod 755 {} \;
    find "$PROJECT_DIR" -type f -exec chmod 644 {} \;
    chmod +x "$PROJECT_DIR"/*.sh 2>/dev/null || true
    
    # Restart fail2ban if available
    if systemctl is-active --quiet fail2ban; then
        systemctl restart fail2ban
        log_success "fail2ban restarted"
    fi
    
    log_success "Post-deployment security measures applied"
}

# Main deployment function
main() {
    log "🚀 Starting secure deployment of $PROJECT_NAME"
    
    check_root
    setup_directories
    backup_current_deployment
    validate_environment
    create_secure_env
    security_checks
    create_docker_compose
    deploy_application
    health_check
    setup_monitoring
    cleanup_backups
    post_deployment_security
    
    log_success "🎉 Secure deployment completed successfully!"
    log "📊 Service status:"
    docker-compose -f "$PROJECT_DIR/$DOCKER_COMPOSE_FILE" ps
    
    log ""
    log "🔒 Security Notes:"
    log "- Environment variables are stored securely in /etc/$PROJECT_NAME/production.env"
    log "- Backups are stored in $BACKUP_DIR"
    log "- Logs are available in /var/log/$PROJECT_NAME/"
    log "- Monitoring is active via systemd timer"
    log ""
    log "🌐 Access your application:"
    log "- Frontend: http://46.247.108.207:3000"
    log "- Backend: http://46.247.108.207:8000"
    log "- Health Check: http://46.247.108.207:8000/health"
}

# Error handling
trap 'log_error "Deployment failed at line $LINENO. Check logs for details."' ERR

# Run main function
main "$@"
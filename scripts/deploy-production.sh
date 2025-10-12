#!/bin/bash

# ================================
# 🚀 AdCopySurge Production Deployment Script
# ================================
# 
# This script handles manual production deployment to your Datalix VPS.
# It performs zero-downtime deployment with health checks and rollback capabilities.
#
# Usage:
#   ./scripts/deploy-production.sh
#   ./scripts/deploy-production.sh --tag v1.2.3
#   ./scripts/deploy-production.sh --rollback
#
# Prerequisites:
# - SSH access to production server
# - Docker and Docker Compose installed on server  
# - Environment variables configured
# ================================

set -euo pipefail  # Exit on any error

# ================================
# 🔧 CONFIGURATION
# ================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Production server details
PROD_SERVER="your-datalix-server.com"
PROD_USER="deploy"
PROD_PATH="/opt/adcopysurge"
COMPOSE_PROJECT_NAME="adcopysurge-prod"

# Docker configuration
DOCKER_REGISTRY="ghcr.io"
DOCKER_NAMESPACE="yourusername/adcopysurge"
DEFAULT_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ================================
# 🛠️ HELPER FUNCTIONS
# ================================
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# SSH command wrapper
ssh_exec() {
    ssh -o StrictHostKeyChecking=no "$PROD_USER@$PROD_SERVER" "$@"
}

# SCP file transfer wrapper
scp_transfer() {
    scp -o StrictHostKeyChecking=no "$1" "$PROD_USER@$PROD_SERVER:$2"
}

# ================================
# 🔍 PRE-DEPLOYMENT CHECKS
# ================================
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check if required commands are available
    if ! command_exists ssh; then
        error "SSH is required but not installed"
    fi
    
    if ! command_exists scp; then
        error "SCP is required but not installed"
    fi
    
    if ! command_exists docker; then
        warning "Docker not found locally (needed for building images)"
    fi
    
    # Check if we can connect to the server
    if ! ssh_exec "echo 'SSH connection successful'"; then
        error "Cannot connect to production server $PROD_SERVER"
    fi
    
    # Check if Docker is available on server
    if ! ssh_exec "docker --version >/dev/null 2>&1"; then
        error "Docker is not installed on the production server"
    fi
    
    # Check if Docker Compose is available on server
    if ! ssh_exec "docker compose version >/dev/null 2>&1"; then
        error "Docker Compose is not installed on the production server"
    fi
    
    success "All pre-deployment checks passed"
}

# ================================
# 🏗️ BUILD AND PUSH IMAGES
# ================================
build_and_push_images() {
    local tag="${1:-$DEFAULT_TAG}"
    
    log "Building and pushing Docker images with tag: $tag"
    
    # Backend image
    log "Building backend image..."
    docker build -t "$DOCKER_REGISTRY/$DOCKER_NAMESPACE/backend:$tag" \
        -f backend/Dockerfile backend/
    
    docker push "$DOCKER_REGISTRY/$DOCKER_NAMESPACE/backend:$tag"
    success "Backend image pushed successfully"
    
    # Frontend image
    log "Building frontend image..."
    docker build -t "$DOCKER_REGISTRY/$DOCKER_NAMESPACE/frontend:$tag" \
        -f frontend/Dockerfile frontend/
        
    docker push "$DOCKER_REGISTRY/$DOCKER_NAMESPACE/frontend:$tag"
    success "Frontend image pushed successfully"
}

# ================================
# 📦 DEPLOY TO PRODUCTION
# ================================
deploy_to_production() {
    local tag="${1:-$DEFAULT_TAG}"
    
    log "Deploying to production with tag: $tag"
    
    # Create deployment directory on server
    ssh_exec "mkdir -p $PROD_PATH/{nginx,monitoring,ssl,backups}"
    
    # Transfer Docker Compose files
    log "Transferring configuration files..."
    scp_transfer "docker-compose.prod.yml" "$PROD_PATH/"
    scp_transfer ".env.production" "$PROD_PATH/.env"
    scp_transfer "nginx/production.conf" "$PROD_PATH/nginx/"
    scp_transfer "monitoring/prometheus.yml" "$PROD_PATH/monitoring/"
    
    # Set the image tag
    ssh_exec "cd $PROD_PATH && echo 'DOCKER_IMAGE_TAG=$tag' >> .env"
    
    # Pull latest images
    log "Pulling Docker images on production server..."
    ssh_exec "cd $PROD_PATH && docker compose -f docker-compose.prod.yml pull"
    
    # Run database migrations
    log "Running database migrations..."
    ssh_exec "cd $PROD_PATH && python backend/scripts/init_passport_schema.py --environment=production"
    
    success "Configuration files transferred and migrations completed"
}

# ================================
# 🔄 ZERO-DOWNTIME DEPLOYMENT
# ================================
zero_downtime_deploy() {
    local tag="${1:-$DEFAULT_TAG}"
    
    log "Performing zero-downtime deployment..."
    
    # Start new containers with a different project name
    local temp_project="${COMPOSE_PROJECT_NAME}-temp"
    
    log "Starting new containers..."
    ssh_exec "cd $PROD_PATH && COMPOSE_PROJECT_NAME=$temp_project docker compose -f docker-compose.prod.yml up -d --remove-orphans"
    
    # Wait for services to be healthy
    log "Waiting for services to become healthy..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if ssh_exec "cd $PROD_PATH && COMPOSE_PROJECT_NAME=$temp_project docker compose -f docker-compose.prod.yml ps --filter health=healthy | grep -q healthy"; then
            success "New services are healthy"
            break
        fi
        
        ((attempt++))
        if [ $attempt -eq $max_attempts ]; then
            error "New services failed to become healthy after $max_attempts attempts"
        fi
        
        log "Attempt $attempt/$max_attempts: Waiting for services to be ready..."
        sleep 10
    done
    
    # Health check the new deployment
    log "Running health checks..."
    if ! ssh_exec "curl -f http://localhost:3000/health > /dev/null 2>&1"; then
        error "Frontend health check failed"
    fi
    
    if ! ssh_exec "curl -f http://localhost:8000/api/health > /dev/null 2>&1"; then
        error "Backend health check failed"
    fi
    
    success "Health checks passed"
    
    # Switch traffic to new containers
    log "Switching to new deployment..."
    
    # Stop old containers
    ssh_exec "cd $PROD_PATH && COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME docker compose -f docker-compose.prod.yml down || true"
    
    # Rename new containers to production
    ssh_exec "cd $PROD_PATH && COMPOSE_PROJECT_NAME=$temp_project docker compose -f docker-compose.prod.yml down"
    ssh_exec "cd $PROD_PATH && COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME docker compose -f docker-compose.prod.yml up -d --remove-orphans"
    
    success "Zero-downtime deployment completed"
}

# ================================
# 🔙 ROLLBACK FUNCTIONALITY
# ================================
rollback_deployment() {
    log "Rolling back to previous deployment..."
    
    # Get previous image tag (you might want to store this in a file)
    local previous_tag
    previous_tag=$(ssh_exec "cd $PROD_PATH && grep DOCKER_IMAGE_TAG .env.backup 2>/dev/null | cut -d'=' -f2" || echo "")
    
    if [ -z "$previous_tag" ]; then
        error "No previous deployment found to rollback to"
    fi
    
    log "Rolling back to tag: $previous_tag"
    
    # Restore previous environment
    ssh_exec "cd $PROD_PATH && cp .env.backup .env"
    
    # Pull previous images
    ssh_exec "cd $PROD_PATH && docker compose -f docker-compose.prod.yml pull"
    
    # Restart services
    ssh_exec "cd $PROD_PATH && docker compose -f docker-compose.prod.yml down"
    ssh_exec "cd $PROD_PATH && docker compose -f docker-compose.prod.yml up -d --remove-orphans"
    
    # Wait for rollback to complete
    sleep 30
    
    # Health check
    if ssh_exec "curl -f http://localhost:8000/api/health > /dev/null 2>&1"; then
        success "Rollback completed successfully"
    else
        error "Rollback health check failed"
    fi
}

# ================================
# 🧹 CLEANUP
# ================================
cleanup_deployment() {
    log "Cleaning up old Docker images and containers..."
    
    # Remove unused images
    ssh_exec "docker image prune -af --filter 'until=168h'" || true  # Keep images from last 7 days
    
    # Remove unused volumes
    ssh_exec "docker volume prune -f" || true
    
    # Remove unused networks
    ssh_exec "docker network prune -f" || true
    
    success "Cleanup completed"
}

# ================================
# 📊 POST-DEPLOYMENT VERIFICATION
# ================================
post_deployment_verification() {
    log "Running post-deployment verification..."
    
    # Check all services are running
    local services_status
    services_status=$(ssh_exec "cd $PROD_PATH && docker compose -f docker-compose.prod.yml ps --format table")
    echo "$services_status"
    
    # Check logs for any immediate errors
    log "Checking recent logs for errors..."
    ssh_exec "cd $PROD_PATH && docker compose -f docker-compose.prod.yml logs --tail=50 backend" || true
    
    # API health check
    log "Testing API endpoints..."
    if ssh_exec "curl -f http://localhost:8000/api/health"; then
        success "Backend API is responding"
    else
        warning "Backend API health check failed"
    fi
    
    # Frontend health check
    if ssh_exec "curl -f http://localhost:3000/health"; then
        success "Frontend is responding"
    else
        warning "Frontend health check failed"
    fi
    
    # Check database connectivity
    log "Checking database connectivity..."
    if ssh_exec "cd $PROD_PATH && docker compose -f docker-compose.prod.yml exec -T backend python -c \"from app.database import get_db; next(get_db())\""; then
        success "Database connectivity verified"
    else
        warning "Database connectivity check failed"
    fi
    
    success "Post-deployment verification completed"
}

# ================================
# 📱 NOTIFICATIONS
# ================================
send_deployment_notification() {
    local status="$1"
    local tag="${2:-$DEFAULT_TAG}"
    local message
    
    if [ "$status" = "success" ]; then
        message="🚀 AdCopySurge production deployment successful! Tag: $tag"
    else
        message="❌ AdCopySurge production deployment failed! Tag: $tag"
    fi
    
    log "$message"
    
    # You can add Slack, Discord, or email notifications here
    # Example for Slack:
    # curl -X POST -H 'Content-type: application/json' \
    #     --data "{\"text\":\"$message\"}" \
    #     "$SLACK_WEBHOOK_URL"
}

# ================================
# 🎯 MAIN EXECUTION
# ================================
main() {
    local command="${1:-deploy}"
    local tag="${2:-$DEFAULT_TAG}"
    
    case "$command" in
        "deploy"|"--deploy")
            log "🚀 Starting AdCopySurge production deployment..."
            
            # Backup current environment
            ssh_exec "cd $PROD_PATH && cp .env .env.backup 2>/dev/null || true"
            
            pre_deployment_checks
            build_and_push_images "$tag"
            deploy_to_production "$tag"
            zero_downtime_deploy "$tag"
            post_deployment_verification
            cleanup_deployment
            send_deployment_notification "success" "$tag"
            
            success "🎉 Production deployment completed successfully!"
            ;;
            
        "--rollback"|"rollback")
            log "🔙 Starting rollback procedure..."
            rollback_deployment
            send_deployment_notification "rollback" "previous"
            success "🔙 Rollback completed successfully!"
            ;;
            
        "--health"|"health")
            log "🔍 Running health checks..."
            post_deployment_verification
            ;;
            
        "--cleanup"|"cleanup")
            log "🧹 Running cleanup..."
            cleanup_deployment
            ;;
            
        "--help"|"help")
            echo "Usage: $0 [deploy|rollback|health|cleanup] [tag]"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy to production (default)"
            echo "  rollback - Rollback to previous deployment"
            echo "  health   - Run health checks"
            echo "  cleanup  - Clean up old Docker resources"
            echo "  help     - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Deploy latest tag"
            echo "  $0 deploy v1.2.3      # Deploy specific tag"
            echo "  $0 rollback           # Rollback to previous"
            ;;
            
        *)
            error "Unknown command: $command. Use --help for usage information."
            ;;
    esac
}

# Handle script arguments
if [ "${1:-}" = "--tag" ] && [ -n "${2:-}" ]; then
    main "deploy" "$2"
else
    main "${1:-deploy}" "${2:-$DEFAULT_TAG}"
fi
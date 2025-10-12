# REPLACED WITH ROBUST VERSION - See health_fixed.py for reference
# This file temporarily disabled during Phase 1 fixes
"""
Health check and metrics endpoints for AdCopySurge API
Production-ready monitoring endpoints for deployment
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import os
from datetime import datetime
from typing import Dict, Any
from app.core.database import get_db
from app.core.config import settings
from app.core.logging import get_logger

# Optional import for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not available - system monitoring disabled")

logger = get_logger(__name__)
router = APIRouter()

# Startup time for uptime calculation
start_time = time.time()


@router.get("/health", tags=["monitoring"])
async def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check endpoint for production monitoring
    Returns status of all critical system components
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.NODE_ENV,
        "checks": {}
    }
    
    is_healthy = True
    
    # 1. Database connectivity check
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        is_healthy = False
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        logger.error(f"Database health check failed: {e}")
    
    # 2. Disk space check
    if PSUTIL_AVAILABLE:
        try:
            disk_usage = psutil.disk_usage('/')
            free_space_gb = disk_usage.free / (1024**3)
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            if used_percent > 90:
                is_healthy = False
                health_status["checks"]["disk"] = {
                    "status": "critical",
                    "message": f"Low disk space: {used_percent:.1f}% used",
                    "free_space_gb": round(free_space_gb, 2),
                    "used_percent": round(used_percent, 1)
                }
            elif used_percent > 80:
                health_status["checks"]["disk"] = {
                    "status": "warning",
                    "message": f"Moderate disk usage: {used_percent:.1f}% used",
                    "free_space_gb": round(free_space_gb, 2),
                    "used_percent": round(used_percent, 1)
                }
            else:
                health_status["checks"]["disk"] = {
                    "status": "healthy",
                    "message": "Sufficient disk space available",
                    "free_space_gb": round(free_space_gb, 2),
                    "used_percent": round(used_percent, 1)
                }
        except Exception as e:
            health_status["checks"]["disk"] = {
                "status": "unknown",
                "message": f"Could not check disk space: {str(e)}"
            }
    else:
        health_status["checks"]["disk"] = {
            "status": "skipped",
            "message": "Disk monitoring unavailable - psutil not installed"
        }
    
    # 3. Memory check
    if PSUTIL_AVAILABLE:
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            available_gb = memory.available / (1024**3)
            
            if memory_percent > 90:
                is_healthy = False
                health_status["checks"]["memory"] = {
                    "status": "critical",
                    "message": f"High memory usage: {memory_percent:.1f}% used",
                    "available_gb": round(available_gb, 2),
                    "used_percent": round(memory_percent, 1)
                }
            elif memory_percent > 85:
                health_status["checks"]["memory"] = {
                    "status": "warning",
                    "message": f"High memory usage: {memory_percent:.1f}% used",
                    "available_gb": round(available_gb, 2),
                    "used_percent": round(memory_percent, 1)
                }
            else:
                health_status["checks"]["memory"] = {
                    "status": "healthy",
                    "message": "Memory usage normal",
                    "available_gb": round(available_gb, 2),
                    "used_percent": round(memory_percent, 1)
                }
        except Exception as e:
            health_status["checks"]["memory"] = {
                "status": "unknown",
                "message": f"Could not check memory: {str(e)}"
            }
    else:
        health_status["checks"]["memory"] = {
            "status": "skipped",
            "message": "Memory monitoring unavailable - psutil not installed"
        }
    
    # 4. Blog service health check
    if settings.ENABLE_BLOG:
        try:
            from app.blog.services.blog_service import BlogService
            blog_service = BlogService(settings.BLOG_CONTENT_DIR, settings.BLOG_GRACEFUL_DEGRADATION)
            blog_health = blog_service.get_health_status()
            health_status["checks"]["blog_service"] = {
                "status": "healthy" if blog_health["healthy"] else "degraded",
                "message": blog_health.get("error_message", "Blog service operational"),
                "dependencies": blog_health["dependencies"]
            }
        except Exception as e:
            health_status["checks"]["blog_service"] = {
                "status": "unavailable",
                "message": f"Blog service check failed: {str(e)}"
            }
    else:
        health_status["checks"]["blog_service"] = {
            "status": "disabled",
            "message": "Blog functionality disabled via configuration"
        }
    
    # 5. Check critical environment variables
    critical_vars = ["SECRET_KEY", "DATABASE_URL"]
    missing_vars = []
    for var in critical_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var)
    
    if missing_vars:
        is_healthy = False
        health_status["checks"]["configuration"] = {
            "status": "unhealthy",
            "message": f"Missing critical environment variables: {', '.join(missing_vars)}"
        }
    else:
        health_status["checks"]["configuration"] = {
            "status": "healthy",
            "message": "All critical environment variables configured"
        }
    
    # Set overall status
    if not is_healthy:
        health_status["status"] = "unhealthy"
    
    # Return appropriate HTTP status
    if is_healthy:
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)


@router.get("/health/ready", tags=["monitoring"])
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness probe - returns 200 when app is ready to serve traffic
    Used by Kubernetes readiness probes
    """
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503, 
            detail={
                "status": "not_ready",
                "message": "Database not accessible"
            }
        )


@router.get("/health/live", tags=["monitoring"])
async def liveness_check():
    """
    Liveness probe - returns 200 if app is running (doesn't check dependencies)
    Used by Kubernetes liveness probes
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - start_time)
    }


@router.get("/metrics", tags=["monitoring"])
async def get_metrics(db: Session = Depends(get_db)):
    """
    Prometheus-compatible metrics endpoint
    Returns application and system metrics in key-value format
    """
    try:
        current_time = time.time()
        uptime = current_time - start_time
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Application metrics
        metrics = {
            # Application info
            "adcopysurge_info": {
                "value": 1,
                "labels": {
                    "version": settings.VERSION,
                    "environment": settings.NODE_ENV
                }
            },
            
            # Uptime
            "adcopysurge_uptime_seconds": uptime,
            
            # System metrics
            "adcopysurge_cpu_usage_percent": cpu_percent,
            "adcopysurge_memory_usage_percent": memory.percent,
            "adcopysurge_memory_available_bytes": memory.available,
            "adcopysurge_disk_usage_percent": (disk.used / disk.total) * 100,
            "adcopysurge_disk_free_bytes": disk.free,
            
            # Database connection test
            "adcopysurge_database_connections_active": 1 if test_db_connection(db) else 0,
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics collection failed")


@router.get("/metrics/prometheus", tags=["monitoring"])
async def get_prometheus_metrics(db: Session = Depends(get_db)):
    """
    Prometheus text format metrics
    Returns metrics in Prometheus exposition format
    """
    try:
        current_time = time.time()
        uptime = current_time - start_time
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Generate Prometheus format
        prometheus_metrics = f"""# HELP adcopysurge_info Application information
# TYPE adcopysurge_info gauge
adcopysurge_info{{version="{settings.VERSION}",environment="{settings.NODE_ENV}"}} 1

# HELP adcopysurge_uptime_seconds Application uptime in seconds
# TYPE adcopysurge_uptime_seconds counter
adcopysurge_uptime_seconds {uptime}

# HELP adcopysurge_cpu_usage_percent Current CPU usage percentage
# TYPE adcopysurge_cpu_usage_percent gauge
adcopysurge_cpu_usage_percent {cpu_percent}

# HELP adcopysurge_memory_usage_percent Current memory usage percentage
# TYPE adcopysurge_memory_usage_percent gauge
adcopysurge_memory_usage_percent {memory.percent}

# HELP adcopysurge_memory_available_bytes Available memory in bytes
# TYPE adcopysurge_memory_available_bytes gauge
adcopysurge_memory_available_bytes {memory.available}

# HELP adcopysurge_disk_usage_percent Disk usage percentage
# TYPE adcopysurge_disk_usage_percent gauge
adcopysurge_disk_usage_percent {(disk.used / disk.total) * 100}

# HELP adcopysurge_disk_free_bytes Free disk space in bytes
# TYPE adcopysurge_disk_free_bytes gauge
adcopysurge_disk_free_bytes {disk.free}

# HELP adcopysurge_database_connections_active Database connection status
# TYPE adcopysurge_database_connections_active gauge
adcopysurge_database_connections_active {1 if test_db_connection(db) else 0}
"""
        
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(prometheus_metrics, media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Prometheus metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics collection failed")


def test_db_connection(db: Session) -> bool:
    """Test database connection"""
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@router.get("/version", tags=["monitoring"])
async def get_version():
    """Get application version information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.NODE_ENV,
        "debug": settings.DEBUG,
        "timestamp": datetime.utcnow().isoformat()
    }

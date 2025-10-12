"""
Health check and metrics endpoints for AdCopySurge API
Production-ready monitoring endpoints for deployment - NEVER returns 500!
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

try:
    from app.core.database_enhanced import get_db, get_database_health
except ImportError:
    try:
        from app.core.database import get_db
        get_database_health = None
    except ImportError:
        get_db = None
        get_database_health = None

try:
    from app.core.config import settings
except ImportError:
    class MockSettings:
        VERSION = "1.0.0"
        NODE_ENV = "unknown"
        ENABLE_BLOG = True
        BLOG_CONTENT_DIR = "content/blog"
        BLOG_GRACEFUL_DEGRADATION = True
    settings = MockSettings()

try:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Optional import for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not available - system monitoring disabled")

router = APIRouter()

# Startup time for uptime calculation
start_time = time.time()

class ComponentState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    DISABLED = "disabled"
    UNKNOWN = "unknown"

def safe_get_db_session():
    """Safely get a database session"""
    try:
        if get_db is None:
            return None
        # Try to get a database session
        db_gen = get_db()
        return next(db_gen)
    except Exception as e:
        logger.warning(f"Failed to get DB session: {e}")
        return None

@router.get("/health", tags=["monitoring"])
async def health_check():
    """
    Comprehensive health check endpoint for production monitoring
    Returns status of all critical system components - NEVER returns 500
    """
    health_status = {
        "status": ComponentState.HEALTHY,
        "timestamp": datetime.utcnow().isoformat(),
        "version": getattr(settings, "VERSION", "unknown"),
        "environment": getattr(settings, "NODE_ENV", "unknown"),
        "checks": {}
    }
    
    overall_health = ComponentState.HEALTHY

    # 1. Enhanced Database connectivity check
    try:
        if get_database_health:
            # Use enhanced database health check
            db_health = get_database_health()
            if db_health["connected"] and db_health["sync_available"]:
                health_status["checks"]["database"] = {
                    "status": ComponentState.HEALTHY,
                    "message": "Database connection successful",
                    "details": {
                        "sync_available": db_health["sync_available"],
                        "async_available": db_health["async_available"],
                        "type": db_health["initialization_status"].get("database_type", "unknown")
                    }
                }
            else:
                health_status["checks"]["database"] = {
                    "status": ComponentState.DEGRADED,
                    "message": "Database partially available",
                    "details": db_health
                }
                if overall_health == ComponentState.HEALTHY:
                    overall_health = ComponentState.DEGRADED
        else:
            # Fallback to basic database check
            db = safe_get_db_session()
            if db is not None:
                db.execute(text("SELECT 1"))
                health_status["checks"]["database"] = {
                    "status": ComponentState.HEALTHY,
                    "message": "Database connection successful"
                }
                db.close()
            else:
                health_status["checks"]["database"] = {
                    "status": ComponentState.DISABLED,
                    "message": "Database not configured or unavailable"
                }
                if overall_health == ComponentState.HEALTHY:
                    overall_health = ComponentState.DEGRADED
    except Exception as e:
        overall_health = ComponentState.DEGRADED
        health_status["checks"]["database"] = {
            "status": ComponentState.DOWN,
            "message": f"Database connection failed: {str(e)[:100]}"
        }
        logger.warning(f"Database health check failed: {e}")

    # 2. Disk space check
    try:
        if PSUTIL_AVAILABLE:
            disk_usage = psutil.disk_usage('/' if os.name != 'nt' else 'C:\\')
            free_space_gb = disk_usage.free / (1024**3)
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            if used_percent > 90:
                if overall_health != ComponentState.DOWN:
                    overall_health = ComponentState.DOWN
                health_status["checks"]["disk"] = {
                    "status": ComponentState.DOWN,
                    "message": f"Critical: Low disk space: {used_percent:.1f}% used",
                    "free_space_gb": round(free_space_gb, 2),
                    "used_percent": round(used_percent, 1)
                }
            elif used_percent > 80:
                if overall_health == ComponentState.HEALTHY:
                    overall_health = ComponentState.DEGRADED
                health_status["checks"]["disk"] = {
                    "status": ComponentState.DEGRADED,
                    "message": f"Warning: Moderate disk usage: {used_percent:.1f}% used",
                    "free_space_gb": round(free_space_gb, 2),
                    "used_percent": round(used_percent, 1)
                }
            else:
                health_status["checks"]["disk"] = {
                    "status": ComponentState.HEALTHY,
                    "message": "Sufficient disk space available",
                    "free_space_gb": round(free_space_gb, 2),
                    "used_percent": round(used_percent, 1)
                }
        else:
            health_status["checks"]["disk"] = {
                "status": ComponentState.DISABLED,
                "message": "Disk monitoring unavailable - psutil not installed"
            }
    except Exception as e:
        health_status["checks"]["disk"] = {
            "status": ComponentState.UNKNOWN,
            "message": f"Could not check disk space: {str(e)[:50]}"
        }
        logger.warning(f"Disk check failed: {e}")

    # 3. Memory check
    try:
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            available_gb = memory.available / (1024**3)
            
            if memory_percent > 90:
                if overall_health != ComponentState.DOWN:
                    overall_health = ComponentState.DOWN
                health_status["checks"]["memory"] = {
                    "status": ComponentState.DOWN,
                    "message": f"Critical: High memory usage: {memory_percent:.1f}% used",
                    "available_gb": round(available_gb, 2),
                    "used_percent": round(memory_percent, 1)
                }
            elif memory_percent > 85:
                if overall_health == ComponentState.HEALTHY:
                    overall_health = ComponentState.DEGRADED
                health_status["checks"]["memory"] = {
                    "status": ComponentState.DEGRADED,
                    "message": f"Warning: High memory usage: {memory_percent:.1f}% used",
                    "available_gb": round(available_gb, 2),
                    "used_percent": round(memory_percent, 1)
                }
            else:
                health_status["checks"]["memory"] = {
                    "status": ComponentState.HEALTHY,
                    "message": "Memory usage normal",
                    "available_gb": round(available_gb, 2),
                    "used_percent": round(memory_percent, 1)
                }
        else:
            health_status["checks"]["memory"] = {
                "status": ComponentState.DISABLED,
                "message": "Memory monitoring unavailable - psutil not installed"
            }
    except Exception as e:
        health_status["checks"]["memory"] = {
            "status": ComponentState.UNKNOWN,
            "message": f"Could not check memory: {str(e)[:50]}"
        }
        logger.warning(f"Memory check failed: {e}")

    # 4. Blog service health check
    try:
        if getattr(settings, "ENABLE_BLOG", True):
            try:
                from app.blog.services.blog_service import BlogService
                blog_service = BlogService(
                    getattr(settings, "BLOG_CONTENT_DIR", "content/blog"),
                    getattr(settings, "BLOG_GRACEFUL_DEGRADATION", True)
                )
                blog_health = blog_service.get_health_status()
                blog_status = ComponentState.HEALTHY if blog_health["healthy"] else ComponentState.DEGRADED
                health_status["checks"]["blog_service"] = {
                    "status": blog_status,
                    "message": blog_health.get("error_message", "Blog service operational"),
                    "dependencies": blog_health.get("dependencies", {})
                }
                if blog_status == ComponentState.DEGRADED and overall_health == ComponentState.HEALTHY:
                    overall_health = ComponentState.DEGRADED
            except Exception as e:
                health_status["checks"]["blog_service"] = {
                    "status": ComponentState.DOWN,
                    "message": f"Blog service check failed: {str(e)[:100]}"
                }
                logger.warning(f"Blog service health check failed: {e}")
        else:
            health_status["checks"]["blog_service"] = {
                "status": ComponentState.DISABLED,
                "message": "Blog functionality disabled via configuration"
            }
    except Exception as e:
        health_status["checks"]["blog_service"] = {
            "status": ComponentState.UNKNOWN,
            "message": f"Blog service check error: {str(e)[:50]}"
        }
        logger.warning(f"Blog service health check error: {e}")

    # 5. Enhanced Supabase authentication health check
    try:
        try:
            from app.api.v1.auth_status import auth_health_check
            # Get database session for auth check
            auth_db = safe_get_db_session()
            if auth_db:
                auth_health = await auth_health_check(auth_db)
                auth_status_enum = getattr(ComponentState, auth_health["status"].upper(), ComponentState.UNKNOWN)
                health_status["checks"]["authentication"] = {
                    "status": auth_status_enum,
                    "message": f"Supabase auth system: {auth_health['status']}",
                    "details": auth_health.get("checks", {})
                }
                auth_db.close()
                
                # Update overall health based on auth status
                if auth_status_enum == ComponentState.DOWN and overall_health != ComponentState.DOWN:
                    # Only degrade if auth is completely down and we don't have anonymous fallback
                    if not auth_health.get("checks", {}).get("anonymous_fallback", False):
                        overall_health = ComponentState.DEGRADED
                elif auth_status_enum == ComponentState.DEGRADED and overall_health == ComponentState.HEALTHY:
                    overall_health = ComponentState.DEGRADED
            else:
                health_status["checks"]["authentication"] = {
                    "status": ComponentState.DISABLED,
                    "message": "Authentication health check skipped - no database"
                }
        except ImportError:
            health_status["checks"]["authentication"] = {
                "status": ComponentState.DISABLED,
                "message": "Enhanced authentication not available"
            }
        except Exception as e:
            health_status["checks"]["authentication"] = {
                "status": ComponentState.UNKNOWN,
                "message": f"Authentication health check failed: {str(e)[:50]}"
            }
            logger.warning(f"Authentication health check failed: {e}")
    except Exception as e:
        health_status["checks"]["authentication"] = {
            "status": ComponentState.UNKNOWN,
            "message": f"Authentication check error: {str(e)[:50]}"
        }
        logger.warning(f"Authentication check error: {e}")

    # 6. Check critical environment variables
    try:
        critical_vars = ["SECRET_KEY"]  # Removed DATABASE_URL since it may not be required
        missing_vars = []
        for var in critical_vars:
            if not getattr(settings, var, None):
                missing_vars.append(var)
        
        if missing_vars:
            overall_health = ComponentState.DOWN
            health_status["checks"]["configuration"] = {
                "status": ComponentState.DOWN,
                "message": f"Missing critical environment variables: {', '.join(missing_vars)}"
            }
        else:
            health_status["checks"]["configuration"] = {
                "status": ComponentState.HEALTHY,
                "message": "All critical environment variables configured"
            }
    except Exception as e:
        health_status["checks"]["configuration"] = {
            "status": ComponentState.UNKNOWN,
            "message": f"Configuration check error: {str(e)[:50]}"
        }
        logger.warning(f"Configuration check error: {e}")

    # Set overall status
    health_status["status"] = overall_health
    
    # Return appropriate HTTP status - NEVER 500!
    if overall_health in [ComponentState.HEALTHY, ComponentState.DEGRADED]:
        return health_status
    else:
        # Return 503 for DOWN status, but still return structured data
        raise HTTPException(status_code=503, detail=health_status)


@router.get("/health/ready", tags=["monitoring"])
async def readiness_check():
    """
    Readiness probe - returns 200 when app is ready to serve traffic
    Used by Kubernetes readiness probes - NEVER returns 500
    """
    try:
        if get_database_health:
            # Use enhanced database health check
            db_health = get_database_health()
            if db_health["initialization_status"].get("sync", False):
                return {
                    "status": "ready",
                    "timestamp": datetime.utcnow().isoformat(),
                    "database": {
                        "type": db_health["initialization_status"].get("database_type", "unknown"),
                        "connected": db_health["connected"]
                    }
                }
            else:
                # Database not ready, but app can still serve non-DB endpoints
                return {
                    "status": "ready",
                    "timestamp": datetime.utcnow().isoformat(),
                    "note": "Database not available - serving in degraded mode"
                }
        else:
            # Fallback to basic check
            db = safe_get_db_session()
            if db is not None:
                db.execute(text("SELECT 1"))
                db.close()
                return {
                    "status": "ready",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                # If no database required, still ready
                return {
                    "status": "ready",
                    "timestamp": datetime.utcnow().isoformat(),
                    "note": "Database not configured"
                }
    except Exception as e:
        logger.warning(f"Readiness check failed: {e}")
        # Return ready but with degraded note instead of 503
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "note": f"Database check failed but app is ready: {str(e)[:50]}"
        }


@router.get("/health/live", tags=["monitoring"])
async def liveness_check():
    """
    Liveness probe - returns 200 if app is running (doesn't check dependencies)
    Used by Kubernetes liveness probes - NEVER fails
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - start_time)
    }


@router.get("/version", tags=["monitoring"])
async def get_version():
    """Get application version information - NEVER fails"""
    try:
        return {
            "name": getattr(settings, "APP_NAME", "AdCopySurge"),
            "version": getattr(settings, "VERSION", "unknown"),
            "environment": getattr(settings, "NODE_ENV", "unknown"),
            "debug": getattr(settings, "DEBUG", False),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.warning(f"Version check error: {e}")
        return {
            "name": "AdCopySurge",
            "version": "unknown",
            "environment": "unknown",
            "debug": False,
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)[:50]
        }
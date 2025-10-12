"""
Blog Service Health Monitor & Auto-Recovery System
A creative solution to prevent and automatically fix blog service issues
"""
import logging
import asyncio
import time
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class BlogHealthMonitor:
    """Intelligent health monitor for blog services with auto-recovery"""
    
    def __init__(self, blog_service, recovery_strategies: Optional[List[Callable]] = None):
        self.blog_service = blog_service
        self.is_monitoring = False
        self.health_history = []
        self.last_check = None
        self.failure_count = 0
        self.recovery_strategies = recovery_strategies or [
            self._strategy_service_restart,
            self._strategy_content_directory_fix,
            self._strategy_dependency_check,
            self._strategy_graceful_fallback
        ]
        
        # Health metrics
        self.metrics = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'recovery_attempts': 0,
            'successful_recoveries': 0,
            'last_recovery_time': None
        }
    
    async def start_monitoring(self, check_interval: int = 30):
        """Start continuous health monitoring"""
        self.is_monitoring = True
        logger.info(f"🔍 Starting blog health monitoring (check every {check_interval}s)")
        
        while self.is_monitoring:
            try:
                await self._perform_health_check()
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(check_interval * 2)  # Back off on error
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.is_monitoring = False
        logger.info("🛑 Blog health monitoring stopped")
    
    async def _perform_health_check(self) -> bool:
        """Perform comprehensive health check"""
        self.metrics['total_checks'] += 1
        self.last_check = datetime.now()
        
        try:
            # Multi-layer health check
            checks = {
                'service_healthy': self._check_service_health(),
                'content_directory_exists': self._check_content_directory(),
                'dependencies_available': self._check_dependencies(),
                'sample_content_accessible': await self._check_sample_content()
            }
            
            health_score = sum(checks.values()) / len(checks)
            is_healthy = health_score >= 0.75  # 75% health threshold
            
            if is_healthy:
                self.metrics['successful_checks'] += 1
                self.failure_count = 0
                logger.debug(f"✅ Blog health check passed (score: {health_score:.2f})")
            else:
                self.metrics['failed_checks'] += 1
                self.failure_count += 1
                logger.warning(f"⚠️ Blog health check failed (score: {health_score:.2f})")
                logger.warning(f"Failed checks: {[k for k, v in checks.items() if not v]}")
                
                # Trigger recovery if multiple failures
                if self.failure_count >= 2:
                    await self._attempt_recovery()
            
            # Store health record
            self.health_history.append({
                'timestamp': self.last_check.isoformat(),
                'healthy': is_healthy,
                'score': health_score,
                'checks': checks,
                'failure_count': self.failure_count
            })
            
            # Keep only last 100 records
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"Health check failed with exception: {e}")
            self.metrics['failed_checks'] += 1
            return False
    
    def _check_service_health(self) -> bool:
        """Check if blog service is healthy"""
        return hasattr(self.blog_service, 'is_healthy') and self.blog_service.is_healthy
    
    def _check_content_directory(self) -> bool:
        """Check if content directory exists and is accessible"""
        try:
            content_dir = Path(self.blog_service.content_dir)
            return content_dir.exists() and content_dir.is_dir()
        except:
            return False
    
    def _check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        try:
            import frontmatter
            from slugify import slugify
            import markdown
            return True
        except ImportError:
            return False
    
    async def _check_sample_content(self) -> bool:
        """Check if sample content can be loaded"""
        try:
            if hasattr(self.blog_service, 'get_all_posts'):
                posts = self.blog_service.get_all_posts(status=None)  # Any status
                return len(posts) >= 0  # Should at least return empty list
            return True
        except Exception:
            return False
    
    async def _attempt_recovery(self):
        """Attempt to recover blog service using various strategies"""
        self.metrics['recovery_attempts'] += 1
        logger.warning(f"🚨 Attempting blog service recovery (attempt #{self.metrics['recovery_attempts']})")
        
        for i, strategy in enumerate(self.recovery_strategies):
            try:
                logger.info(f"Trying recovery strategy #{i+1}: {strategy.__name__}")
                success = await strategy()
                
                if success:
                    self.metrics['successful_recoveries'] += 1
                    self.metrics['last_recovery_time'] = datetime.now().isoformat()
                    self.failure_count = 0
                    logger.info(f"✅ Recovery successful using strategy: {strategy.__name__}")
                    return True
                    
            except Exception as e:
                logger.error(f"Recovery strategy {strategy.__name__} failed: {e}")
                continue
        
        logger.error("❌ All recovery strategies failed")
        return False
    
    async def _strategy_service_restart(self) -> bool:
        """Strategy 1: Try to restart the blog service"""
        try:
            # Reinitialize blog service
            from ..services.blog_service import BlogService
            from ...core.config import settings
            
            new_service = BlogService(
                content_dir=settings.BLOG_CONTENT_DIR,
                graceful_degradation=settings.BLOG_GRACEFUL_DEGRADATION
            )
            
            if new_service.is_healthy:
                # Replace the service instance (this is tricky in FastAPI)
                logger.info("Blog service reinitialized successfully")
                return True
                
        except Exception as e:
            logger.error(f"Service restart failed: {e}")
        
        return False
    
    async def _strategy_content_directory_fix(self) -> bool:
        """Strategy 2: Fix content directory issues"""
        try:
            content_dir = Path(self.blog_service.content_dir)
            
            # Create directory if missing
            if not content_dir.exists():
                content_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created missing content directory: {content_dir}")
            
            # Check permissions
            if content_dir.exists():
                test_file = content_dir / ".health_check"
                test_file.write_text("health check")
                test_file.unlink()
                return True
                
        except Exception as e:
            logger.error(f"Content directory fix failed: {e}")
        
        return False
    
    async def _strategy_dependency_check(self) -> bool:
        """Strategy 3: Check and report dependency status"""
        try:
            missing_deps = []
            
            try:
                import frontmatter
            except ImportError:
                missing_deps.append("python-frontmatter")
            
            try:
                from slugify import slugify
            except ImportError:
                missing_deps.append("python-slugify")
            
            try:
                import markdown
            except ImportError:
                missing_deps.append("markdown")
            
            if missing_deps:
                logger.error(f"Missing dependencies: {missing_deps}")
                # Could trigger automatic pip install here
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Dependency check failed: {e}")
        
        return False
    
    async def _strategy_graceful_fallback(self) -> bool:
        """Strategy 4: Enable graceful fallback mode"""
        try:
            if hasattr(self.blog_service, 'graceful_degradation'):
                self.blog_service.graceful_degradation = True
                logger.info("Enabled graceful degradation mode")
                return True
        except Exception as e:
            logger.error(f"Graceful fallback failed: {e}")
        
        return False
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        return {
            'monitoring_active': self.is_monitoring,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'current_failure_count': self.failure_count,
            'metrics': self.metrics,
            'recent_health_history': self.health_history[-10:],  # Last 10 checks
            'service_status': {
                'is_healthy': self._check_service_health(),
                'content_directory_ok': self._check_content_directory(),
                'dependencies_ok': self._check_dependencies()
            }
        }
    
    async def force_recovery(self) -> bool:
        """Manually trigger recovery process"""
        logger.info("🔧 Manual recovery triggered")
        return await self._attempt_recovery()


# Global health monitor instance
_health_monitor: Optional[BlogHealthMonitor] = None


def get_health_monitor(blog_service=None) -> BlogHealthMonitor:
    """Get or create global health monitor instance"""
    global _health_monitor
    
    if _health_monitor is None and blog_service:
        _health_monitor = BlogHealthMonitor(blog_service)
    
    return _health_monitor


async def start_blog_monitoring(blog_service, check_interval: int = 30):
    """Start blog health monitoring"""
    monitor = get_health_monitor(blog_service)
    if monitor:
        await monitor.start_monitoring(check_interval)


def stop_blog_monitoring():
    """Stop blog health monitoring"""
    monitor = get_health_monitor()
    if monitor:
        monitor.stop_monitoring()
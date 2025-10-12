"""
Auto-Restart and Server Health Service
The ultimate solution for preventing blog service issues
"""
import asyncio
import subprocess
import psutil
import logging
import signal
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import json

logger = logging.getLogger(__name__)


class AutoRestartService:
    """
    Intelligent service for monitoring and restarting the blog service
    when critical issues are detected
    """
    
    def __init__(self, 
                 process_name: str = "python", 
                 script_path: str = None,
                 max_restarts_per_hour: int = 3,
                 health_check_interval: int = 60):
        
        self.process_name = process_name
        self.script_path = script_path or self._detect_main_script()
        self.max_restarts_per_hour = max_restarts_per_hour
        self.health_check_interval = health_check_interval
        
        self.restart_history = []
        self.is_monitoring = False
        self.last_health_check = None
        self.critical_failure_count = 0
        
        # Health thresholds
        self.thresholds = {
            'memory_mb': 2048,      # 2GB memory limit
            'cpu_percent': 80,       # 80% CPU usage
            'response_time_ms': 5000, # 5 second response time
            'error_rate_percent': 10  # 10% error rate
        }
        
        self.health_callbacks = []
    
    def _detect_main_script(self) -> str:
        """Auto-detect the main script path"""
        possible_paths = [
            "main.py",
            "app.py",
            "server.py",
            "manage.py",
            "main_launch_ready.py"
        ]
        
        for path_str in possible_paths:
            path = Path(path_str)
            if path.exists():
                return str(path.absolute())
        
        return str(Path("main.py").absolute())
    
    def add_health_callback(self, callback: Callable):
        """Add a callback for health status changes"""
        self.health_callbacks.append(callback)
    
    async def start_monitoring(self):
        """Start the monitoring service"""
        self.is_monitoring = True
        logger.info(f"🛡️ Starting auto-restart monitoring for {self.script_path}")
        
        while self.is_monitoring:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(self.health_check_interval * 2)
    
    def stop_monitoring(self):
        """Stop the monitoring service"""
        self.is_monitoring = False
        logger.info("🛑 Auto-restart monitoring stopped")
    
    async def _perform_health_check(self) -> Dict[str, any]:
        """Perform comprehensive health check"""
        self.last_health_check = datetime.now()
        
        health_status = {
            'timestamp': self.last_health_check.isoformat(),
            'healthy': True,
            'issues': [],
            'metrics': {}
        }
        
        try:
            # Check process existence and resources
            process = self._get_main_process()
            
            if not process:
                health_status['healthy'] = False
                health_status['issues'].append('Process not found')
                logger.warning("⚠️ Main process not found!")
                await self._handle_process_failure()
                return health_status
            
            # Check memory usage
            memory_mb = process.memory_info().rss / (1024 * 1024)
            health_status['metrics']['memory_mb'] = memory_mb
            
            if memory_mb > self.thresholds['memory_mb']:
                health_status['healthy'] = False
                health_status['issues'].append(f'High memory usage: {memory_mb:.1f}MB')
            
            # Check CPU usage
            cpu_percent = process.cpu_percent(interval=1)
            health_status['metrics']['cpu_percent'] = cpu_percent
            
            if cpu_percent > self.thresholds['cpu_percent']:
                health_status['healthy'] = False
                health_status['issues'].append(f'High CPU usage: {cpu_percent:.1f}%')
            
            # Check if process is responding (try HTTP health endpoint)
            response_time = await self._check_http_health()
            health_status['metrics']['response_time_ms'] = response_time
            
            if response_time > self.thresholds['response_time_ms']:
                health_status['healthy'] = False
                health_status['issues'].append(f'Slow response time: {response_time}ms')
            
            # Update failure count
            if not health_status['healthy']:
                self.critical_failure_count += 1
                logger.warning(f"❌ Health check failed (failure #{self.critical_failure_count}): {health_status['issues']}")
                
                # Trigger restart if too many failures
                if self.critical_failure_count >= 3:
                    await self._trigger_restart("Multiple health check failures")
            else:
                self.critical_failure_count = 0
                logger.debug("✅ Health check passed")
            
            # Notify callbacks
            for callback in self.health_callbacks:
                try:
                    await callback(health_status)
                except Exception as e:
                    logger.error(f"Health callback error: {e}")
            
        except Exception as e:
            logger.error(f"Health check exception: {e}")
            health_status['healthy'] = False
            health_status['issues'].append(f'Check failed: {str(e)}')
        
        return health_status
    
    def _get_main_process(self) -> Optional[psutil.Process]:
        """Find the main application process"""
        try:
            current_pid = os.getpid()
            
            # Look for processes running our script
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == self.process_name:
                        cmdline = proc.info['cmdline'] or []
                        if any(self.script_path in arg for arg in cmdline):
                            return proc
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Fallback: return current process
            return psutil.Process(current_pid)
            
        except Exception as e:
            logger.error(f"Error finding main process: {e}")
            return None
    
    async def _check_http_health(self) -> int:
        """Check HTTP health endpoint response time"""
        try:
            import aiohttp
            import time
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8000/api/blog/health', timeout=10) as response:
                    await response.text()
                    response_time = (time.time() - start_time) * 1000
                    return int(response_time)
                    
        except Exception as e:
            logger.debug(f"HTTP health check failed: {e}")
            return 999999  # Very high response time indicates failure
    
    async def _handle_process_failure(self):
        """Handle when the main process is not found"""
        logger.error("🚨 Main process failure detected!")
        await self._trigger_restart("Process not found")
    
    async def _trigger_restart(self, reason: str):
        """Trigger a restart of the service"""
        
        # Check restart limits
        current_time = datetime.now()
        recent_restarts = [r for r in self.restart_history 
                          if current_time - datetime.fromisoformat(r['timestamp']) < timedelta(hours=1)]
        
        if len(recent_restarts) >= self.max_restarts_per_hour:
            logger.error(f"❌ Restart limit exceeded ({self.max_restarts_per_hour}/hour). Manual intervention required.")
            return False
        
        # Record the restart
        restart_record = {
            'timestamp': current_time.isoformat(),
            'reason': reason,
            'method': 'auto'
        }
        
        self.restart_history.append(restart_record)
        logger.warning(f"🔄 Triggering restart: {reason}")
        
        try:
            # Try graceful restart first
            success = await self._graceful_restart()
            
            if not success:
                # Try forceful restart
                logger.warning("Graceful restart failed, trying forceful restart")
                success = await self._forceful_restart()
            
            restart_record['success'] = success
            restart_record['completed_at'] = datetime.now().isoformat()
            
            if success:
                logger.info("✅ Restart completed successfully")
                self.critical_failure_count = 0
            else:
                logger.error("❌ Restart failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Restart failed with exception: {e}")
            restart_record['success'] = False
            restart_record['error'] = str(e)
            return False
    
    async def _graceful_restart(self) -> bool:
        """Attempt a graceful restart"""
        try:
            process = self._get_main_process()
            
            if process:
                logger.info("Sending SIGTERM for graceful shutdown...")
                process.terminate()
                
                # Wait for process to terminate
                for _ in range(10):  # Wait up to 10 seconds
                    if not process.is_running():
                        break
                    await asyncio.sleep(1)
                
                if process.is_running():
                    logger.warning("Process didn't terminate gracefully")
                    return False
            
            # Restart the process
            await self._start_new_process()
            return True
            
        except Exception as e:
            logger.error(f"Graceful restart failed: {e}")
            return False
    
    async def _forceful_restart(self) -> bool:
        """Attempt a forceful restart"""
        try:
            process = self._get_main_process()
            
            if process:
                logger.warning("Sending SIGKILL for forceful shutdown...")
                process.kill()
                await asyncio.sleep(2)
            
            # Restart the process
            await self._start_new_process()
            return True
            
        except Exception as e:
            logger.error(f"Forceful restart failed: {e}")
            return False
    
    async def _start_new_process(self):
        """Start a new instance of the main process"""
        try:
            cmd = [sys.executable, self.script_path]
            logger.info(f"Starting new process: {' '.join(cmd)}")
            
            # Start the process in background
            subprocess.Popen(cmd, 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           cwd=str(Path(self.script_path).parent))
            
            # Wait a moment for startup
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Failed to start new process: {e}")
            raise
    
    def get_restart_report(self) -> Dict[str, any]:
        """Get comprehensive restart report"""
        current_time = datetime.now()
        
        # Recent restarts (last 24 hours)
        recent_restarts = [r for r in self.restart_history 
                          if current_time - datetime.fromisoformat(r['timestamp']) < timedelta(hours=24)]
        
        return {
            'monitoring_active': self.is_monitoring,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'critical_failure_count': self.critical_failure_count,
            'total_restarts': len(self.restart_history),
            'recent_restarts_24h': len(recent_restarts),
            'restart_limit_per_hour': self.max_restarts_per_hour,
            'thresholds': self.thresholds,
            'recent_restart_history': recent_restarts[-5:],  # Last 5 restarts
            'script_path': self.script_path
        }
    
    async def manual_restart(self, reason: str = "Manual restart") -> bool:
        """Manually trigger a restart"""
        logger.info(f"🔧 Manual restart requested: {reason}")
        return await self._trigger_restart(reason)


# Global auto-restart service instance
_auto_restart_service: Optional[AutoRestartService] = None


def get_auto_restart_service() -> AutoRestartService:
    """Get or create global auto-restart service instance"""
    global _auto_restart_service
    
    if _auto_restart_service is None:
        _auto_restart_service = AutoRestartService()
    
    return _auto_restart_service


async def start_auto_restart_monitoring():
    """Start auto-restart monitoring"""
    service = get_auto_restart_service()
    await service.start_monitoring()


def stop_auto_restart_monitoring():
    """Stop auto-restart monitoring"""
    service = get_auto_restart_service()
    service.stop_monitoring()
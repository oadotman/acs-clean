#!/usr/bin/env python3
"""
🚀 BLOG RESURRECTION TOOLKIT 🚀
The Ultimate Creative Solution for Blog 404 Issues

This script implements a comprehensive, multi-layered approach to permanently
solve blog service issues through:
1. Intelligent health monitoring
2. Smart fallback routing  
3. Auto-recovery mechanisms
4. Enhanced error handling
5. Performance optimization

Usage:
    python blog_resurrection.py [command]

Commands:
    start       - Start the enhanced blog service (default)
    monitor     - Run health monitoring only
    diagnose    - Run comprehensive diagnostics
    fix         - Apply emergency fixes
    status      - Show current status
"""

import asyncio
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
import json
import subprocess
import time

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.blog.services.health_monitor import get_health_monitor, start_blog_monitoring
from app.blog.services.fallback_router import get_fallback_router
from app.blog.services.auto_restart_service import get_auto_restart_service, start_auto_restart_monitoring
from app.blog.services.blog_service import BlogService
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/blog_resurrection.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)


class BlogResurrectionManager:
    """
    Master controller for the Blog Resurrection Toolkit
    """
    
    def __init__(self):
        self.blog_service = None
        self.health_monitor = None
        self.fallback_router = None
        self.auto_restart_service = None
        self.is_running = False
        
        # Create logs directory
        Path('logs').mkdir(exist_ok=True)
        
    async def initialize_services(self):
        """Initialize all services with error handling"""
        logger.info("🔧 Initializing Blog Resurrection services...")
        
        try:
            # Initialize blog service
            self.blog_service = BlogService(
                content_dir=settings.BLOG_CONTENT_DIR,
                graceful_degradation=settings.BLOG_GRACEFUL_DEGRADATION
            )
            logger.info(f"✅ Blog service initialized (healthy: {self.blog_service.is_healthy})")
            
            # Initialize health monitor
            self.health_monitor = get_health_monitor(self.blog_service)
            logger.info("✅ Health monitor initialized")
            
            # Initialize fallback router
            self.fallback_router = get_fallback_router(self.blog_service)
            logger.info("✅ Fallback router initialized")
            
            # Initialize auto-restart service
            self.auto_restart_service = get_auto_restart_service()
            logger.info("✅ Auto-restart service initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Service initialization failed: {e}")
            return False
    
    async def start_monitoring(self):
        """Start all monitoring services"""
        logger.info("🛡️ Starting comprehensive monitoring...")
        
        tasks = []
        
        # Start health monitoring
        if self.health_monitor:
            task = asyncio.create_task(
                start_blog_monitoring(self.blog_service, check_interval=30)
            )
            tasks.append(task)
            logger.info("📊 Health monitoring started")
        
        # Start auto-restart monitoring
        if self.auto_restart_service:
            task = asyncio.create_task(start_auto_restart_monitoring())
            tasks.append(task)
            logger.info("🔄 Auto-restart monitoring started")
        
        return tasks
    
    async def run_diagnostics(self):
        """Run comprehensive diagnostics"""
        logger.info("🔍 Running comprehensive diagnostics...")
        
        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'health': {},
            'performance': {},
            'recommendations': []
        }
        
        try:
            # Check blog service
            if self.blog_service:
                diagnostics['services']['blog_service'] = {
                    'healthy': self.blog_service.is_healthy,
                    'content_dir': str(self.blog_service.content_dir),
                    'graceful_degradation': self.blog_service.graceful_degradation
                }
            
            # Health check
            if self.health_monitor:
                health_report = self.health_monitor.get_health_report()
                diagnostics['health'] = health_report
            
            # Fallback analytics
            if self.fallback_router:
                fallback_analytics = self.fallback_router.get_analytics_report()
                diagnostics['performance'] = fallback_analytics
            
            # Auto-restart status
            if self.auto_restart_service:
                restart_report = self.auto_restart_service.get_restart_report()
                diagnostics['auto_restart'] = restart_report
            
            # Generate recommendations
            diagnostics['recommendations'] = self._generate_recommendations(diagnostics)
            
            # Save diagnostics report
            report_file = f"logs/diagnostics_{int(time.time())}.json"
            with open(report_file, 'w') as f:
                json.dump(diagnostics, f, indent=2)
            
            logger.info(f"📋 Diagnostics completed. Report saved to: {report_file}")
            return diagnostics
            
        except Exception as e:
            logger.error(f"❌ Diagnostics failed: {e}")
            return None
    
    def _generate_recommendations(self, diagnostics: dict) -> list:
        """Generate recommendations based on diagnostics"""
        recommendations = []
        
        # Check service health
        if not diagnostics.get('services', {}).get('blog_service', {}).get('healthy', True):
            recommendations.append({
                'priority': 'HIGH',
                'issue': 'Blog service unhealthy',
                'action': 'Run manual recovery: python blog_resurrection.py fix'
            })
        
        # Check 404 rate
        total_404s = diagnostics.get('performance', {}).get('total_404_count', 0)
        if total_404s > 50:
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': f'High 404 rate: {total_404s} total 404s',
                'action': 'Review slug redirects and content mapping'
            })
        
        # Check restart frequency
        recent_restarts = diagnostics.get('auto_restart', {}).get('recent_restarts_24h', 0)
        if recent_restarts > 5:
            recommendations.append({
                'priority': 'HIGH',
                'issue': f'Frequent restarts: {recent_restarts} in 24h',
                'action': 'Investigate root cause of service instability'
            })
        
        if not recommendations:
            recommendations.append({
                'priority': 'INFO',
                'issue': 'All systems healthy',
                'action': 'Continue monitoring'
            })
        
        return recommendations
    
    async def apply_emergency_fixes(self):
        """Apply emergency fixes for common issues"""
        logger.info("🚨 Applying emergency fixes...")
        
        fixes_applied = []
        
        try:
            # Fix 1: Ensure content directory exists
            content_dir = Path(settings.BLOG_CONTENT_DIR)
            if not content_dir.exists():
                content_dir.mkdir(parents=True, exist_ok=True)
                fixes_applied.append("Created missing content directory")
                logger.info(f"✅ Created content directory: {content_dir}")
            
            # Fix 2: Clear caches
            if self.fallback_router:
                self.fallback_router.clear_caches()
                fixes_applied.append("Cleared fallback caches")
                logger.info("✅ Cleared fallback router caches")
            
            # Fix 3: Force health recovery
            if self.health_monitor:
                success = await self.health_monitor.force_recovery()
                if success:
                    fixes_applied.append("Health recovery successful")
                    logger.info("✅ Health recovery completed")
                else:
                    fixes_applied.append("Health recovery failed")
                    logger.warning("⚠️ Health recovery failed")
            
            # Fix 4: Add common redirects
            if self.fallback_router:
                common_redirects = [
                    ('blog-post', 'case-study-ecommerce-roas'),
                    ('facebook-ads', 'facebook-ad-copy-secrets'),
                    ('ad-copy', 'facebook-ad-copy-secrets')
                ]
                
                for old_slug, new_slug in common_redirects:
                    try:
                        self.fallback_router.add_redirect(old_slug, new_slug)
                        fixes_applied.append(f"Added redirect: {old_slug} -> {new_slug}")
                    except Exception as e:
                        logger.debug(f"Redirect already exists or failed: {e}")
            
            logger.info(f"🎯 Applied {len(fixes_applied)} emergency fixes:")
            for fix in fixes_applied:
                logger.info(f"   - {fix}")
            
            return fixes_applied
            
        except Exception as e:
            logger.error(f"❌ Emergency fixes failed: {e}")
            return []
    
    async def get_status(self):
        """Get comprehensive system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'overall_health': 'UNKNOWN',
            'services': {},
            'uptime': time.time(),
            'version': '2.0.0-enhanced'
        }
        
        try:
            # Blog service status
            if self.blog_service:
                status['services']['blog_service'] = {
                    'status': 'HEALTHY' if self.blog_service.is_healthy else 'UNHEALTHY',
                    'content_dir': str(self.blog_service.content_dir)
                }
            
            # Health monitor status
            if self.health_monitor:
                health_report = self.health_monitor.get_health_report()
                status['services']['health_monitor'] = {
                    'status': 'ACTIVE' if health_report['monitoring_active'] else 'INACTIVE',
                    'last_check': health_report['last_check']
                }
            
            # Auto-restart status
            if self.auto_restart_service:
                restart_report = self.auto_restart_service.get_restart_report()
                status['services']['auto_restart'] = {
                    'status': 'ACTIVE' if restart_report['monitoring_active'] else 'INACTIVE',
                    'restarts_24h': restart_report['recent_restarts_24h']
                }
            
            # Determine overall health
            all_services = status['services'].values()
            if all(s.get('status') in ['HEALTHY', 'ACTIVE'] for s in all_services):
                status['overall_health'] = 'HEALTHY'
            elif any(s.get('status') == 'UNHEALTHY' for s in all_services):
                status['overall_health'] = 'UNHEALTHY'
            else:
                status['overall_health'] = 'DEGRADED'
            
            return status
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            status['overall_health'] = 'ERROR'
            status['error'] = str(e)
            return status


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Blog Resurrection Toolkit')
    parser.add_argument('command', nargs='?', default='start',
                       choices=['start', 'monitor', 'diagnose', 'fix', 'status'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    # Create manager
    manager = BlogResurrectionManager()
    
    # Initialize services
    if not await manager.initialize_services():
        logger.error("❌ Failed to initialize services. Exiting.")
        return 1
    
    logger.info(f"🚀 Blog Resurrection Toolkit - Command: {args.command}")
    
    try:
        if args.command == 'start':
            logger.info("🎯 Starting enhanced blog service with full monitoring...")
            
            # Start monitoring
            monitoring_tasks = await manager.start_monitoring()
            
            # Keep running
            if monitoring_tasks:
                logger.info("✅ All services started successfully. Monitoring active.")
                logger.info("Press Ctrl+C to stop...")
                
                try:
                    # Wait for all monitoring tasks
                    await asyncio.gather(*monitoring_tasks)
                except KeyboardInterrupt:
                    logger.info("🛑 Stopping services...")
            else:
                logger.warning("⚠️ No monitoring tasks started")
        
        elif args.command == 'monitor':
            logger.info("📊 Starting monitoring services only...")
            monitoring_tasks = await manager.start_monitoring()
            
            if monitoring_tasks:
                try:
                    await asyncio.gather(*monitoring_tasks)
                except KeyboardInterrupt:
                    logger.info("🛑 Monitoring stopped")
        
        elif args.command == 'diagnose':
            logger.info("🔍 Running comprehensive diagnostics...")
            diagnostics = await manager.run_diagnostics()
            
            if diagnostics:
                print(json.dumps(diagnostics, indent=2))
                
                # Print recommendations
                print("\n🎯 RECOMMENDATIONS:")
                for rec in diagnostics.get('recommendations', []):
                    print(f"  [{rec['priority']}] {rec['issue']}")
                    print(f"      Action: {rec['action']}")
                    print()
        
        elif args.command == 'fix':
            logger.info("🚨 Applying emergency fixes...")
            fixes = await manager.apply_emergency_fixes()
            
            print(f"✅ Applied {len(fixes)} fixes:")
            for fix in fixes:
                print(f"  - {fix}")
        
        elif args.command == 'status':
            logger.info("📋 Getting system status...")
            status = await manager.get_status()
            
            print(f"Overall Health: {status['overall_health']}")
            print(f"Timestamp: {status['timestamp']}")
            print("\nServices:")
            for name, service_status in status['services'].items():
                print(f"  {name}: {service_status['status']}")
            
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
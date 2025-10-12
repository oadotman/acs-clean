#!/usr/bin/env python3
"""
AdCopySurge Health Check Script
Monitors the application health and sends alerts if issues are detected
"""

import requests
import time
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import sys

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 minutes
ALERT_EMAIL = os.getenv('ALERT_EMAIL', 'admin@adcopysurge.com')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/adcopysurge/health_check.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self):
        self.last_alert_time = {}
        self.alert_cooldown = 1800  # 30 minutes between alerts
        
    def check_endpoint(self, endpoint, timeout=10):
        """Check if an endpoint is responding"""
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=timeout)
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'content': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'response_time': None
            }
    
    def check_database_health(self):
        """Check database connectivity through API"""
        result = self.check_endpoint('/api/ads/tools/status')
        if result['success']:
            try:
                tools_status = result.get('content', {})
                if isinstance(tools_status, dict):
                    return {
                        'success': True,
                        'tools_available': tools_status.get('tools', {}),
                        'overall_status': tools_status.get('overall_status', 'Unknown')
                    }
            except Exception as e:
                logger.error(f"Error parsing tools status: {e}")
        
        return {'success': False, 'error': 'Unable to check database health'}
    
    def check_system_resources(self):
        """Check system resource usage"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'success': True,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }
        except ImportError:
            return {'success': False, 'error': 'psutil not available'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_alert(self, subject, message):
        """Send email alert"""
        if not all([SMTP_USERNAME, SMTP_PASSWORD, ALERT_EMAIL]):
            logger.warning("Email configuration incomplete, cannot send alerts")
            return False
        
        # Check cooldown
        now = time.time()
        if subject in self.last_alert_time:
            if now - self.last_alert_time[subject] < self.alert_cooldown:
                logger.info(f"Alert '{subject}' is in cooldown, skipping")
                return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USERNAME
            msg['To'] = ALERT_EMAIL
            msg['Subject'] = f"AdCopySurge Alert: {subject}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(SMTP_USERNAME, ALERT_EMAIL, text)
            server.quit()
            
            self.last_alert_time[subject] = now
            logger.info(f"Alert sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False
    
    def run_health_checks(self):
        """Run all health checks"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_healthy': True,
            'checks': {}
        }
        
        # Check main endpoints
        endpoints = [
            ('/', 'Root endpoint'),
            ('/health', 'Health check endpoint'),
            ('/api/ads/tools/status', 'Tools status'),
        ]
        
        for endpoint, description in endpoints:
            result = self.check_endpoint(endpoint)
            results['checks'][endpoint] = {
                'description': description,
                **result
            }
            
            if not result['success']:
                results['overall_healthy'] = False
                self.send_alert(
                    f"Endpoint {endpoint} is down",
                    f"The {description} ({endpoint}) is not responding.\n\n"
                    f"Error: {result.get('error', 'Unknown error')}\n"
                    f"Time: {datetime.now()}\n"
                    f"Please investigate immediately."
                )
        
        # Check database health
        db_health = self.check_database_health()
        results['checks']['database'] = db_health
        if not db_health['success']:
            results['overall_healthy'] = False
            self.send_alert(
                "Database connectivity issues",
                f"Database health check failed.\n\n"
                f"Error: {db_health.get('error', 'Unknown error')}\n"
                f"Time: {datetime.now()}\n"
                f"Please check database connection and API services."
            )
        
        # Check system resources
        resources = self.check_system_resources()
        results['checks']['system_resources'] = resources
        if resources['success']:
            # Alert on high resource usage
            if resources['cpu_percent'] > 80:
                self.send_alert(
                    "High CPU usage",
                    f"CPU usage is at {resources['cpu_percent']:.1f}%\n"
                    f"Time: {datetime.now()}\n"
                    f"Consider scaling up or investigating high CPU processes."
                )
            
            if resources['memory_percent'] > 85:
                self.send_alert(
                    "High memory usage",
                    f"Memory usage is at {resources['memory_percent']:.1f}%\n"
                    f"Available memory: {resources['memory_available_gb']:.2f} GB\n"
                    f"Time: {datetime.now()}\n"
                    f"Consider scaling up or investigating memory leaks."
                )
            
            if resources['disk_percent'] > 90:
                self.send_alert(
                    "Low disk space",
                    f"Disk usage is at {resources['disk_percent']:.1f}%\n"
                    f"Free space: {resources['disk_free_gb']:.2f} GB\n"
                    f"Time: {datetime.now()}\n"
                    f"Please clean up disk space immediately."
                )
        
        return results
    
    def log_results(self, results):
        """Log health check results"""
        if results['overall_healthy']:
            logger.info("✅ All health checks passed")
        else:
            logger.error("❌ Health check failures detected")
        
        for check_name, check_result in results['checks'].items():
            if check_result.get('success'):
                if 'response_time' in check_result:
                    logger.info(f"  {check_name}: OK ({check_result['response_time']:.2f}s)")
                else:
                    logger.info(f"  {check_name}: OK")
            else:
                logger.error(f"  {check_name}: FAILED - {check_result.get('error', 'Unknown error')}")

def main():
    """Main monitoring loop"""
    logger.info("🔍 Starting AdCopySurge health monitoring...")
    checker = HealthChecker()
    
    try:
        while True:
            results = checker.run_health_checks()
            checker.log_results(results)
            
            # Save results to file for external monitoring
            with open('/var/log/adcopysurge/health_status.json', 'w') as f:
                json.dump(results, f, indent=2)
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Health monitoring stopped by user")
    except Exception as e:
        logger.error(f"Health monitoring crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

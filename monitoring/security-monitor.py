#!/usr/bin/env python3
"""
AdCopySurge Security Monitoring System
Comprehensive security monitoring and alerting for the AdCopySurge platform
"""

import os
import json
import time
import logging
import smtplib
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from dataclasses import dataclass
import psutil
import redis
import schedule
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/adcopysurge/security-monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SecurityAlert:
    """Security alert data structure"""
    severity: str  # critical, high, medium, low
    category: str  # auth, ddos, injection, abuse, etc.
    title: str
    description: str
    source_ip: Optional[str] = None
    affected_resource: Optional[str] = None
    timestamp: datetime = None
    additional_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.additional_data is None:
            self.additional_data = {}

class SecurityMonitor:
    """Main security monitoring class"""
    
    def __init__(self, config_path: str = "/etc/adcopysurge/monitoring.conf"):
        self.config = self._load_config(config_path)
        self.redis_client = self._init_redis()
        self.alerts_sent = {}  # Rate limiting for alerts
        self.log_files = {
            'nginx_access': '/var/log/nginx/adcopysurge-api.access.log',
            'nginx_error': '/var/log/nginx/adcopysurge-api.error.log',
            'fail2ban': '/var/log/fail2ban.log',
            'system': '/var/log/syslog',
            'auth': '/var/log/auth.log',
            'app': '/var/log/adcopysurge/app.log'
        }
        
        # Security thresholds
        self.thresholds = {
            'failed_auth_per_minute': 10,
            'requests_per_minute': 1000,
            'error_rate_percent': 5,
            'cpu_usage_percent': 80,
            'memory_usage_percent': 85,
            'disk_usage_percent': 90,
            'response_time_ms': 5000,
            'banned_ips_per_hour': 50
        }
        
        self.start_time = datetime.utcnow()
        self.stats = {
            'alerts_sent': 0,
            'threats_detected': 0,
            'ips_blocked': 0,
            'attacks_prevented': 0
        }

    def _load_config(self, config_path: str) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            'email': {
                'smtp_host': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': os.getenv('SMTP_USERNAME'),
                'password': os.getenv('SMTP_PASSWORD'),
                'from_addr': 'security@adcopysurge.com',
                'to_addrs': ['admin@adcopysurge.com']
            },
            'redis': {
                'url': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            },
            'webhooks': {
                'slack': os.getenv('SLACK_WEBHOOK_URL'),
                'discord': os.getenv('DISCORD_WEBHOOK_URL')
            },
            'monitoring': {
                'check_interval': 60,  # seconds
                'alert_cooldown': 300,  # 5 minutes between same alerts
                'enable_email': True,
                'enable_webhooks': True
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                default_config.update(config)
            return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config

    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection"""
        try:
            client = redis.from_url(self.config['redis']['url'], decode_responses=True)
            client.ping()
            return client
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            return None

    def start_monitoring(self):
        """Start the security monitoring system"""
        logger.info("🔒 Starting AdCopySurge Security Monitor")
        
        # Schedule monitoring tasks
        schedule.every(1).minutes.do(self.check_authentication_failures)
        schedule.every(1).minutes.do(self.check_error_rates)
        schedule.every(2).minutes.do(self.check_system_resources)
        schedule.every(5).minutes.do(self.check_suspicious_activity)
        schedule.every(10).minutes.do(self.check_fail2ban_status)
        schedule.every(30).minutes.do(self.generate_security_report)
        schedule.every().hour.do(self.cleanup_old_data)
        
        # Start background thread for log monitoring
        log_thread = threading.Thread(target=self.monitor_logs_realtime, daemon=True)
        log_thread.start()
        
        # Main monitoring loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Security monitoring stopped by user")
        except Exception as e:
            logger.error(f"Security monitoring error: {e}")

    def monitor_logs_realtime(self):
        """Real-time log monitoring for critical events"""
        logger.info("Starting real-time log monitoring")
        
        # Monitor critical patterns in real-time
        critical_patterns = [
            r'CRITICAL',
            r'SQL injection',
            r'Authentication bypass',
            r'Mass password attempts',
            r'DDoS detected',
            r'System compromise'
        ]
        
        try:
            # Use tail -f equivalent for real-time monitoring
            for log_file in [self.log_files['nginx_error'], self.log_files['app']]:
                if os.path.exists(log_file):
                    threading.Thread(
                        target=self._tail_log_file, 
                        args=(log_file, critical_patterns),
                        daemon=True
                    ).start()
        except Exception as e:
            logger.error(f"Real-time log monitoring error: {e}")

    def _tail_log_file(self, log_file: str, patterns: List[str]):
        """Tail a log file and check for patterns"""
        try:
            process = subprocess.Popen(
                ['tail', '-f', log_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            for line in iter(process.stdout.readline, ''):
                for pattern in patterns:
                    if pattern.lower() in line.lower():
                        self.handle_critical_event(line, log_file, pattern)
                        
        except Exception as e:
            logger.error(f"Error tailing {log_file}: {e}")

    def handle_critical_event(self, log_line: str, source: str, pattern: str):
        """Handle critical security events immediately"""
        alert = SecurityAlert(
            severity="critical",
            category="realtime",
            title=f"Critical Security Event Detected",
            description=f"Pattern '{pattern}' detected in {source}",
            additional_data={
                'log_line': log_line.strip(),
                'source_file': source,
                'detection_time': datetime.utcnow().isoformat()
            }
        )
        
        self.send_alert(alert)

    def check_authentication_failures(self):
        """Monitor authentication failure patterns"""
        try:
            # Check nginx access logs for auth failures
            nginx_log = self.log_files['nginx_access']
            if not os.path.exists(nginx_log):
                return
            
            # Count auth failures in last minute
            one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
            auth_failures = 0
            suspicious_ips = {}
            
            with open(nginx_log, 'r') as f:
                for line in f:
                    if '/api/auth/' in line and ('401' in line or '403' in line):
                        # Extract IP and timestamp (simplified)
                        parts = line.split()
                        if len(parts) >= 4:
                            ip = parts[0]
                            # Parse timestamp (nginx format)
                            auth_failures += 1
                            suspicious_ips[ip] = suspicious_ips.get(ip, 0) + 1
            
            # Check thresholds
            if auth_failures > self.thresholds['failed_auth_per_minute']:
                alert = SecurityAlert(
                    severity="high",
                    category="authentication",
                    title="High Authentication Failure Rate",
                    description=f"{auth_failures} authentication failures detected in the last minute",
                    additional_data={
                        'failure_count': auth_failures,
                        'suspicious_ips': suspicious_ips,
                        'threshold': self.thresholds['failed_auth_per_minute']
                    }
                )
                self.send_alert(alert)
                
            # Check for specific IPs with high failure rates
            for ip, count in suspicious_ips.items():
                if count >= 5:  # 5+ failures from single IP
                    alert = SecurityAlert(
                        severity="medium",
                        category="brute_force",
                        title="Potential Brute Force Attack",
                        description=f"IP {ip} has {count} authentication failures",
                        source_ip=ip,
                        additional_data={'failure_count': count}
                    )
                    self.send_alert(alert)
                    
        except Exception as e:
            logger.error(f"Error checking authentication failures: {e}")

    def check_error_rates(self):
        """Monitor application error rates"""
        try:
            nginx_log = self.log_files['nginx_access']
            if not os.path.exists(nginx_log):
                return
                
            # Count requests and errors in last 5 minutes
            total_requests = 0
            error_requests = 0
            
            # Simplified log parsing - in production, use proper log parsing
            with open(nginx_log, 'r') as f:
                lines = f.readlines()[-1000:]  # Last 1000 lines
                
            for line in lines:
                if '/api/' in line:
                    total_requests += 1
                    # Check for error status codes
                    if any(code in line for code in ['4', '5']):
                        if any(code in line for code in ['40', '50']):
                            error_requests += 1
            
            if total_requests > 0:
                error_rate = (error_requests / total_requests) * 100
                
                if error_rate > self.thresholds['error_rate_percent']:
                    alert = SecurityAlert(
                        severity="medium",
                        category="performance",
                        title="High Error Rate Detected",
                        description=f"Error rate: {error_rate:.2f}% ({error_requests}/{total_requests})",
                        additional_data={
                            'error_rate': error_rate,
                            'total_requests': total_requests,
                            'error_requests': error_requests
                        }
                    )
                    self.send_alert(alert)
                    
        except Exception as e:
            logger.error(f"Error checking error rates: {e}")

    def check_system_resources(self):
        """Monitor system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.thresholds['cpu_usage_percent']:
                alert = SecurityAlert(
                    severity="medium",
                    category="system",
                    title="High CPU Usage",
                    description=f"CPU usage: {cpu_percent}%",
                    additional_data={'cpu_usage': cpu_percent}
                )
                self.send_alert(alert)
            
            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.thresholds['memory_usage_percent']:
                alert = SecurityAlert(
                    severity="medium",
                    category="system", 
                    title="High Memory Usage",
                    description=f"Memory usage: {memory.percent}%",
                    additional_data={
                        'memory_percent': memory.percent,
                        'memory_available': memory.available,
                        'memory_total': memory.total
                    }
                )
                self.send_alert(alert)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > self.thresholds['disk_usage_percent']:
                alert = SecurityAlert(
                    severity="high",
                    category="system",
                    title="High Disk Usage",
                    description=f"Disk usage: {disk_percent:.1f}%",
                    additional_data={
                        'disk_percent': disk_percent,
                        'disk_free': disk.free,
                        'disk_total': disk.total
                    }
                )
                self.send_alert(alert)
                
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")

    def check_suspicious_activity(self):
        """Monitor for suspicious activity patterns"""
        try:
            # Check for unusual request patterns
            nginx_log = self.log_files['nginx_access']
            if not os.path.exists(nginx_log):
                return
            
            # Look for scanning/reconnaissance patterns
            suspicious_patterns = [
                '.php', '.asp', '.aspx', 'wp-admin', 'phpmyadmin',
                'admin', '/../', '.env', 'config.php', '.git',
                'backup', '.sql', '.bak'
            ]
            
            suspicious_requests = []
            
            with open(nginx_log, 'r') as f:
                lines = f.readlines()[-500:]  # Last 500 lines
            
            for line in lines:
                for pattern in suspicious_patterns:
                    if pattern in line:
                        # Extract IP
                        ip = line.split()[0] if line.split() else 'unknown'
                        suspicious_requests.append({
                            'ip': ip,
                            'pattern': pattern,
                            'line': line.strip()
                        })
            
            if len(suspicious_requests) >= 5:
                # Group by IP
                ip_counts = {}
                for req in suspicious_requests:
                    ip = req['ip']
                    ip_counts[ip] = ip_counts.get(ip, 0) + 1
                
                for ip, count in ip_counts.items():
                    if count >= 3:
                        alert = SecurityAlert(
                            severity="high",
                            category="reconnaissance",
                            title="Reconnaissance Activity Detected",
                            description=f"IP {ip} made {count} suspicious requests",
                            source_ip=ip,
                            additional_data={
                                'suspicious_requests': count,
                                'patterns': [req['pattern'] for req in suspicious_requests if req['ip'] == ip]
                            }
                        )
                        self.send_alert(alert)
                        
        except Exception as e:
            logger.error(f"Error checking suspicious activity: {e}")

    def check_fail2ban_status(self):
        """Monitor fail2ban status and banned IPs"""
        try:
            # Get fail2ban status
            result = subprocess.run(
                ['fail2ban-client', 'status'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse output for jail status
                jails = []
                for line in result.stdout.split('\n'):
                    if 'Jail list:' in line:
                        jails_str = line.split('Jail list:')[1].strip()
                        jails = [j.strip() for j in jails_str.split(',') if j.strip()]
                
                # Check each jail
                total_banned = 0
                jail_status = {}
                
                for jail in jails:
                    jail_result = subprocess.run(
                        ['fail2ban-client', 'status', jail],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if jail_result.returncode == 0:
                        # Parse banned IPs count
                        for line in jail_result.stdout.split('\n'):
                            if 'Currently banned:' in line:
                                banned_count = int(line.split(':')[1].strip())
                                total_banned += banned_count
                                jail_status[jail] = banned_count
                
                # Store in Redis if available
                if self.redis_client:
                    self.redis_client.setex(
                        'fail2ban:status',
                        3600,
                        json.dumps({
                            'total_banned': total_banned,
                            'jails': jail_status,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    )
                
                # Check for high ban activity
                if total_banned > self.thresholds['banned_ips_per_hour']:
                    alert = SecurityAlert(
                        severity="medium",
                        category="fail2ban",
                        title="High IP Ban Activity",
                        description=f"fail2ban has banned {total_banned} IPs",
                        additional_data={
                            'total_banned': total_banned,
                            'jail_status': jail_status
                        }
                    )
                    self.send_alert(alert)
                    
        except Exception as e:
            logger.error(f"Error checking fail2ban status: {e}")

    def send_alert(self, alert: SecurityAlert):
        """Send security alert via configured channels"""
        # Rate limiting - don't spam same alerts
        alert_key = f"{alert.category}_{alert.title}"
        last_sent = self.alerts_sent.get(alert_key, 0)
        cooldown = self.config['monitoring']['alert_cooldown']
        
        if time.time() - last_sent < cooldown:
            return  # Skip - too soon since last alert
        
        self.alerts_sent[alert_key] = time.time()
        self.stats['alerts_sent'] += 1
        
        logger.warning(f"🚨 SECURITY ALERT: [{alert.severity.upper()}] {alert.title}")
        
        # Send email alert
        if self.config['monitoring']['enable_email']:
            self._send_email_alert(alert)
        
        # Send webhook alerts
        if self.config['monitoring']['enable_webhooks']:
            self._send_webhook_alert(alert)
        
        # Store in Redis for dashboard
        if self.redis_client:
            self.redis_client.lpush(
                'security:alerts',
                json.dumps({
                    'severity': alert.severity,
                    'category': alert.category,
                    'title': alert.title,
                    'description': alert.description,
                    'source_ip': alert.source_ip,
                    'timestamp': alert.timestamp.isoformat(),
                    'additional_data': alert.additional_data
                })
            )
            # Keep only last 1000 alerts
            self.redis_client.ltrim('security:alerts', 0, 999)

    def _send_email_alert(self, alert: SecurityAlert):
        """Send email alert"""
        try:
            email_config = self.config['email']
            if not all([email_config['username'], email_config['password']]):
                return
            
            msg = MimeMultipart()
            msg['From'] = email_config['from_addr']
            msg['To'] = ', '.join(email_config['to_addrs'])
            msg['Subject'] = f"🚨 AdCopySurge Security Alert: {alert.title}"
            
            # Create HTML email body
            html_body = f"""
            <html>
            <body>
            <h2>🔒 AdCopySurge Security Alert</h2>
            <p><strong>Severity:</strong> <span style="color: {'red' if alert.severity == 'critical' else 'orange' if alert.severity == 'high' else 'blue'};">{alert.severity.upper()}</span></p>
            <p><strong>Category:</strong> {alert.category}</p>
            <p><strong>Title:</strong> {alert.title}</p>
            <p><strong>Description:</strong> {alert.description}</p>
            <p><strong>Time:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            {f'<p><strong>Source IP:</strong> {alert.source_ip}</p>' if alert.source_ip else ''}
            {f'<p><strong>Affected Resource:</strong> {alert.affected_resource}</p>' if alert.affected_resource else ''}
            
            {f'<h3>Additional Details:</h3><pre>{json.dumps(alert.additional_data, indent=2)}</pre>' if alert.additional_data else ''}
            
            <hr>
            <p><small>AdCopySurge Security Monitor | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</small></p>
            </body>
            </html>
            """
            
            msg.attach(MimeText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(email_config['smtp_host'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
                
            logger.info(f"Email alert sent for: {alert.title}")
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")

    def _send_webhook_alert(self, alert: SecurityAlert):
        """Send webhook alerts (Slack, Discord, etc.)"""
        try:
            webhooks = self.config['webhooks']
            
            # Prepare webhook payload
            webhook_data = {
                'text': f"🚨 AdCopySurge Security Alert",
                'attachments': [
                    {
                        'color': 'danger' if alert.severity in ['critical', 'high'] else 'warning',
                        'title': alert.title,
                        'text': alert.description,
                        'fields': [
                            {'title': 'Severity', 'value': alert.severity.upper(), 'short': True},
                            {'title': 'Category', 'value': alert.category, 'short': True},
                            {'title': 'Time', 'value': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'), 'short': True}
                        ]
                    }
                ]
            }
            
            if alert.source_ip:
                webhook_data['attachments'][0]['fields'].append({
                    'title': 'Source IP', 'value': alert.source_ip, 'short': True
                })
            
            # Send to Slack
            if webhooks.get('slack'):
                response = requests.post(webhooks['slack'], json=webhook_data, timeout=10)
                response.raise_for_status()
                logger.info(f"Slack alert sent for: {alert.title}")
            
            # Send to Discord  
            if webhooks.get('discord'):
                discord_data = {
                    'content': f"🚨 **AdCopySurge Security Alert**",
                    'embeds': [
                        {
                            'title': alert.title,
                            'description': alert.description,
                            'color': 16711680 if alert.severity in ['critical', 'high'] else 16776960,
                            'fields': [
                                {'name': 'Severity', 'value': alert.severity.upper(), 'inline': True},
                                {'name': 'Category', 'value': alert.category, 'inline': True},
                                {'name': 'Time', 'value': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'), 'inline': True}
                            ]
                        }
                    ]
                }
                
                if alert.source_ip:
                    discord_data['embeds'][0]['fields'].append({
                        'name': 'Source IP', 'value': alert.source_ip, 'inline': True
                    })
                
                response = requests.post(webhooks['discord'], json=discord_data, timeout=10)
                response.raise_for_status()
                logger.info(f"Discord alert sent for: {alert.title}")
                
        except Exception as e:
            logger.error(f"Error sending webhook alert: {e}")

    def generate_security_report(self):
        """Generate periodic security report"""
        try:
            uptime = datetime.utcnow() - self.start_time
            
            report = {
                'timestamp': datetime.utcnow().isoformat(),
                'uptime_hours': uptime.total_seconds() / 3600,
                'statistics': self.stats.copy(),
                'system_status': {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
                }
            }
            
            # Add fail2ban status if available
            if self.redis_client:
                fail2ban_status = self.redis_client.get('fail2ban:status')
                if fail2ban_status:
                    report['fail2ban_status'] = json.loads(fail2ban_status)
            
            # Store report
            if self.redis_client:
                self.redis_client.setex(
                    'security:report:latest',
                    3600,
                    json.dumps(report)
                )
            
            logger.info(f"Security report generated - Alerts: {self.stats['alerts_sent']}, Uptime: {uptime}")
            
        except Exception as e:
            logger.error(f"Error generating security report: {e}")

    def cleanup_old_data(self):
        """Clean up old monitoring data"""
        try:
            if self.redis_client:
                # Clean up old alerts (keep last 7 days)
                seven_days_ago = datetime.utcnow() - timedelta(days=7)
                
                # This is a simplified cleanup - in production, implement proper timestamp-based cleanup
                self.redis_client.ltrim('security:alerts', 0, 1000)
                
            logger.info("Old monitoring data cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")


def main():
    """Main entry point"""
    monitor = SecurityMonitor()
    monitor.start_monitoring()


if __name__ == "__main__":
    main()
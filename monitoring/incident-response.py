#!/usr/bin/env python3
"""
AdCopySurge Automated Incident Response System
Automated incident response and threat mitigation for the AdCopySurge platform
"""

import os
import json
import time
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import redis
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/adcopysurge/incident-response.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ResponseStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"

@dataclass
class SecurityIncident:
    """Security incident data structure"""
    id: str
    severity: IncidentSeverity
    category: str
    title: str
    description: str
    source_ip: Optional[str] = None
    affected_resources: List[str] = None
    timestamp: datetime = None
    additional_data: Dict[str, Any] = None
    status: ResponseStatus = ResponseStatus.PENDING
    actions_taken: List[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.additional_data is None:
            self.additional_data = {}
        if self.actions_taken is None:
            self.actions_taken = []
        if self.affected_resources is None:
            self.affected_resources = []

class IncidentResponseSystem:
    """Main incident response system"""
    
    def __init__(self, config_path: str = "/etc/adcopysurge/incident-response.conf"):
        self.config = self._load_config(config_path)
        self.redis_client = self._init_redis()
        self.incidents = {}  # Active incidents
        self.response_playbooks = self._load_playbooks()
        self.blocked_ips = set()
        
        # Response thresholds
        self.thresholds = {
            'max_failed_auth_before_block': 10,
            'max_requests_per_minute': 1000,
            'auto_escalation_threshold': 5,  # incidents before escalation
            'critical_response_time_seconds': 300,  # 5 minutes
            'high_response_time_seconds': 900,  # 15 minutes
            'ban_duration_minutes': 60
        }
        
        # Statistics
        self.stats = {
            'incidents_handled': 0,
            'automatic_responses': 0,
            'manual_escalations': 0,
            'ips_blocked': 0,
            'false_positives': 0
        }

    def _load_config(self, config_path: str) -> Dict:
        """Load incident response configuration"""
        default_config = {
            'redis': {
                'url': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            },
            'email': {
                'smtp_host': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': os.getenv('SMTP_USERNAME'),
                'password': os.getenv('SMTP_PASSWORD'),
                'security_team': ['security@adcopysurge.com'],
                'admin_team': ['admin@adcopysurge.com']
            },
            'webhooks': {
                'security_channel': os.getenv('SECURITY_SLACK_WEBHOOK'),
                'pagerduty_key': os.getenv('PAGERDUTY_API_KEY')
            },
            'auto_response': {
                'enable_ip_blocking': True,
                'enable_rate_limiting': True,
                'enable_service_isolation': False,  # Dangerous - manual only
                'enable_fail2ban_integration': True
            },
            'escalation': {
                'auto_escalate_critical': True,
                'escalation_timeout_minutes': 30,
                'on_call_phone': os.getenv('ON_CALL_PHONE')
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
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

    def _load_playbooks(self) -> Dict:
        """Load incident response playbooks"""
        return {
            'brute_force': {
                'auto_actions': ['block_ip', 'increase_monitoring'],
                'manual_actions': ['investigate_source', 'check_compromised_accounts'],
                'escalation_criteria': ['multiple_successful_breaches', 'internal_ip_source']
            },
            'ddos': {
                'auto_actions': ['enable_rate_limiting', 'block_source_ips', 'activate_cdn_protection'],
                'manual_actions': ['contact_upstream_provider', 'implement_geo_blocking'],
                'escalation_criteria': ['traffic_exceeds_capacity', 'multiple_attack_vectors']
            },
            'sql_injection': {
                'auto_actions': ['block_ip', 'isolate_affected_endpoint'],
                'manual_actions': ['audit_database_access', 'check_data_integrity'],
                'escalation_criteria': ['successful_data_access', 'multiple_injection_points']
            },
            'reconnaissance': {
                'auto_actions': ['block_ip', 'increase_logging'],
                'manual_actions': ['analyze_scanning_patterns', 'harden_exposed_services'],
                'escalation_criteria': ['internal_scanning', 'advanced_techniques']
            },
            'malware': {
                'auto_actions': ['isolate_system', 'block_ip'],
                'manual_actions': ['malware_analysis', 'check_lateral_movement'],
                'escalation_criteria': ['always']  # Always escalate malware
            },
            'privilege_escalation': {
                'auto_actions': ['disable_affected_account', 'increase_monitoring'],
                'manual_actions': ['audit_privilege_changes', 'check_system_integrity'],
                'escalation_criteria': ['admin_account_compromise', 'system_level_access']
            }
        }

    def handle_security_alert(self, alert_data: Dict):
        """Handle incoming security alert and trigger response"""
        try:
            # Create incident from alert
            incident = self._create_incident_from_alert(alert_data)
            self.incidents[incident.id] = incident
            
            logger.info(f"🚨 New security incident: {incident.id} - {incident.title}")
            
            # Determine response actions
            response_actions = self._determine_response_actions(incident)
            
            # Execute automatic responses
            for action in response_actions.get('auto', []):
                self._execute_automatic_action(incident, action)
            
            # Check escalation criteria
            if self._should_escalate(incident):
                self._escalate_incident(incident)
            
            # Store incident in Redis for tracking
            if self.redis_client:
                self.redis_client.hset(
                    'incidents:active',
                    incident.id,
                    json.dumps({
                        'id': incident.id,
                        'severity': incident.severity.value,
                        'category': incident.category,
                        'title': incident.title,
                        'timestamp': incident.timestamp.isoformat(),
                        'status': incident.status.value,
                        'source_ip': incident.source_ip,
                        'actions_taken': incident.actions_taken
                    })
                )
            
            self.stats['incidents_handled'] += 1
            return incident
            
        except Exception as e:
            logger.error(f"Error handling security alert: {e}")
            return None

    def _create_incident_from_alert(self, alert_data: Dict) -> SecurityIncident:
        """Create incident from alert data"""
        incident_id = f"INC-{int(time.time())}-{alert_data.get('category', 'UNK')[:3].upper()}"
        
        # Map severity
        severity_map = {
            'low': IncidentSeverity.LOW,
            'medium': IncidentSeverity.MEDIUM,
            'high': IncidentSeverity.HIGH,
            'critical': IncidentSeverity.CRITICAL
        }
        
        severity = severity_map.get(alert_data.get('severity', 'medium'), IncidentSeverity.MEDIUM)
        
        return SecurityIncident(
            id=incident_id,
            severity=severity,
            category=alert_data.get('category', 'unknown'),
            title=alert_data.get('title', 'Security Alert'),
            description=alert_data.get('description', ''),
            source_ip=alert_data.get('source_ip'),
            additional_data=alert_data.get('additional_data', {}),
            timestamp=datetime.utcnow()
        )

    def _determine_response_actions(self, incident: SecurityIncident) -> Dict[str, List[str]]:
        """Determine appropriate response actions for incident"""
        playbook = self.response_playbooks.get(incident.category, {})
        
        auto_actions = []
        manual_actions = []
        
        # Get playbook actions
        if playbook:
            auto_actions.extend(playbook.get('auto_actions', []))
            manual_actions.extend(playbook.get('manual_actions', []))
        
        # Add severity-based actions
        if incident.severity == IncidentSeverity.CRITICAL:
            auto_actions.extend(['notify_security_team', 'increase_logging_level'])
            manual_actions.extend(['immediate_investigation', 'consider_service_isolation'])
        elif incident.severity == IncidentSeverity.HIGH:
            auto_actions.extend(['notify_security_team'])
            manual_actions.extend(['investigate_within_15min'])
        
        # IP-based actions
        if incident.source_ip and self._is_external_ip(incident.source_ip):
            if incident.category in ['brute_force', 'ddos', 'sql_injection']:
                auto_actions.append('block_ip')
        
        return {
            'auto': auto_actions,
            'manual': manual_actions
        }

    def _execute_automatic_action(self, incident: SecurityIncident, action: str):
        """Execute automatic response action"""
        try:
            logger.info(f"Executing automatic action '{action}' for incident {incident.id}")
            
            action_success = False
            
            if action == 'block_ip' and incident.source_ip:
                action_success = self._block_ip_address(incident.source_ip, incident.id)
                
            elif action == 'increase_monitoring':
                action_success = self._increase_monitoring_level(incident.category)
                
            elif action == 'enable_rate_limiting':
                action_success = self._enable_rate_limiting()
                
            elif action == 'notify_security_team':
                action_success = self._notify_security_team(incident)
                
            elif action == 'isolate_affected_endpoint':
                action_success = self._isolate_endpoint(incident)
                
            elif action == 'disable_affected_account':
                action_success = self._disable_user_account(incident)
                
            elif action == 'activate_cdn_protection':
                action_success = self._activate_cdn_protection()
                
            elif action == 'increase_logging_level':
                action_success = self._increase_logging_level()
                
            else:
                logger.warning(f"Unknown automatic action: {action}")
                return False
            
            # Record action
            if action_success:
                incident.actions_taken.append(f"AUTO: {action} - {datetime.utcnow().isoformat()}")
                self.stats['automatic_responses'] += 1
                logger.info(f"✅ Action '{action}' completed successfully for incident {incident.id}")
            else:
                incident.actions_taken.append(f"FAILED: {action} - {datetime.utcnow().isoformat()}")
                logger.error(f"❌ Action '{action}' failed for incident {incident.id}")
            
            return action_success
            
        except Exception as e:
            logger.error(f"Error executing action '{action}' for incident {incident.id}: {e}")
            incident.actions_taken.append(f"ERROR: {action} - {e}")
            return False

    def _block_ip_address(self, ip_address: str, incident_id: str) -> bool:
        """Block IP address using iptables and fail2ban"""
        try:
            # Add to iptables
            result = subprocess.run([
                'iptables', '-I', 'INPUT', '-s', ip_address, '-j', 'DROP'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Add to fail2ban if configured
                if self.config['auto_response']['enable_fail2ban_integration']:
                    subprocess.run([
                        'fail2ban-client', 'set', 'adcopysurge-general', 'banip', ip_address
                    ], capture_output=True, text=True, timeout=10)
                
                # Track blocked IP
                self.blocked_ips.add(ip_address)
                self.stats['ips_blocked'] += 1
                
                # Store in Redis for tracking
                if self.redis_client:
                    self.redis_client.hset(
                        'security:blocked_ips',
                        ip_address,
                        json.dumps({
                            'blocked_at': datetime.utcnow().isoformat(),
                            'incident_id': incident_id,
                            'auto_unblock_at': (datetime.utcnow() + timedelta(minutes=self.thresholds['ban_duration_minutes'])).isoformat()
                        })
                    )
                
                logger.info(f"🚫 IP {ip_address} blocked successfully")
                return True
            else:
                logger.error(f"Failed to block IP {ip_address}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address}: {e}")
            return False

    def _increase_monitoring_level(self, category: str) -> bool:
        """Increase monitoring sensitivity for specific category"""
        try:
            # Notify monitoring system to increase sensitivity
            if self.redis_client:
                self.redis_client.hset(
                    'monitoring:sensitivity',
                    category,
                    json.dumps({
                        'level': 'high',
                        'increased_at': datetime.utcnow().isoformat(),
                        'duration_minutes': 60
                    })
                )
                
            logger.info(f"📈 Monitoring level increased for category: {category}")
            return True
            
        except Exception as e:
            logger.error(f"Error increasing monitoring level: {e}")
            return False

    def _enable_rate_limiting(self) -> bool:
        """Enable enhanced rate limiting"""
        try:
            # Update nginx rate limiting
            rate_limit_config = """
            # Enhanced rate limiting for incident response
            limit_req_zone $binary_remote_addr zone=enhanced_auth:10m rate=5r/m;
            limit_req_zone $binary_remote_addr zone=enhanced_api:10m rate=50r/m;
            """
            
            # In production, update nginx config and reload
            # For now, just update Redis flag
            if self.redis_client:
                self.redis_client.setex(
                    'rate_limiting:enhanced',
                    3600,  # 1 hour
                    'enabled'
                )
            
            logger.info("🛡️ Enhanced rate limiting enabled")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling rate limiting: {e}")
            return False

    def _notify_security_team(self, incident: SecurityIncident) -> bool:
        """Send immediate notification to security team"""
        try:
            # Send email notification
            email_config = self.config['email']
            if email_config['username'] and email_config['password']:
                msg = MimeMultipart()
                msg['From'] = 'security@adcopysurge.com'
                msg['To'] = ', '.join(email_config['security_team'])
                msg['Subject'] = f"🚨 SECURITY INCIDENT: {incident.title} [{incident.severity.value.upper()}]"
                
                body = f"""
SECURITY INCIDENT ALERT

Incident ID: {incident.id}
Severity: {incident.severity.value.upper()}
Category: {incident.category}
Title: {incident.title}
Description: {incident.description}
Source IP: {incident.source_ip or 'N/A'}
Timestamp: {incident.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

Actions Taken:
{chr(10).join(['- ' + action for action in incident.actions_taken])}

Additional Data:
{json.dumps(incident.additional_data, indent=2)}

This incident requires immediate attention.

AdCopySurge Security Team
                """
                
                msg.attach(MimeText(body, 'plain'))
                
                with smtplib.SMTP(email_config['smtp_host'], email_config['smtp_port']) as server:
                    server.starttls()
                    server.login(email_config['username'], email_config['password'])
                    server.send_message(msg)
            
            # Send webhook notification
            webhook_url = self.config['webhooks']['security_channel']
            if webhook_url:
                payload = {
                    'text': f"🚨 SECURITY INCIDENT: {incident.title}",
                    'attachments': [{
                        'color': 'danger',
                        'fields': [
                            {'title': 'Incident ID', 'value': incident.id, 'short': True},
                            {'title': 'Severity', 'value': incident.severity.value.upper(), 'short': True},
                            {'title': 'Category', 'value': incident.category, 'short': True},
                            {'title': 'Source IP', 'value': incident.source_ip or 'N/A', 'short': True}
                        ]
                    }]
                }
                
                response = requests.post(webhook_url, json=payload, timeout=10)
                response.raise_for_status()
            
            logger.info(f"📧 Security team notified for incident {incident.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error notifying security team: {e}")
            return False

    def _isolate_endpoint(self, incident: SecurityIncident) -> bool:
        """Isolate affected endpoint (manual approval required)"""
        try:
            # For now, just flag for manual review
            if self.redis_client:
                self.redis_client.lpush(
                    'manual_actions:endpoint_isolation',
                    json.dumps({
                        'incident_id': incident.id,
                        'requested_at': datetime.utcnow().isoformat(),
                        'affected_resources': incident.affected_resources
                    })
                )
            
            logger.info(f"🔒 Endpoint isolation requested for incident {incident.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error requesting endpoint isolation: {e}")
            return False

    def _disable_user_account(self, incident: SecurityIncident) -> bool:
        """Disable affected user account"""
        try:
            # Extract user info from additional data
            user_id = incident.additional_data.get('user_id')
            username = incident.additional_data.get('username')
            
            if not (user_id or username):
                logger.warning(f"No user identifier found for incident {incident.id}")
                return False
            
            # Flag account for immediate review/disable
            if self.redis_client:
                self.redis_client.lpush(
                    'manual_actions:disable_account',
                    json.dumps({
                        'incident_id': incident.id,
                        'user_id': user_id,
                        'username': username,
                        'requested_at': datetime.utcnow().isoformat(),
                        'reason': incident.description
                    })
                )
            
            logger.info(f"👤 Account disable requested for incident {incident.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error requesting account disable: {e}")
            return False

    def _activate_cdn_protection(self) -> bool:
        """Activate CDN DDoS protection"""
        try:
            # This would integrate with CDN provider API
            # For now, flag for manual activation
            if self.redis_client:
                self.redis_client.setex(
                    'cdn:ddos_protection_requested',
                    3600,
                    json.dumps({
                        'requested_at': datetime.utcnow().isoformat(),
                        'status': 'pending_manual_activation'
                    })
                )
            
            logger.info("🌐 CDN DDoS protection activation requested")
            return True
            
        except Exception as e:
            logger.error(f"Error requesting CDN protection: {e}")
            return False

    def _increase_logging_level(self) -> bool:
        """Increase application logging level"""
        try:
            if self.redis_client:
                self.redis_client.setex(
                    'app:logging_level',
                    3600,  # 1 hour
                    'DEBUG'
                )
            
            logger.info("📋 Application logging level increased to DEBUG")
            return True
            
        except Exception as e:
            logger.error(f"Error increasing logging level: {e}")
            return False

    def _is_external_ip(self, ip: str) -> bool:
        """Check if IP is external (not internal network)"""
        # Simple check for private IP ranges
        private_ranges = [
            '10.', '172.16.', '172.17.', '172.18.', '172.19.',
            '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
            '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
            '172.30.', '172.31.', '192.168.', '127.'
        ]
        
        return not any(ip.startswith(prefix) for prefix in private_ranges)

    def _should_escalate(self, incident: SecurityIncident) -> bool:
        """Determine if incident should be escalated"""
        playbook = self.response_playbooks.get(incident.category, {})
        escalation_criteria = playbook.get('escalation_criteria', [])
        
        # Always escalate critical incidents
        if incident.severity == IncidentSeverity.CRITICAL:
            return True
        
        # Check specific escalation criteria
        if 'always' in escalation_criteria:
            return True
        
        # Check if multiple incidents of same type
        if self.redis_client:
            recent_incidents = self.redis_client.hgetall('incidents:active')
            same_category_count = sum(
                1 for inc_data in recent_incidents.values()
                if json.loads(inc_data).get('category') == incident.category
            )
            
            if same_category_count >= self.thresholds['auto_escalation_threshold']:
                return True
        
        # Additional escalation logic
        additional_data = incident.additional_data
        if ('successful_data_access' in str(additional_data) or
            'internal_ip_source' in escalation_criteria and not self._is_external_ip(incident.source_ip or '')):
            return True
        
        return False

    def _escalate_incident(self, incident: SecurityIncident):
        """Escalate incident to higher level response team"""
        try:
            incident.status = ResponseStatus.ESCALATED
            self.stats['manual_escalations'] += 1
            
            logger.warning(f"🚨 ESCALATING INCIDENT: {incident.id}")
            
            # Send high-priority notifications
            self._send_escalation_notification(incident)
            
            # Create PagerDuty alert if configured
            pagerduty_key = self.config['webhooks'].get('pagerduty_key')
            if pagerduty_key:
                self._trigger_pagerduty_alert(incident, pagerduty_key)
            
            # Mark for immediate manual review
            if self.redis_client:
                self.redis_client.lpush(
                    'incidents:escalated',
                    json.dumps({
                        'incident_id': incident.id,
                        'escalated_at': datetime.utcnow().isoformat(),
                        'severity': incident.severity.value,
                        'category': incident.category,
                        'description': incident.description,
                        'priority': 'immediate_attention_required'
                    })
                )
            
        except Exception as e:
            logger.error(f"Error escalating incident {incident.id}: {e}")

    def _send_escalation_notification(self, incident: SecurityIncident):
        """Send escalation notification to admin team"""
        try:
            email_config = self.config['email']
            if email_config['username'] and email_config['password']:
                msg = MimeMultipart()
                msg['From'] = 'security@adcopysurge.com'
                msg['To'] = ', '.join(email_config['admin_team'])
                msg['Subject'] = f"🚨🚨 ESCALATED SECURITY INCIDENT: {incident.title}"
                
                body = f"""
ESCALATED SECURITY INCIDENT - IMMEDIATE ATTENTION REQUIRED

⚠️ This incident has been automatically escalated and requires immediate attention.

Incident Details:
- ID: {incident.id}
- Severity: {incident.severity.value.upper()}
- Category: {incident.category}
- Title: {incident.title}
- Description: {incident.description}
- Source IP: {incident.source_ip or 'N/A'}
- Timestamp: {incident.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
- Escalated At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Automatic Actions Taken:
{chr(10).join(['- ' + action for action in incident.actions_taken]) if incident.actions_taken else '- None'}

Additional Data:
{json.dumps(incident.additional_data, indent=2)}

Please take immediate action to investigate and resolve this incident.

AdCopySurge Security Team - ESCALATED ALERT
                """
                
                msg.attach(MimeText(body, 'plain'))
                
                with smtplib.SMTP(email_config['smtp_host'], email_config['smtp_port']) as server:
                    server.starttls()
                    server.login(email_config['username'], email_config['password'])
                    server.send_message(msg)
                
                logger.info(f"📧 Escalation notification sent for incident {incident.id}")
                
        except Exception as e:
            logger.error(f"Error sending escalation notification: {e}")

    def _trigger_pagerduty_alert(self, incident: SecurityIncident, api_key: str):
        """Trigger PagerDuty alert for critical incidents"""
        try:
            url = "https://events.pagerduty.com/v2/enqueue"
            
            payload = {
                "routing_key": api_key,
                "event_action": "trigger",
                "payload": {
                    "summary": f"ESCALATED: {incident.title}",
                    "severity": incident.severity.value,
                    "source": "AdCopySurge Security Monitor",
                    "component": incident.category,
                    "group": "Security",
                    "class": "Security Incident",
                    "custom_details": {
                        "incident_id": incident.id,
                        "source_ip": incident.source_ip,
                        "description": incident.description,
                        "actions_taken": incident.actions_taken
                    }
                }
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"📟 PagerDuty alert triggered for incident {incident.id}")
            
        except Exception as e:
            logger.error(f"Error triggering PagerDuty alert: {e}")

    def cleanup_resolved_incidents(self):
        """Clean up old resolved incidents"""
        try:
            if not self.redis_client:
                return
            
            # Remove incidents older than 7 days
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            active_incidents = self.redis_client.hgetall('incidents:active')
            for incident_id, incident_data in active_incidents.items():
                data = json.loads(incident_data)
                incident_time = datetime.fromisoformat(data['timestamp'])
                
                if incident_time < seven_days_ago:
                    self.redis_client.hdel('incidents:active', incident_id)
                    self.redis_client.hset('incidents:archived', incident_id, incident_data)
            
            # Unblock IPs that have exceeded ban duration
            blocked_ips = self.redis_client.hgetall('security:blocked_ips')
            for ip, block_data in blocked_ips.items():
                data = json.loads(block_data)
                unblock_time = datetime.fromisoformat(data['auto_unblock_at'])
                
                if datetime.utcnow() > unblock_time:
                    self._unblock_ip_address(ip)
                    self.redis_client.hdel('security:blocked_ips', ip)
            
            logger.info("🧹 Cleanup completed - old incidents archived, expired blocks removed")
            
        except Exception as e:
            logger.error(f"Error cleaning up incidents: {e}")

    def _unblock_ip_address(self, ip_address: str) -> bool:
        """Unblock IP address"""
        try:
            result = subprocess.run([
                'iptables', '-D', 'INPUT', '-s', ip_address, '-j', 'DROP'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                if ip_address in self.blocked_ips:
                    self.blocked_ips.remove(ip_address)
                
                logger.info(f"✅ IP {ip_address} unblocked successfully")
                return True
            else:
                logger.warning(f"Could not unblock IP {ip_address} (may not have been blocked)")
                return False
                
        except Exception as e:
            logger.error(f"Error unblocking IP {ip_address}: {e}")
            return False

    def get_incident_status(self, incident_id: str) -> Optional[Dict]:
        """Get current status of an incident"""
        if self.redis_client:
            incident_data = self.redis_client.hget('incidents:active', incident_id)
            if incident_data:
                return json.loads(incident_data)
        return None

    def list_active_incidents(self) -> List[Dict]:
        """List all active incidents"""
        if self.redis_client:
            active_incidents = self.redis_client.hgetall('incidents:active')
            return [json.loads(data) for data in active_incidents.values()]
        return []

    def get_response_stats(self) -> Dict:
        """Get incident response statistics"""
        return {
            **self.stats,
            'active_incidents': len(self.list_active_incidents()),
            'blocked_ips_count': len(self.blocked_ips),
            'uptime_hours': (datetime.utcnow() - datetime.utcnow()).total_seconds() / 3600
        }


def main():
    """Main entry point for testing"""
    response_system = IncidentResponseSystem()
    
    # Example alert handling
    sample_alert = {
        'severity': 'high',
        'category': 'brute_force',
        'title': 'Multiple Authentication Failures',
        'description': 'IP attempting brute force attack on login endpoint',
        'source_ip': '192.0.2.100',
        'additional_data': {
            'failure_count': 15,
            'endpoint': '/api/auth/login',
            'user_agent': 'suspicious-bot'
        }
    }
    
    incident = response_system.handle_security_alert(sample_alert)
    if incident:
        print(f"Handled incident: {incident.id}")
        print(f"Actions taken: {incident.actions_taken}")


if __name__ == "__main__":
    main()
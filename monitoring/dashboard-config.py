#!/usr/bin/env python3
"""
AdCopySurge Security Dashboard Configuration
Dashboard configuration for real-time security monitoring and incident management
"""

import os
import json
from typing import Dict, List, Any

class SecurityDashboardConfig:
    """Configuration for the AdCopySurge security dashboard"""
    
    @staticmethod
    def get_dashboard_config() -> Dict[str, Any]:
        """Get the main dashboard configuration"""
        return {
            'dashboard': {
                'title': 'AdCopySurge Security Operations Center',
                'refresh_interval': 30,  # seconds
                'theme': 'dark',
                'timezone': 'UTC',
                'enable_sound_alerts': True,
                'auto_acknowledge_timeout': 300,  # 5 minutes
                'max_visible_alerts': 100,
                'alert_retention_days': 30
            },
            
            'widgets': [
                {
                    'id': 'security_overview',
                    'title': 'Security Overview',
                    'type': 'stats_grid',
                    'position': {'x': 0, 'y': 0, 'width': 12, 'height': 2},
                    'data_source': 'redis://security:stats',
                    'metrics': [
                        {'key': 'active_alerts', 'label': 'Active Alerts', 'color': 'red'},
                        {'key': 'incidents_today', 'label': 'Incidents Today', 'color': 'orange'},
                        {'key': 'blocked_ips', 'label': 'Blocked IPs', 'color': 'blue'},
                        {'key': 'system_health', 'label': 'System Health', 'color': 'green'}
                    ]
                },
                
                {
                    'id': 'real_time_alerts',
                    'title': 'Real-Time Security Alerts',
                    'type': 'alert_feed',
                    'position': {'x': 0, 'y': 2, 'width': 8, 'height': 6},
                    'data_source': 'redis://security:alerts',
                    'config': {
                        'max_items': 20,
                        'auto_scroll': True,
                        'severity_colors': {
                            'critical': '#ff0000',
                            'high': '#ff6600',
                            'medium': '#ffaa00',
                            'low': '#00aa00'
                        },
                        'sound_alerts': {
                            'critical': 'alarm_critical.mp3',
                            'high': 'alert_high.mp3'
                        }
                    }
                },
                
                {
                    'id': 'incident_status',
                    'title': 'Incident Response Status',
                    'type': 'incident_board',
                    'position': {'x': 8, 'y': 2, 'width': 4, 'height': 6},
                    'data_source': 'redis://incidents:active',
                    'config': {
                        'show_actions': True,
                        'enable_manual_actions': True,
                        'auto_refresh': True
                    }
                },
                
                {
                    'id': 'threat_map',
                    'title': 'Geographic Threat Map',
                    'type': 'world_map',
                    'position': {'x': 0, 'y': 8, 'width': 6, 'height': 4},
                    'data_source': 'redis://security:geo_threats',
                    'config': {
                        'map_type': 'world',
                        'attack_markers': True,
                        'heat_map': True,
                        'country_stats': True
                    }
                },
                
                {
                    'id': 'attack_trends',
                    'title': 'Attack Trends (24h)',
                    'type': 'time_series',
                    'position': {'x': 6, 'y': 8, 'width': 6, 'height': 4},
                    'data_source': 'redis://security:metrics',
                    'config': {
                        'timeframe': '24h',
                        'metrics': [
                            'brute_force_attempts',
                            'sql_injection_attempts',
                            'ddos_requests',
                            'reconnaissance_scans'
                        ],
                        'colors': ['#ff4444', '#ff8800', '#4488ff', '#44ff44']
                    }
                },
                
                {
                    'id': 'system_metrics',
                    'title': 'System Performance',
                    'type': 'gauge_grid',
                    'position': {'x': 0, 'y': 12, 'width': 4, 'height': 3},
                    'data_source': 'redis://system:metrics',
                    'config': {
                        'gauges': [
                            {'metric': 'cpu_usage', 'label': 'CPU %', 'max': 100, 'warning': 80, 'critical': 95},
                            {'metric': 'memory_usage', 'label': 'Memory %', 'max': 100, 'warning': 85, 'critical': 95},
                            {'metric': 'disk_usage', 'label': 'Disk %', 'max': 100, 'warning': 80, 'critical': 90}
                        ]
                    }
                },
                
                {
                    'id': 'network_traffic',
                    'title': 'Network Traffic Analysis',
                    'type': 'traffic_analyzer',
                    'position': {'x': 4, 'y': 12, 'width': 4, 'height': 3},
                    'data_source': 'redis://network:traffic',
                    'config': {
                        'show_protocols': True,
                        'show_top_ips': True,
                        'anomaly_detection': True,
                        'traffic_threshold': 1000  # requests per minute
                    }
                },
                
                {
                    'id': 'security_logs',
                    'title': 'Security Event Logs',
                    'type': 'log_viewer',
                    'position': {'x': 8, 'y': 12, 'width': 4, 'height': 3},
                    'data_source': 'file:///var/log/adcopysurge/security.log',
                    'config': {
                        'tail_lines': 100,
                        'auto_scroll': True,
                        'highlight_patterns': [
                            {'pattern': 'CRITICAL', 'color': '#ff0000'},
                            {'pattern': 'ERROR', 'color': '#ff6600'},
                            {'pattern': 'WARNING', 'color': '#ffaa00'},
                            {'pattern': 'BLOCKED', 'color': '#0066ff'}
                        ]
                    }
                },
                
                {
                    'id': 'fail2ban_status',
                    'title': 'Fail2Ban Status',
                    'type': 'jail_monitor',
                    'position': {'x': 0, 'y': 15, 'width': 6, 'height': 2},
                    'data_source': 'redis://fail2ban:status',
                    'config': {
                        'show_banned_ips': True,
                        'show_jail_status': True,
                        'enable_unban_actions': True
                    }
                },
                
                {
                    'id': 'threat_intelligence',
                    'title': 'Threat Intelligence Feed',
                    'type': 'threat_feed',
                    'position': {'x': 6, 'y': 15, 'width': 6, 'height': 2},
                    'data_source': 'api://threat_intelligence',
                    'config': {
                        'feeds': [
                            'malware_ips',
                            'botnet_c2',
                            'phishing_domains',
                            'tor_exits'
                        ],
                        'update_interval': 3600  # 1 hour
                    }
                }
            ],
            
            'notifications': {
                'email': {
                    'enabled': True,
                    'recipients': ['security@adcopysurge.com'],
                    'severity_threshold': 'medium'
                },
                'slack': {
                    'enabled': True,
                    'webhook_url': os.getenv('SLACK_SECURITY_WEBHOOK'),
                    'channel': '#security-alerts',
                    'severity_threshold': 'high'
                },
                'sms': {
                    'enabled': False,
                    'api_key': os.getenv('SMS_API_KEY'),
                    'recipients': ['+1234567890'],
                    'severity_threshold': 'critical'
                },
                'push': {
                    'enabled': True,
                    'service': 'pushover',
                    'api_token': os.getenv('PUSHOVER_TOKEN'),
                    'severity_threshold': 'high'
                }
            },
            
            'data_sources': {
                'redis': {
                    'host': os.getenv('REDIS_HOST', 'localhost'),
                    'port': int(os.getenv('REDIS_PORT', 6379)),
                    'db': int(os.getenv('REDIS_DB', 0)),
                    'password': os.getenv('REDIS_PASSWORD')
                },
                'elasticsearch': {
                    'enabled': False,
                    'hosts': [os.getenv('ELASTICSEARCH_URL', 'localhost:9200')],
                    'index_pattern': 'adcopysurge-security-*'
                },
                'prometheus': {
                    'enabled': False,
                    'url': os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
                }
            },
            
            'user_management': {
                'authentication': 'oauth',
                'oauth_provider': 'google',
                'allowed_domains': ['adcopysurge.com'],
                'roles': {
                    'admin': {
                        'permissions': ['read', 'write', 'manage_users', 'manage_config'],
                        'widgets': '*'
                    },
                    'security_analyst': {
                        'permissions': ['read', 'acknowledge_alerts', 'manage_incidents'],
                        'widgets': ['security_overview', 'real_time_alerts', 'incident_status', 'threat_map', 'security_logs']
                    },
                    'viewer': {
                        'permissions': ['read'],
                        'widgets': ['security_overview', 'threat_map', 'attack_trends']
                    }
                }
            },
            
            'integrations': {
                'jira': {
                    'enabled': False,
                    'url': os.getenv('JIRA_URL'),
                    'username': os.getenv('JIRA_USERNAME'),
                    'api_token': os.getenv('JIRA_API_TOKEN'),
                    'project_key': 'SEC',
                    'issue_type': 'Security Incident'
                },
                'servicenow': {
                    'enabled': False,
                    'instance': os.getenv('SERVICENOW_INSTANCE'),
                    'username': os.getenv('SERVICENOW_USERNAME'),
                    'password': os.getenv('SERVICENOW_PASSWORD'),
                    'table': 'incident'
                },
                'splunk': {
                    'enabled': False,
                    'host': os.getenv('SPLUNK_HOST'),
                    'port': int(os.getenv('SPLUNK_PORT', 8089)),
                    'username': os.getenv('SPLUNK_USERNAME'),
                    'password': os.getenv('SPLUNK_PASSWORD'),
                    'index': 'adcopysurge_security'
                }
            },
            
            'api': {
                'enable_rest_api': True,
                'api_key_required': True,
                'rate_limit': '100/hour',
                'cors_origins': ['https://dashboard.adcopysurge.com'],
                'endpoints': [
                    '/api/v1/alerts',
                    '/api/v1/incidents',
                    '/api/v1/metrics',
                    '/api/v1/status',
                    '/api/v1/actions'
                ]
            },
            
            'security': {
                'session_timeout': 3600,  # 1 hour
                'csrf_protection': True,
                'content_security_policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
                'x_frame_options': 'DENY',
                'x_content_type_options': 'nosniff',
                'enable_audit_log': True,
                'audit_log_retention': 90  # days
            }
        }
    
    @staticmethod
    def get_alert_rules() -> List[Dict[str, Any]]:
        """Get alert rules configuration"""
        return [
            {
                'name': 'Critical Authentication Failures',
                'condition': 'auth_failures_per_minute > 20',
                'severity': 'critical',
                'description': 'Massive authentication failure spike detected',
                'auto_actions': ['block_top_ips', 'enable_rate_limiting', 'notify_security_team'],
                'cooldown': 300  # 5 minutes
            },
            {
                'name': 'DDoS Attack Detection',
                'condition': 'requests_per_minute > 5000 AND unique_ips < 10',
                'severity': 'critical',
                'description': 'Potential DDoS attack from few source IPs',
                'auto_actions': ['enable_ddos_protection', 'block_source_ips', 'escalate_incident'],
                'cooldown': 600  # 10 minutes
            },
            {
                'name': 'SQL Injection Attempts',
                'condition': 'sql_injection_patterns > 5',
                'severity': 'high',
                'description': 'Multiple SQL injection attempts detected',
                'auto_actions': ['block_source_ip', 'isolate_endpoint', 'notify_security_team'],
                'cooldown': 180  # 3 minutes
            },
            {
                'name': 'Reconnaissance Activity',
                'condition': 'scanning_patterns > 10',
                'severity': 'medium',
                'description': 'Network reconnaissance activity detected',
                'auto_actions': ['block_source_ip', 'increase_monitoring'],
                'cooldown': 300  # 5 minutes
            },
            {
                'name': 'Malware Detection',
                'condition': 'malware_signatures > 0',
                'severity': 'critical',
                'description': 'Malware activity detected on system',
                'auto_actions': ['isolate_system', 'escalate_incident', 'notify_admin_team'],
                'cooldown': 0  # Immediate, no cooldown
            },
            {
                'name': 'High Error Rate',
                'condition': 'error_rate_percent > 10',
                'severity': 'medium',
                'description': 'Application error rate is abnormally high',
                'auto_actions': ['increase_logging', 'notify_dev_team'],
                'cooldown': 900  # 15 minutes
            },
            {
                'name': 'System Resource Exhaustion',
                'condition': 'cpu_usage > 95 OR memory_usage > 95 OR disk_usage > 95',
                'severity': 'high',
                'description': 'System resources critically low',
                'auto_actions': ['notify_ops_team', 'scale_resources'],
                'cooldown': 300  # 5 minutes
            },
            {
                'name': 'Privilege Escalation Attempt',
                'condition': 'privilege_escalation_patterns > 0',
                'severity': 'critical',
                'description': 'Privilege escalation attempt detected',
                'auto_actions': ['disable_affected_account', 'escalate_incident', 'audit_system'],
                'cooldown': 0  # Immediate
            },
            {
                'name': 'Data Exfiltration Attempt',
                'condition': 'large_data_transfers > 1GB AND unusual_time',
                'severity': 'critical',
                'description': 'Potential data exfiltration detected',
                'auto_actions': ['block_transfer', 'escalate_incident', 'notify_legal_team'],
                'cooldown': 0  # Immediate
            },
            {
                'name': 'Insider Threat Indicators',
                'condition': 'unusual_access_patterns OR off_hours_activity',
                'severity': 'medium',
                'description': 'Potential insider threat activity',
                'auto_actions': ['increase_user_monitoring', 'notify_security_team'],
                'cooldown': 3600  # 1 hour
            }
        ]
    
    @staticmethod
    def get_response_playbooks() -> Dict[str, Dict[str, Any]]:
        """Get incident response playbook configurations"""
        return {
            'brute_force_attack': {
                'title': 'Brute Force Attack Response',
                'severity_threshold': 'medium',
                'steps': [
                    {
                        'action': 'identify_source',
                        'description': 'Identify attacking IP addresses and patterns',
                        'automated': True,
                        'timeout': 60
                    },
                    {
                        'action': 'block_attackers',
                        'description': 'Block identified attacking IPs',
                        'automated': True,
                        'timeout': 30
                    },
                    {
                        'action': 'analyze_targets',
                        'description': 'Analyze targeted accounts and endpoints',
                        'automated': False,
                        'timeout': 300
                    },
                    {
                        'action': 'check_compromised',
                        'description': 'Check for compromised accounts',
                        'automated': False,
                        'timeout': 600
                    },
                    {
                        'action': 'strengthen_auth',
                        'description': 'Implement additional authentication measures',
                        'automated': False,
                        'timeout': 1800
                    }
                ]
            },
            
            'ddos_attack': {
                'title': 'DDoS Attack Response',
                'severity_threshold': 'high',
                'steps': [
                    {
                        'action': 'activate_protection',
                        'description': 'Activate DDoS protection mechanisms',
                        'automated': True,
                        'timeout': 30
                    },
                    {
                        'action': 'scale_infrastructure',
                        'description': 'Scale infrastructure to handle load',
                        'automated': True,
                        'timeout': 300
                    },
                    {
                        'action': 'analyze_traffic',
                        'description': 'Analyze attack traffic patterns',
                        'automated': False,
                        'timeout': 600
                    },
                    {
                        'action': 'contact_upstream',
                        'description': 'Contact upstream providers for filtering',
                        'automated': False,
                        'timeout': 900
                    },
                    {
                        'action': 'implement_filtering',
                        'description': 'Implement traffic filtering rules',
                        'automated': False,
                        'timeout': 1200
                    }
                ]
            },
            
            'malware_detection': {
                'title': 'Malware Incident Response',
                'severity_threshold': 'critical',
                'steps': [
                    {
                        'action': 'isolate_system',
                        'description': 'Isolate affected systems from network',
                        'automated': True,
                        'timeout': 60
                    },
                    {
                        'action': 'preserve_evidence',
                        'description': 'Create system image for forensic analysis',
                        'automated': False,
                        'timeout': 1800
                    },
                    {
                        'action': 'malware_analysis',
                        'description': 'Analyze malware sample and behavior',
                        'automated': False,
                        'timeout': 3600
                    },
                    {
                        'action': 'check_lateral_movement',
                        'description': 'Check for lateral movement and persistence',
                        'automated': False,
                        'timeout': 3600
                    },
                    {
                        'action': 'eradicate_malware',
                        'description': 'Remove malware and restore systems',
                        'automated': False,
                        'timeout': 7200
                    }
                ]
            },
            
            'data_breach': {
                'title': 'Data Breach Response',
                'severity_threshold': 'critical',
                'steps': [
                    {
                        'action': 'contain_breach',
                        'description': 'Stop ongoing data exfiltration',
                        'automated': True,
                        'timeout': 60
                    },
                    {
                        'action': 'assess_scope',
                        'description': 'Determine scope and type of compromised data',
                        'automated': False,
                        'timeout': 1800
                    },
                    {
                        'action': 'notify_stakeholders',
                        'description': 'Notify management and legal team',
                        'automated': True,
                        'timeout': 300
                    },
                    {
                        'action': 'legal_compliance',
                        'description': 'Ensure compliance with data protection laws',
                        'automated': False,
                        'timeout': 3600
                    },
                    {
                        'action': 'customer_notification',
                        'description': 'Prepare customer notification if required',
                        'automated': False,
                        'timeout': 7200
                    }
                ]
            }
        }
    
    @staticmethod
    def get_monitoring_thresholds() -> Dict[str, Any]:
        """Get monitoring thresholds configuration"""
        return {
            'authentication': {
                'failed_logins_per_minute': 10,
                'failed_logins_per_hour': 100,
                'account_lockout_threshold': 5,
                'suspicious_login_locations': True
            },
            
            'network': {
                'requests_per_minute_threshold': 1000,
                'error_rate_threshold_percent': 5,
                'response_time_threshold_ms': 5000,
                'bandwidth_threshold_mbps': 1000
            },
            
            'system': {
                'cpu_usage_warning': 80,
                'cpu_usage_critical': 95,
                'memory_usage_warning': 85,
                'memory_usage_critical': 95,
                'disk_usage_warning': 80,
                'disk_usage_critical': 90
            },
            
            'security': {
                'sql_injection_attempts': 3,
                'xss_attempts': 5,
                'directory_traversal_attempts': 3,
                'command_injection_attempts': 1,
                'suspicious_user_agents': 10
            },
            
            'application': {
                'database_connection_errors': 5,
                'api_timeout_threshold_ms': 10000,
                'cache_miss_rate_threshold': 50,
                'queue_size_threshold': 1000
            }
        }
    
    @staticmethod
    def save_config_file(config_path: str = "/etc/adcopysurge/dashboard.json"):
        """Save dashboard configuration to file"""
        config = {
            'dashboard': SecurityDashboardConfig.get_dashboard_config(),
            'alert_rules': SecurityDashboardConfig.get_alert_rules(),
            'playbooks': SecurityDashboardConfig.get_response_playbooks(),
            'thresholds': SecurityDashboardConfig.get_monitoring_thresholds()
        }
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Dashboard configuration saved to: {config_path}")


def main():
    """Generate and save dashboard configuration"""
    # Save to default location
    SecurityDashboardConfig.save_config_file()
    
    # Also save to project directory for development
    project_config_path = os.path.join(os.path.dirname(__file__), 'dashboard-config.json')
    SecurityDashboardConfig.save_config_file(project_config_path)
    
    print("Dashboard configuration files generated successfully!")


if __name__ == "__main__":
    main()
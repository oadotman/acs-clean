"""
AdCopySurge Session Management & Security System
Comprehensive session handling with device tracking, suspicious activity detection, and security controls
"""

import os
import json
import secrets
import hashlib
import redis
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from cryptography.fernet import Fernet
import base64
import geoip2.database
import ipaddress
from user_agents import parse
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    LOCKED = "locked"
    SUSPICIOUS = "suspicious"

class DeviceType(Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    BOT = "bot"
    UNKNOWN = "unknown"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEvent(Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    SESSION_CREATED = "session_created"
    SESSION_RENEWED = "session_renewed"
    SESSION_EXPIRED = "session_expired"
    SESSION_REVOKED = "session_revoked"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DEVICE_CHANGE = "device_change"
    LOCATION_CHANGE = "location_change"
    CONCURRENT_SESSION = "concurrent_session"
    BRUTE_FORCE_DETECTED = "brute_force_detected"

@dataclass
class DeviceInfo:
    """Device information for session tracking"""
    device_id: str
    device_type: DeviceType
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None
    screen_resolution: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    is_mobile: bool = False
    is_bot: bool = False
    fingerprint: Optional[str] = None

@dataclass
class LocationInfo:
    """Location information for session tracking"""
    ip_address: str
    country: Optional[str] = None
    country_code: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    isp: Optional[str] = None
    is_vpn: bool = False
    is_proxy: bool = False

@dataclass
class SecurityMetrics:
    """Security metrics for session analysis"""
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    failed_login_attempts: int = 0
    suspicious_activities: int = 0
    device_changes: int = 0
    location_changes: int = 0
    concurrent_sessions: int = 0
    last_activity_at: Optional[datetime] = None

@dataclass
class SessionData:
    """Complete session information"""
    session_id: str
    user_id: str
    status: SessionStatus
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    device_info: DeviceInfo
    location_info: LocationInfo
    security_metrics: SecurityMetrics
    ip_address: str
    user_agent: str
    csrf_token: Optional[str] = None
    mfa_verified: bool = False
    remember_me: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now(timezone.utc) > self.expires_at
    
    def is_active(self) -> bool:
        """Check if session is active and valid"""
        return self.status == SessionStatus.ACTIVE and not self.is_expired()
    
    def time_until_expiry(self) -> timedelta:
        """Get time until session expires"""
        return self.expires_at - datetime.now(timezone.utc)

@dataclass
class SecurityEvent:
    """Security event for audit logging"""
    event_id: str
    session_id: Optional[str]
    user_id: Optional[str]
    event_type: str
    description: str
    risk_level: RiskLevel
    ip_address: str
    user_agent: str
    timestamp: datetime
    additional_data: Dict[str, Any] = field(default_factory=dict)

class SessionManager:
    """Comprehensive session management and security system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.redis_client = self._init_redis()
        self.encryption_key = self._get_encryption_key()
        self.geoip_reader = self._init_geoip()
        
        # Session settings
        self.default_session_lifetime = timedelta(hours=self.config.get('default_session_hours', 24))
        self.remember_me_lifetime = timedelta(days=self.config.get('remember_me_days', 30))
        self.idle_timeout = timedelta(minutes=self.config.get('idle_timeout_minutes', 30))
        self.max_concurrent_sessions = self.config.get('max_concurrent_sessions', 5)
        
        # Security settings
        self.max_login_attempts = self.config.get('max_login_attempts', 5)
        self.lockout_duration = timedelta(minutes=self.config.get('lockout_duration_minutes', 15))
        self.suspicious_threshold = self.config.get('suspicious_threshold', 0.7)
        self.enable_device_tracking = self.config.get('enable_device_tracking', True)
        self.enable_location_tracking = self.config.get('enable_location_tracking', True)
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default session configuration"""
        return {
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/6'),
            'encryption_key': os.getenv('SESSION_ENCRYPTION_KEY'),
            'default_session_hours': 24,
            'remember_me_days': 30,
            'idle_timeout_minutes': 30,
            'max_concurrent_sessions': 5,
            'max_login_attempts': 5,
            'lockout_duration_minutes': 15,
            'suspicious_threshold': 0.7,
            'enable_device_tracking': True,
            'enable_location_tracking': True,
            'enable_security_monitoring': True,
            'geoip_database_path': '/usr/share/GeoIP/GeoLite2-City.mmdb',
            'session_cookie_name': 'adcs_session',
            'session_cookie_secure': True,
            'session_cookie_httponly': True,
            'session_cookie_samesite': 'Strict'
        }
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for session data"""
        try:
            client = redis.from_url(self.config['redis_url'], decode_responses=True)
            client.ping()
            return client
        except Exception as e:
            logger.warning(f"Redis not available for sessions: {e}")
            return None
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for session data"""
        key_str = self.config.get('encryption_key')
        if key_str:
            return base64.urlsafe_b64decode(key_str.encode())
        else:
            key = Fernet.generate_key()
            logger.warning("Session encryption key not configured, using generated key (not persistent)")
            return key
    
    def _init_geoip(self) -> Optional[Any]:
        """Initialize GeoIP database for location tracking"""
        try:
            geoip_path = self.config.get('geoip_database_path')
            if geoip_path and os.path.exists(geoip_path):
                return geoip2.database.Reader(geoip_path)
        except Exception as e:
            logger.warning(f"GeoIP database not available: {e}")
        return None
    
    # Session Management
    
    def create_session(self, 
                      user_id: str, 
                      ip_address: str, 
                      user_agent: str,
                      remember_me: bool = False,
                      mfa_verified: bool = False,
                      additional_headers: Dict[str, str] = None) -> Tuple[SessionData, str]:
        """Create a new user session"""
        try:
            # Generate session ID and CSRF token
            session_id = self._generate_session_id()
            csrf_token = self._generate_csrf_token()
            
            # Parse device information
            device_info = self._parse_device_info(user_agent, additional_headers or {})
            
            # Get location information
            location_info = self._get_location_info(ip_address)
            
            # Calculate security metrics
            security_metrics = self._calculate_initial_security_metrics(user_id, ip_address, device_info, location_info)
            
            # Determine session lifetime
            lifetime = self.remember_me_lifetime if remember_me else self.default_session_lifetime
            expires_at = datetime.now(timezone.utc) + lifetime
            
            # Create session data
            session = SessionData(
                session_id=session_id,
                user_id=user_id,
                status=SessionStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                last_activity_at=datetime.now(timezone.utc),
                expires_at=expires_at,
                device_info=device_info,
                location_info=location_info,
                security_metrics=security_metrics,
                ip_address=ip_address,
                user_agent=user_agent,
                csrf_token=csrf_token,
                mfa_verified=mfa_verified,
                remember_me=remember_me
            )
            
            # Check concurrent session limits
            self._enforce_concurrent_session_limits(user_id, session_id)
            
            # Store session
            if self.redis_client:
                self._store_session(session)
                
                # Add to user's active sessions
                self.redis_client.sadd(f"sessions:user:{user_id}", session_id)
                
                # Set session expiry
                ttl = int(lifetime.total_seconds())
                self.redis_client.expire(f"session:{session_id}", ttl)
            
            # Log session creation
            self._log_security_event(
                session_id=session_id,
                user_id=user_id,
                event_type=SecurityEvent.SESSION_CREATED.value,
                description="New session created",
                risk_level=security_metrics.risk_level,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            logger.info(f"Session created for user {user_id}: {session_id}")
            return session, csrf_token
            
        except Exception as e:
            logger.error(f"Error creating session for user {user_id}: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session by ID"""
        try:
            if not self.redis_client:
                return None
            
            session_data = self.redis_client.get(f"session:{session_id}")
            if not session_data:
                return None
            
            # Decrypt and deserialize session data
            decrypted_data = self._decrypt_session_data(session_data)
            session = self._deserialize_session(json.loads(decrypted_data))
            
            # Check if session is expired
            if session.is_expired():
                self._expire_session(session_id)
                return None
            
            return session
            
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    def validate_session(self, 
                        session_id: str, 
                        ip_address: str, 
                        user_agent: str,
                        csrf_token: str = None) -> Tuple[bool, Optional[SessionData], Optional[str]]:
        """Validate session with security checks"""
        try:
            session = self.get_session(session_id)
            if not session:
                return False, None, "Session not found or expired"
            
            # Check session status
            if not session.is_active():
                return False, None, f"Session is {session.status.value}"
            
            # Check CSRF token if provided
            if csrf_token and csrf_token != session.csrf_token:
                self._log_security_event(
                    session_id=session_id,
                    user_id=session.user_id,
                    event_type=SecurityEvent.SUSPICIOUS_ACTIVITY.value,
                    description="CSRF token mismatch",
                    risk_level=RiskLevel.HIGH,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return False, None, "Invalid CSRF token"
            
            # Perform security checks
            security_check = self._perform_security_checks(session, ip_address, user_agent)
            if not security_check['valid']:
                return False, None, security_check['reason']
            
            # Update session activity
            session.last_activity_at = datetime.now(timezone.utc)
            if security_check.get('risk_score_changed', False):
                session.security_metrics = security_check['updated_metrics']
            
            # Store updated session
            if self.redis_client:
                self._store_session(session)
            
            return True, session, None
            
        except Exception as e:
            logger.error(f"Error validating session {session_id}: {e}")
            return False, None, "Session validation error"
    
    def refresh_session(self, session_id: str, extend_expiry: bool = True) -> bool:
        """Refresh session and optionally extend expiry"""
        try:
            session = self.get_session(session_id)
            if not session or not session.is_active():
                return False
            
            # Update activity timestamp
            session.last_activity_at = datetime.now(timezone.utc)
            
            # Extend expiry if requested
            if extend_expiry:
                lifetime = self.remember_me_lifetime if session.remember_me else self.default_session_lifetime
                session.expires_at = datetime.now(timezone.utc) + lifetime
            
            # Store updated session
            if self.redis_client:
                self._store_session(session)
                
                # Update Redis expiry
                if extend_expiry:
                    ttl = int((session.expires_at - datetime.now(timezone.utc)).total_seconds())
                    self.redis_client.expire(f"session:{session_id}", ttl)
            
            # Log session renewal
            self._log_security_event(
                session_id=session_id,
                user_id=session.user_id,
                event_type=SecurityEvent.SESSION_RENEWED.value,
                description="Session refreshed",
                risk_level=session.security_metrics.risk_level,
                ip_address=session.ip_address,
                user_agent=session.user_agent
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing session {session_id}: {e}")
            return False
    
    def revoke_session(self, session_id: str, reason: str = "Manual revocation") -> bool:
        """Revoke a specific session"""
        try:
            session = self.get_session(session_id)
            if not session:
                return False
            
            # Update session status
            session.status = SessionStatus.REVOKED
            
            # Store updated session (briefly for audit)
            if self.redis_client:
                self._store_session(session)
                
                # Remove from active sessions
                self.redis_client.srem(f"sessions:user:{session.user_id}", session_id)
                
                # Set short TTL for audit purposes
                self.redis_client.expire(f"session:{session_id}", 86400)  # 24 hours
            
            # Log revocation
            self._log_security_event(
                session_id=session_id,
                user_id=session.user_id,
                event_type=SecurityEvent.SESSION_REVOKED.value,
                description=f"Session revoked: {reason}",
                risk_level=RiskLevel.MEDIUM,
                ip_address=session.ip_address,
                user_agent=session.user_agent
            )
            
            logger.info(f"Session revoked: {session_id} - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking session {session_id}: {e}")
            return False
    
    def revoke_all_user_sessions(self, user_id: str, except_session: str = None, reason: str = "Revoke all sessions") -> int:
        """Revoke all sessions for a user"""
        try:
            if not self.redis_client:
                return 0
            
            # Get all user sessions
            session_ids = self.redis_client.smembers(f"sessions:user:{user_id}")
            revoked_count = 0
            
            for session_id in session_ids:
                if except_session and session_id == except_session:
                    continue
                
                if self.revoke_session(session_id, reason):
                    revoked_count += 1
            
            logger.info(f"Revoked {revoked_count} sessions for user {user_id}")
            return revoked_count
            
        except Exception as e:
            logger.error(f"Error revoking all sessions for user {user_id}: {e}")
            return 0
    
    def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[SessionData]:
        """Get all sessions for a user"""
        sessions = []
        
        try:
            if not self.redis_client:
                return sessions
            
            session_ids = self.redis_client.smembers(f"sessions:user:{user_id}")
            
            for session_id in session_ids:
                session = self.get_session(session_id)
                if session:
                    if not active_only or session.is_active():
                        sessions.append(session)
            
            # Sort by last activity (most recent first)
            sessions.sort(key=lambda s: s.last_activity_at, reverse=True)
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}")
            return []
    
    # Security Monitoring
    
    def record_login_attempt(self, 
                           user_id: str, 
                           ip_address: str, 
                           user_agent: str, 
                           success: bool,
                           failure_reason: str = None) -> bool:
        """Record login attempt for security monitoring"""
        try:
            if not self.redis_client:
                return False
            
            # Create attempt record
            attempt = {
                'user_id': user_id,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'success': success,
                'failure_reason': failure_reason,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Store attempt
            key = f"login_attempts:{user_id}:{int(datetime.now(timezone.utc).timestamp())}"
            self.redis_client.setex(key, 3600, json.dumps(attempt))  # 1 hour TTL
            
            # Track failed attempts for brute force detection
            if not success:
                attempts_key = f"failed_attempts:{user_id}"
                attempts_count = self.redis_client.incr(attempts_key)
                self.redis_client.expire(attempts_key, self.lockout_duration.total_seconds())
                
                # Check for brute force
                if attempts_count >= self.max_login_attempts:
                    self._handle_brute_force_detection(user_id, ip_address, user_agent, attempts_count)
                
                # Log failed attempt
                self._log_security_event(
                    session_id=None,
                    user_id=user_id,
                    event_type=SecurityEvent.LOGIN_FAILURE.value,
                    description=f"Login failed: {failure_reason}",
                    risk_level=RiskLevel.MEDIUM if attempts_count < self.max_login_attempts else RiskLevel.HIGH,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    additional_data={'attempt_count': attempts_count}
                )
            else:
                # Reset failed attempts on success
                self.redis_client.delete(f"failed_attempts:{user_id}")
                
                # Log successful login
                self._log_security_event(
                    session_id=None,
                    user_id=user_id,
                    event_type=SecurityEvent.LOGIN_SUCCESS.value,
                    description="Successful login",
                    risk_level=RiskLevel.LOW,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording login attempt: {e}")
            return False
    
    def is_user_locked(self, user_id: str) -> Tuple[bool, Optional[datetime]]:
        """Check if user is locked due to failed login attempts"""
        try:
            if not self.redis_client:
                return False, None
            
            attempts_key = f"failed_attempts:{user_id}"
            attempts_count = self.redis_client.get(attempts_key)
            
            if attempts_count and int(attempts_count) >= self.max_login_attempts:
                # Get TTL to determine when lockout expires
                ttl = self.redis_client.ttl(attempts_key)
                if ttl > 0:
                    unlock_time = datetime.now(timezone.utc) + timedelta(seconds=ttl)
                    return True, unlock_time
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking user lock status: {e}")
            return False, None
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            if not self.redis_client:
                return 0
            
            cleaned_count = 0
            
            # Get all session keys
            session_keys = self.redis_client.keys("session:*")
            
            for key in session_keys:
                try:
                    session_data = self.redis_client.get(key)
                    if session_data:
                        decrypted_data = self._decrypt_session_data(session_data)
                        session_dict = json.loads(decrypted_data)
                        
                        expires_at = datetime.fromisoformat(session_dict['expires_at'])
                        if expires_at < datetime.now(timezone.utc):
                            session_id = key.split(":", 1)[1]
                            self._expire_session(session_id)
                            cleaned_count += 1
                            
                except Exception as e:
                    # Delete corrupted session data
                    self.redis_client.delete(key)
                    cleaned_count += 1
                    logger.warning(f"Deleted corrupted session data: {key}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired/corrupted sessions")
                
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    # Helper Methods
    
    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        return secrets.token_urlsafe(32)
    
    def _generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    def _parse_device_info(self, user_agent: str, headers: Dict[str, str]) -> DeviceInfo:
        """Parse device information from user agent and headers"""
        try:
            ua = parse(user_agent)
            
            # Generate device fingerprint
            fingerprint_data = f"{user_agent}"
            for header in ['accept-language', 'accept-encoding', 'accept']:
                if header in headers:
                    fingerprint_data += f"|{headers[header]}"
            
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
            
            # Determine device type
            device_type = DeviceType.UNKNOWN
            if ua.is_mobile:
                device_type = DeviceType.MOBILE
            elif ua.is_tablet:
                device_type = DeviceType.TABLET
            elif ua.is_bot:
                device_type = DeviceType.BOT
            elif ua.is_pc:
                device_type = DeviceType.DESKTOP
            
            return DeviceInfo(
                device_id=fingerprint,
                device_type=device_type,
                os_name=ua.os.family,
                os_version=ua.os.version_string,
                browser_name=ua.browser.family,
                browser_version=ua.browser.version_string,
                is_mobile=ua.is_mobile,
                is_bot=ua.is_bot,
                fingerprint=fingerprint,
                screen_resolution=headers.get('screen-resolution'),
                timezone=headers.get('timezone'),
                language=headers.get('accept-language', '').split(',')[0] if headers.get('accept-language') else None
            )
            
        except Exception as e:
            logger.error(f"Error parsing device info: {e}")
            return DeviceInfo(
                device_id=secrets.token_urlsafe(8),
                device_type=DeviceType.UNKNOWN,
                fingerprint=hashlib.sha256(user_agent.encode()).hexdigest()[:16]
            )
    
    def _get_location_info(self, ip_address: str) -> LocationInfo:
        """Get location information from IP address"""
        try:
            location = LocationInfo(ip_address=ip_address)
            
            # Skip private IPs
            ip_obj = ipaddress.ip_address(ip_address)
            if ip_obj.is_private:
                location.country = "Private Network"
                return location
            
            if self.geoip_reader:
                try:
                    response = self.geoip_reader.city(ip_address)
                    location.country = response.country.name
                    location.country_code = response.country.iso_code
                    location.region = response.subdivisions.most_specific.name
                    location.city = response.city.name
                    location.latitude = float(response.location.latitude) if response.location.latitude else None
                    location.longitude = float(response.location.longitude) if response.location.longitude else None
                    location.timezone = response.location.time_zone
                except Exception as e:
                    logger.debug(f"Could not get location for IP {ip_address}: {e}")
            
            return location
            
        except Exception as e:
            logger.error(f"Error getting location info: {e}")
            return LocationInfo(ip_address=ip_address)
    
    def _calculate_initial_security_metrics(self, 
                                          user_id: str, 
                                          ip_address: str, 
                                          device_info: DeviceInfo, 
                                          location_info: LocationInfo) -> SecurityMetrics:
        """Calculate initial security metrics for a session"""
        risk_score = 0.0
        
        # Bot detection
        if device_info.is_bot:
            risk_score += 0.3
        
        # VPN/Proxy detection (simplified)
        if location_info.is_vpn or location_info.is_proxy:
            risk_score += 0.2
        
        # New device detection
        if self.redis_client and self.enable_device_tracking:
            known_devices = self.redis_client.smembers(f"user_devices:{user_id}")
            if device_info.fingerprint not in known_devices:
                risk_score += 0.3
                # Store new device
                self.redis_client.sadd(f"user_devices:{user_id}", device_info.fingerprint)
                self.redis_client.expire(f"user_devices:{user_id}", 86400 * 90)  # 90 days
        
        # Location change detection
        if self.redis_client and self.enable_location_tracking and location_info.country_code:
            last_country_key = f"user_last_country:{user_id}"
            last_country = self.redis_client.get(last_country_key)
            
            if last_country and last_country != location_info.country_code:
                risk_score += 0.4
            
            self.redis_client.setex(last_country_key, 86400 * 30, location_info.country_code)  # 30 days
        
        # Determine risk level
        risk_level = RiskLevel.LOW
        if risk_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 0.3:
            risk_level = RiskLevel.MEDIUM
        
        return SecurityMetrics(
            risk_score=risk_score,
            risk_level=risk_level,
            last_activity_at=datetime.now(timezone.utc)
        )
    
    def _perform_security_checks(self, 
                                session: SessionData, 
                                current_ip: str, 
                                current_user_agent: str) -> Dict[str, Any]:
        """Perform security checks on session validation"""
        result = {'valid': True, 'risk_score_changed': False}
        updated_metrics = session.security_metrics
        
        try:
            # Check for IP address changes
            if current_ip != session.ip_address:
                # Allow some flexibility for mobile users and load balancers
                if not self._is_acceptable_ip_change(session.ip_address, current_ip):
                    updated_metrics.location_changes += 1
                    updated_metrics.risk_score += 0.2
                    
                    if updated_metrics.risk_score > self.suspicious_threshold:
                        session.status = SessionStatus.SUSPICIOUS
                        result['valid'] = False
                        result['reason'] = "Suspicious IP address change"
                        
                        self._log_security_event(
                            session_id=session.session_id,
                            user_id=session.user_id,
                            event_type=SecurityEvent.LOCATION_CHANGE.value,
                            description=f"IP changed from {session.ip_address} to {current_ip}",
                            risk_level=RiskLevel.HIGH,
                            ip_address=current_ip,
                            user_agent=current_user_agent
                        )
                        
                        return result
            
            # Check for user agent changes
            if current_user_agent != session.user_agent:
                # Parse new user agent
                current_device = self._parse_device_info(current_user_agent, {})
                
                # Check if it's a significantly different device
                if not self._is_similar_device(session.device_info, current_device):
                    updated_metrics.device_changes += 1
                    updated_metrics.risk_score += 0.3
                    
                    if updated_metrics.risk_score > self.suspicious_threshold:
                        session.status = SessionStatus.SUSPICIOUS
                        result['valid'] = False
                        result['reason'] = "Suspicious device change"
                        
                        self._log_security_event(
                            session_id=session.session_id,
                            user_id=session.user_id,
                            event_type=SecurityEvent.DEVICE_CHANGE.value,
                            description="Significant device fingerprint change detected",
                            risk_level=RiskLevel.HIGH,
                            ip_address=current_ip,
                            user_agent=current_user_agent
                        )
                        
                        return result
            
            # Check idle timeout
            idle_time = datetime.now(timezone.utc) - session.last_activity_at
            if idle_time > self.idle_timeout:
                result['valid'] = False
                result['reason'] = "Session idle timeout exceeded"
                return result
            
            # Update metrics if changed
            if updated_metrics != session.security_metrics:
                result['risk_score_changed'] = True
                result['updated_metrics'] = updated_metrics
            
            return result
            
        except Exception as e:
            logger.error(f"Error performing security checks: {e}")
            return {'valid': False, 'reason': 'Security check error'}
    
    def _is_acceptable_ip_change(self, old_ip: str, new_ip: str) -> bool:
        """Check if IP address change is acceptable"""
        try:
            old_ip_obj = ipaddress.ip_address(old_ip)
            new_ip_obj = ipaddress.ip_address(new_ip)
            
            # Allow changes within private networks
            if old_ip_obj.is_private and new_ip_obj.is_private:
                return True
            
            # Allow changes within the same /24 subnet for IPv4
            if isinstance(old_ip_obj, ipaddress.IPv4Address) and isinstance(new_ip_obj, ipaddress.IPv4Address):
                old_network = ipaddress.IPv4Network(f"{old_ip}/24", strict=False)
                return new_ip_obj in old_network
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking IP change acceptability: {e}")
            return False
    
    def _is_similar_device(self, device1: DeviceInfo, device2: DeviceInfo) -> bool:
        """Check if two devices are similar enough"""
        # Compare key device characteristics
        return (device1.device_type == device2.device_type and
                device1.os_name == device2.os_name and
                device1.browser_name == device2.browser_name)
    
    def _handle_brute_force_detection(self, user_id: str, ip_address: str, user_agent: str, attempt_count: int):
        """Handle brute force attack detection"""
        try:
            # Log brute force detection
            self._log_security_event(
                session_id=None,
                user_id=user_id,
                event_type=SecurityEvent.BRUTE_FORCE_DETECTED.value,
                description=f"Brute force attack detected: {attempt_count} failed attempts",
                risk_level=RiskLevel.CRITICAL,
                ip_address=ip_address,
                user_agent=user_agent,
                additional_data={'attempt_count': attempt_count}
            )
            
            # Revoke all user sessions
            self.revoke_all_user_sessions(user_id, reason="Brute force attack detected")
            
            logger.warning(f"Brute force attack detected for user {user_id} from {ip_address}")
            
        except Exception as e:
            logger.error(f"Error handling brute force detection: {e}")
    
    def _enforce_concurrent_session_limits(self, user_id: str, new_session_id: str):
        """Enforce concurrent session limits"""
        try:
            if not self.redis_client:
                return
            
            active_sessions = self.get_user_sessions(user_id, active_only=True)
            
            if len(active_sessions) >= self.max_concurrent_sessions:
                # Remove oldest sessions
                sessions_to_remove = len(active_sessions) - self.max_concurrent_sessions + 1
                sessions_by_activity = sorted(active_sessions, key=lambda s: s.last_activity_at)
                
                for session in sessions_by_activity[:sessions_to_remove]:
                    self.revoke_session(session.session_id, "Concurrent session limit exceeded")
            
        except Exception as e:
            logger.error(f"Error enforcing concurrent session limits: {e}")
    
    def _store_session(self, session: SessionData):
        """Store session data in Redis"""
        try:
            if not self.redis_client:
                return
            
            # Serialize session data
            session_dict = asdict(session)
            session_dict['status'] = session.status.value
            session_dict['created_at'] = session.created_at.isoformat()
            session_dict['last_activity_at'] = session.last_activity_at.isoformat()
            session_dict['expires_at'] = session.expires_at.isoformat()
            session_dict['device_info']['device_type'] = session.device_info.device_type.value
            session_dict['security_metrics']['risk_level'] = session.security_metrics.risk_level.value
            if session.security_metrics.last_activity_at:
                session_dict['security_metrics']['last_activity_at'] = session.security_metrics.last_activity_at.isoformat()
            
            # Encrypt and store
            session_json = json.dumps(session_dict)
            encrypted_data = self._encrypt_session_data(session_json)
            
            key = f"session:{session.session_id}"
            self.redis_client.set(key, encrypted_data)
            
        except Exception as e:
            logger.error(f"Error storing session: {e}")
    
    def _deserialize_session(self, session_dict: Dict[str, Any]) -> SessionData:
        """Deserialize session data from dictionary"""
        return SessionData(
            session_id=session_dict['session_id'],
            user_id=session_dict['user_id'],
            status=SessionStatus(session_dict['status']),
            created_at=datetime.fromisoformat(session_dict['created_at']),
            last_activity_at=datetime.fromisoformat(session_dict['last_activity_at']),
            expires_at=datetime.fromisoformat(session_dict['expires_at']),
            device_info=DeviceInfo(
                device_id=session_dict['device_info']['device_id'],
                device_type=DeviceType(session_dict['device_info']['device_type']),
                os_name=session_dict['device_info'].get('os_name'),
                os_version=session_dict['device_info'].get('os_version'),
                browser_name=session_dict['device_info'].get('browser_name'),
                browser_version=session_dict['device_info'].get('browser_version'),
                screen_resolution=session_dict['device_info'].get('screen_resolution'),
                timezone=session_dict['device_info'].get('timezone'),
                language=session_dict['device_info'].get('language'),
                is_mobile=session_dict['device_info'].get('is_mobile', False),
                is_bot=session_dict['device_info'].get('is_bot', False),
                fingerprint=session_dict['device_info'].get('fingerprint')
            ),
            location_info=LocationInfo(
                ip_address=session_dict['location_info']['ip_address'],
                country=session_dict['location_info'].get('country'),
                country_code=session_dict['location_info'].get('country_code'),
                region=session_dict['location_info'].get('region'),
                city=session_dict['location_info'].get('city'),
                latitude=session_dict['location_info'].get('latitude'),
                longitude=session_dict['location_info'].get('longitude'),
                timezone=session_dict['location_info'].get('timezone'),
                isp=session_dict['location_info'].get('isp'),
                is_vpn=session_dict['location_info'].get('is_vpn', False),
                is_proxy=session_dict['location_info'].get('is_proxy', False)
            ),
            security_metrics=SecurityMetrics(
                risk_score=session_dict['security_metrics']['risk_score'],
                risk_level=RiskLevel(session_dict['security_metrics']['risk_level']),
                failed_login_attempts=session_dict['security_metrics'].get('failed_login_attempts', 0),
                suspicious_activities=session_dict['security_metrics'].get('suspicious_activities', 0),
                device_changes=session_dict['security_metrics'].get('device_changes', 0),
                location_changes=session_dict['security_metrics'].get('location_changes', 0),
                concurrent_sessions=session_dict['security_metrics'].get('concurrent_sessions', 0),
                last_activity_at=datetime.fromisoformat(session_dict['security_metrics']['last_activity_at']) if session_dict['security_metrics'].get('last_activity_at') else None
            ),
            ip_address=session_dict['ip_address'],
            user_agent=session_dict['user_agent'],
            csrf_token=session_dict.get('csrf_token'),
            mfa_verified=session_dict.get('mfa_verified', False),
            remember_me=session_dict.get('remember_me', False),
            metadata=session_dict.get('metadata', {})
        )
    
    def _encrypt_session_data(self, data: str) -> str:
        """Encrypt session data"""
        try:
            f = Fernet(self.encryption_key)
            encrypted = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Error encrypting session data: {e}")
            raise
    
    def _decrypt_session_data(self, encrypted_data: str) -> str:
        """Decrypt session data"""
        try:
            f = Fernet(self.encryption_key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error decrypting session data: {e}")
            raise
    
    def _expire_session(self, session_id: str):
        """Mark session as expired and clean up"""
        try:
            if self.redis_client:
                session = self.get_session(session_id)
                if session:
                    # Remove from active sessions
                    self.redis_client.srem(f"sessions:user:{session.user_id}", session_id)
                    
                    # Log expiration
                    self._log_security_event(
                        session_id=session_id,
                        user_id=session.user_id,
                        event_type=SecurityEvent.SESSION_EXPIRED.value,
                        description="Session expired",
                        risk_level=RiskLevel.LOW,
                        ip_address=session.ip_address,
                        user_agent=session.user_agent
                    )
                
                # Remove session data
                self.redis_client.delete(f"session:{session_id}")
                
        except Exception as e:
            logger.error(f"Error expiring session {session_id}: {e}")
    
    def _log_security_event(self, 
                          session_id: Optional[str], 
                          user_id: Optional[str],
                          event_type: str, 
                          description: str,
                          risk_level: RiskLevel, 
                          ip_address: str, 
                          user_agent: str,
                          additional_data: Dict[str, Any] = None):
        """Log security event for audit purposes"""
        try:
            if not self.config.get('enable_security_monitoring'):
                return
            
            event = {
                'event_id': secrets.token_urlsafe(8),
                'session_id': session_id,
                'user_id': user_id,
                'event_type': event_type,
                'description': description,
                'risk_level': risk_level.value,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'additional_data': additional_data or {}
            }
            
            if self.redis_client:
                # Store with TTL (e.g., 90 days)
                key = f"security_event:{datetime.now(timezone.utc).strftime('%Y%m%d')}:{event['event_id']}"
                self.redis_client.setex(key, 86400 * 90, json.dumps(event))
                
        except Exception as e:
            logger.error(f"Error logging security event: {e}")


# Utility functions

def create_session_manager(config: Dict[str, Any] = None) -> SessionManager:
    """Factory function to create session manager"""
    return SessionManager(config)
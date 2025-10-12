"""
AdCopySurge Enhanced JWT Security Implementation
Comprehensive JWT handling with security best practices, token rotation, and blacklisting
"""

import os
import jwt
import redis
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import json
import ipaddress
from user_agents import parse
import geoip2.database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"
    VERIFY = "verify"
    API = "api"

class TokenStatus(Enum):
    VALID = "valid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    BLACKLISTED = "blacklisted"
    INVALID = "invalid"

@dataclass
class TokenMetadata:
    """Token metadata for security tracking"""
    jti: str  # JWT ID
    user_id: str
    token_type: TokenType
    issued_at: datetime
    expires_at: datetime
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    permissions: List[str] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []

@dataclass
class SecurityContext:
    """Security context for token validation"""
    ip_address: str
    user_agent: str
    device_fingerprint: str
    location: Optional[Dict[str, Any]] = None
    suspicious_activity: bool = False
    risk_score: float = 0.0

class JWTSecurityManager:
    """Enhanced JWT security manager with advanced security features"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.redis_client = self._init_redis()
        self.geoip_reader = self._init_geoip()
        
        # Security settings
        self.access_token_lifetime = timedelta(minutes=self.config.get('access_token_minutes', 15))
        self.refresh_token_lifetime = timedelta(days=self.config.get('refresh_token_days', 7))
        self.reset_token_lifetime = timedelta(hours=self.config.get('reset_token_hours', 1))
        self.api_token_lifetime = timedelta(days=self.config.get('api_token_days', 30))
        
        # Security thresholds
        self.max_tokens_per_user = self.config.get('max_tokens_per_user', 10)
        self.suspicious_login_threshold = self.config.get('suspicious_login_threshold', 5)
        self.location_change_risk_score = self.config.get('location_change_risk_score', 0.7)
        
        # JWT settings
        self.algorithm = 'HS256'
        self.secret_key = self._get_secret_key()
        self.issuer = self.config.get('issuer', 'adcopysurge.com')
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default JWT security configuration"""
        return {
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
            'secret_key': os.getenv('JWT_SECRET_KEY'),
            'access_token_minutes': 15,
            'refresh_token_days': 7,
            'reset_token_hours': 1,
            'api_token_days': 30,
            'max_tokens_per_user': 10,
            'suspicious_login_threshold': 5,
            'location_change_risk_score': 0.7,
            'issuer': 'adcopysurge.com',
            'geoip_database_path': '/usr/share/GeoIP/GeoLite2-City.mmdb',
            'enable_device_tracking': True,
            'enable_location_tracking': True,
            'enable_risk_analysis': True
        }
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for token management"""
        try:
            client = redis.from_url(self.config['redis_url'], decode_responses=True)
            client.ping()
            return client
        except Exception as e:
            logger.warning(f"Redis not available for JWT security: {e}")
            return None
    
    def _init_geoip(self) -> Optional[Any]:
        """Initialize GeoIP database for location tracking"""
        try:
            geoip_path = self.config.get('geoip_database_path')
            if geoip_path and os.path.exists(geoip_path):
                return geoip2.database.Reader(geoip_path)
        except Exception as e:
            logger.warning(f"GeoIP database not available: {e}")
        return None
    
    def _get_secret_key(self) -> str:
        """Get or generate JWT secret key"""
        secret_key = self.config.get('secret_key')
        if not secret_key:
            # Generate a secure secret key if not provided
            secret_key = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
            logger.warning("JWT secret key not configured, using generated key (not persistent)")
        return secret_key
    
    def create_token(self, 
                    user_id: str, 
                    token_type: TokenType, 
                    security_context: SecurityContext,
                    permissions: List[str] = None,
                    custom_claims: Dict[str, Any] = None) -> Tuple[str, TokenMetadata]:
        """Create a secure JWT token with metadata"""
        
        # Generate unique token ID
        jti = self._generate_jti()
        now = datetime.now(timezone.utc)
        
        # Determine token lifetime
        lifetime_map = {
            TokenType.ACCESS: self.access_token_lifetime,
            TokenType.REFRESH: self.refresh_token_lifetime,
            TokenType.RESET: self.reset_token_lifetime,
            TokenType.API: self.api_token_lifetime,
            TokenType.VERIFY: timedelta(hours=24)
        }
        lifetime = lifetime_map.get(token_type, self.access_token_lifetime)
        expires_at = now + lifetime
        
        # Create token metadata
        metadata = TokenMetadata(
            jti=jti,
            user_id=user_id,
            token_type=token_type,
            issued_at=now,
            expires_at=expires_at,
            device_fingerprint=security_context.device_fingerprint,
            ip_address=security_context.ip_address,
            user_agent=security_context.user_agent,
            location=security_context.location,
            permissions=permissions or []
        )
        
        # Create JWT payload
        payload = {
            'jti': jti,
            'sub': user_id,  # Subject (user ID)
            'iss': self.issuer,  # Issuer
            'aud': 'adcopysurge-api',  # Audience
            'iat': int(now.timestamp()),  # Issued at
            'nbf': int(now.timestamp()),  # Not before
            'exp': int(expires_at.timestamp()),  # Expires at
            'type': token_type.value,
            'permissions': permissions or [],
            'device_fp': security_context.device_fingerprint,
            'ip': security_context.ip_address,
            'risk_score': security_context.risk_score
        }
        
        # Add custom claims
        if custom_claims:
            payload.update(custom_claims)
        
        # Generate JWT token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Store token metadata in Redis
        if self.redis_client:
            self._store_token_metadata(metadata)
            self._track_user_tokens(user_id, jti, token_type)
        
        # Log token creation
        logger.info(f"Created {token_type.value} token for user {user_id} from {security_context.ip_address}")
        
        return token, metadata
    
    def validate_token(self, 
                      token: str, 
                      security_context: SecurityContext,
                      expected_type: Optional[TokenType] = None,
                      check_permissions: List[str] = None) -> Tuple[TokenStatus, Optional[Dict[str, Any]]]:
        """Validate JWT token with comprehensive security checks"""
        
        try:
            # Decode token
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience='adcopysurge-api',
                issuer=self.issuer,
                options={"verify_exp": True, "verify_nbf": True}
            )
            
            jti = payload.get('jti')
            user_id = payload.get('sub')
            token_type_str = payload.get('type')
            
            if not all([jti, user_id, token_type_str]):
                return TokenStatus.INVALID, None
            
            # Check if token is blacklisted
            if self.redis_client and self.redis_client.sismember('jwt:blacklist', jti):
                logger.warning(f"Blacklisted token attempted: {jti}")
                return TokenStatus.BLACKLISTED, None
            
            # Verify token type if specified
            token_type = TokenType(token_type_str)
            if expected_type and token_type != expected_type:
                return TokenStatus.INVALID, None
            
            # Get stored metadata
            metadata = self._get_token_metadata(jti)
            if not metadata:
                logger.warning(f"Token metadata not found: {jti}")
                return TokenStatus.INVALID, None
            
            # Security context validation
            if not self._validate_security_context(payload, security_context, metadata):
                return TokenStatus.INVALID, None
            
            # Permission validation
            if check_permissions:
                token_permissions = payload.get('permissions', [])
                if not all(perm in token_permissions for perm in check_permissions):
                    logger.warning(f"Insufficient permissions for token {jti}")
                    return TokenStatus.INVALID, None
            
            # Update token usage
            if self.redis_client:
                self._update_token_usage(jti, security_context)
            
            return TokenStatus.VALID, payload
            
        except jwt.ExpiredSignatureError:
            logger.info("Token expired")
            return TokenStatus.EXPIRED, None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return TokenStatus.INVALID, None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return TokenStatus.INVALID, None
    
    def refresh_token(self, 
                     refresh_token: str, 
                     security_context: SecurityContext) -> Tuple[Optional[str], Optional[str], TokenStatus]:
        """Refresh access token using refresh token"""
        
        # Validate refresh token
        status, payload = self.validate_token(refresh_token, security_context, TokenType.REFRESH)
        
        if status != TokenStatus.VALID:
            return None, None, status
        
        user_id = payload['sub']
        permissions = payload.get('permissions', [])
        
        # Revoke old refresh token
        old_jti = payload['jti']
        self.revoke_token(old_jti, "Token refreshed")
        
        # Create new access token
        new_access_token, _ = self.create_token(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            security_context=security_context,
            permissions=permissions
        )
        
        # Create new refresh token
        new_refresh_token, _ = self.create_token(
            user_id=user_id,
            token_type=TokenType.REFRESH,
            security_context=security_context,
            permissions=permissions
        )
        
        logger.info(f"Tokens refreshed for user {user_id}")
        return new_access_token, new_refresh_token, TokenStatus.VALID
    
    def revoke_token(self, jti: str, reason: str = "Manual revocation"):
        """Revoke a specific token"""
        if self.redis_client:
            # Add to blacklist
            self.redis_client.sadd('jwt:blacklist', jti)
            self.redis_client.expire('jwt:blacklist', int(self.refresh_token_lifetime.total_seconds()))
            
            # Remove from active tokens
            metadata = self._get_token_metadata(jti)
            if metadata:
                self.redis_client.srem(f'jwt:user_tokens:{metadata["user_id"]}', jti)
                self.redis_client.delete(f'jwt:metadata:{jti}')
            
            logger.info(f"Token {jti} revoked: {reason}")
    
    def revoke_all_user_tokens(self, user_id: str, reason: str = "Revoke all tokens"):
        """Revoke all tokens for a specific user"""
        if self.redis_client:
            # Get all user tokens
            user_tokens = self.redis_client.smembers(f'jwt:user_tokens:{user_id}')
            
            for jti in user_tokens:
                self.revoke_token(jti, reason)
            
            logger.info(f"All tokens revoked for user {user_id}: {reason}")
    
    def create_security_context(self, 
                              ip_address: str, 
                              user_agent: str,
                              additional_headers: Dict[str, str] = None) -> SecurityContext:
        """Create security context from request information"""
        
        # Generate device fingerprint
        device_fingerprint = self._generate_device_fingerprint(ip_address, user_agent, additional_headers or {})
        
        # Get location information
        location = None
        if self.geoip_reader and self.config.get('enable_location_tracking'):
            location = self._get_location_info(ip_address)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(ip_address, user_agent, location, device_fingerprint)
        
        # Check for suspicious activity
        suspicious_activity = risk_score > 0.7
        
        return SecurityContext(
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            location=location,
            suspicious_activity=suspicious_activity,
            risk_score=risk_score
        )
    
    def get_user_active_tokens(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active tokens for a user"""
        active_tokens = []
        
        if self.redis_client:
            token_jti_list = self.redis_client.smembers(f'jwt:user_tokens:{user_id}')
            
            for jti in token_jti_list:
                metadata = self._get_token_metadata(jti)
                if metadata:
                    active_tokens.append(metadata)
        
        return active_tokens
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens and metadata"""
        if not self.redis_client:
            return
        
        try:
            # Get all token metadata keys
            metadata_keys = self.redis_client.keys('jwt:metadata:*')
            expired_count = 0
            
            for key in metadata_keys:
                metadata_str = self.redis_client.get(key)
                if metadata_str:
                    try:
                        metadata = json.loads(metadata_str)
                        expires_at = datetime.fromisoformat(metadata['expires_at'].replace('Z', '+00:00'))
                        
                        if expires_at < datetime.now(timezone.utc):
                            # Remove expired token metadata
                            jti = metadata['jti']
                            user_id = metadata['user_id']
                            
                            self.redis_client.delete(key)
                            self.redis_client.srem(f'jwt:user_tokens:{user_id}', jti)
                            self.redis_client.srem('jwt:blacklist', jti)
                            expired_count += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing token metadata {key}: {e}")
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired tokens")
                
        except Exception as e:
            logger.error(f"Error during token cleanup: {e}")
    
    # Private helper methods
    
    def _generate_jti(self) -> str:
        """Generate unique JWT ID"""
        return secrets.token_urlsafe(32)
    
    def _generate_device_fingerprint(self, ip_address: str, user_agent: str, headers: Dict[str, str]) -> str:
        """Generate device fingerprint for tracking"""
        fingerprint_data = f"{ip_address}|{user_agent}"
        
        # Add additional headers for more unique fingerprint
        for header in ['accept-language', 'accept-encoding', 'x-forwarded-for']:
            if header in headers:
                fingerprint_data += f"|{headers[header]}"
        
        # Create hash
        fingerprint_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()
        return fingerprint_hash[:16]  # Use first 16 characters
    
    def _get_location_info(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """Get location information from IP address"""
        try:
            if not self.geoip_reader:
                return None
            
            # Skip private IP addresses
            ip_obj = ipaddress.ip_address(ip_address)
            if ip_obj.is_private:
                return None
            
            response = self.geoip_reader.city(ip_address)
            return {
                'country': response.country.name,
                'country_code': response.country.iso_code,
                'city': response.city.name,
                'region': response.subdivisions.most_specific.name,
                'latitude': float(response.location.latitude) if response.location.latitude else None,
                'longitude': float(response.location.longitude) if response.location.longitude else None
            }
            
        except Exception as e:
            logger.debug(f"Could not get location for IP {ip_address}: {e}")
            return None
    
    def _calculate_risk_score(self, 
                            ip_address: str, 
                            user_agent: str, 
                            location: Optional[Dict[str, Any]], 
                            device_fingerprint: str) -> float:
        """Calculate risk score for the request"""
        risk_score = 0.0
        
        try:
            # Check IP address type
            ip_obj = ipaddress.ip_address(ip_address)
            if ip_obj.is_private:
                risk_score += 0.1  # Private IPs are generally safer
            else:
                risk_score += 0.3  # Public IPs have higher risk
            
            # Parse user agent
            user_agent_obj = parse(user_agent)
            if user_agent_obj.is_bot:
                risk_score += 0.5  # Bots are higher risk
            
            # Check for suspicious user agents
            suspicious_agents = ['curl', 'wget', 'python', 'scanner', 'bot']
            if any(agent in user_agent.lower() for agent in suspicious_agents):
                risk_score += 0.4
            
            # Location-based risk (if available)
            if location and self.redis_client:
                # Check if this is a new location for the device
                location_key = f"device_locations:{device_fingerprint}"
                known_countries = self.redis_client.smembers(location_key)
                
                if known_countries and location['country_code'] not in known_countries:
                    risk_score += self.location_change_risk_score
                
                # Store new location
                self.redis_client.sadd(location_key, location['country_code'])
                self.redis_client.expire(location_key, 86400 * 30)  # 30 days
            
            # Cap risk score at 1.0
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.5  # Default moderate risk
    
    def _validate_security_context(self, 
                                 payload: Dict[str, Any], 
                                 security_context: SecurityContext, 
                                 metadata: Dict[str, Any]) -> bool:
        """Validate security context against token metadata"""
        
        # Check IP address (allow some flexibility for mobile users)
        token_ip = payload.get('ip')
        if token_ip and self.config.get('strict_ip_validation', False):
            if token_ip != security_context.ip_address:
                logger.warning(f"IP address mismatch for token: {token_ip} vs {security_context.ip_address}")
                return False
        
        # Check device fingerprint
        token_device_fp = payload.get('device_fp')
        if token_device_fp and token_device_fp != security_context.device_fingerprint:
            # Allow some tolerance for device fingerprint changes
            if not self._is_similar_device_fingerprint(token_device_fp, security_context.device_fingerprint):
                logger.warning(f"Device fingerprint mismatch for token")
                return False
        
        # Check risk score
        if security_context.risk_score > 0.8:
            logger.warning(f"High risk score for token validation: {security_context.risk_score}")
            return False
        
        return True
    
    def _is_similar_device_fingerprint(self, fp1: str, fp2: str) -> bool:
        """Check if two device fingerprints are similar enough"""
        # Simple similarity check - could be enhanced with more sophisticated algorithms
        if len(fp1) != len(fp2):
            return False
        
        differences = sum(c1 != c2 for c1, c2 in zip(fp1, fp2))
        similarity = 1 - (differences / len(fp1))
        
        return similarity > 0.8  # 80% similarity threshold
    
    def _store_token_metadata(self, metadata: TokenMetadata):
        """Store token metadata in Redis"""
        if self.redis_client:
            metadata_dict = asdict(metadata)
            # Convert datetime objects to ISO strings
            metadata_dict['issued_at'] = metadata.issued_at.isoformat()
            metadata_dict['expires_at'] = metadata.expires_at.isoformat()
            metadata_dict['token_type'] = metadata.token_type.value
            
            key = f'jwt:metadata:{metadata.jti}'
            self.redis_client.setex(
                key, 
                int(self.refresh_token_lifetime.total_seconds()),
                json.dumps(metadata_dict)
            )
    
    def _get_token_metadata(self, jti: str) -> Optional[Dict[str, Any]]:
        """Get token metadata from Redis"""
        if self.redis_client:
            metadata_str = self.redis_client.get(f'jwt:metadata:{jti}')
            if metadata_str:
                return json.loads(metadata_str)
        return None
    
    def _track_user_tokens(self, user_id: str, jti: str, token_type: TokenType):
        """Track user tokens for management"""
        if self.redis_client:
            user_tokens_key = f'jwt:user_tokens:{user_id}'
            
            # Add new token
            self.redis_client.sadd(user_tokens_key, jti)
            self.redis_client.expire(user_tokens_key, int(self.refresh_token_lifetime.total_seconds()))
            
            # Check token limit
            token_count = self.redis_client.scard(user_tokens_key)
            if token_count > self.max_tokens_per_user:
                # Remove oldest tokens (this is simplified - in production, you'd want more sophisticated cleanup)
                tokens_to_remove = token_count - self.max_tokens_per_user
                oldest_tokens = self.redis_client.spop(user_tokens_key, tokens_to_remove)
                
                for old_jti in oldest_tokens:
                    self.revoke_token(old_jti, "Token limit exceeded")
    
    def _update_token_usage(self, jti: str, security_context: SecurityContext):
        """Update token usage statistics"""
        if self.redis_client:
            usage_key = f'jwt:usage:{jti}'
            usage_data = {
                'last_used': datetime.now(timezone.utc).isoformat(),
                'ip_address': security_context.ip_address,
                'user_agent': security_context.user_agent,
                'risk_score': security_context.risk_score
            }
            
            self.redis_client.setex(usage_key, 3600, json.dumps(usage_data))  # 1 hour TTL


# Utility functions for integration

def create_jwt_security_manager(config: Dict[str, Any] = None) -> JWTSecurityManager:
    """Factory function to create JWT security manager"""
    return JWTSecurityManager(config)

def get_token_from_header(authorization_header: str) -> Optional[str]:
    """Extract JWT token from Authorization header"""
    if not authorization_header:
        return None
    
    parts = authorization_header.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]
    
    return None
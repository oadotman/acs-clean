"""
AdCopySurge Multi-Factor Authentication (MFA) System
Comprehensive MFA implementation with TOTP, backup codes, and security key support
"""

import os
import secrets
import base64
import pyotp
import qrcode
import io
import json
import redis
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import hashlib
import struct
import base58
from webauthn import generate_registration_options, verify_registration_response
from webauthn import generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AuthenticatorAttachment,
    ResidentKeyRequirement,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MFAMethod(Enum):
    TOTP = "totp"
    BACKUP_CODES = "backup_codes"
    SECURITY_KEY = "security_key"
    SMS = "sms"
    EMAIL = "email"
    APP_NOTIFICATION = "app_notification"

class MFAStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    PENDING_SETUP = "pending_setup"
    LOCKED = "locked"

@dataclass
class MFADevice:
    """MFA device information"""
    device_id: str
    user_id: str
    method: MFAMethod
    name: str
    secret: Optional[str] = None
    backup_codes: Optional[List[str]] = None
    public_key: Optional[str] = None
    credential_id: Optional[str] = None
    counter: int = 0
    created_at: datetime = None
    last_used: Optional[datetime] = None
    status: MFAStatus = MFAStatus.ENABLED
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MFAChallenge:
    """MFA challenge information"""
    challenge_id: str
    user_id: str
    method: MFAMethod
    challenge_data: Dict[str, Any]
    created_at: datetime
    expires_at: datetime
    attempts: int = 0
    max_attempts: int = 3
    
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at
    
    def is_locked(self) -> bool:
        return self.attempts >= self.max_attempts

class MFAManager:
    """Comprehensive MFA management system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.redis_client = self._init_redis()
        self.encryption_key = self._get_encryption_key()
        
        # MFA settings
        self.totp_issuer = self.config.get('totp_issuer', 'AdCopySurge')
        self.totp_period = self.config.get('totp_period', 30)
        self.totp_digits = self.config.get('totp_digits', 6)
        self.backup_codes_count = self.config.get('backup_codes_count', 10)
        self.challenge_timeout = self.config.get('challenge_timeout_minutes', 5)
        
        # WebAuthn settings
        self.webauthn_rp_id = self.config.get('webauthn_rp_id', 'adcopysurge.com')
        self.webauthn_rp_name = self.config.get('webauthn_rp_name', 'AdCopySurge')
        self.webauthn_origin = self.config.get('webauthn_origin', 'https://adcopysurge.com')
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default MFA configuration"""
        return {
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/2'),
            'encryption_key': os.getenv('MFA_ENCRYPTION_KEY'),
            'totp_issuer': 'AdCopySurge',
            'totp_period': 30,
            'totp_digits': 6,
            'backup_codes_count': 10,
            'challenge_timeout_minutes': 5,
            'max_devices_per_user': 10,
            'require_mfa_for_admin': True,
            'allow_recovery_codes': True,
            'webauthn_rp_id': 'adcopysurge.com',
            'webauthn_rp_name': 'AdCopySurge',
            'webauthn_origin': 'https://adcopysurge.com',
        }
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for MFA data"""
        try:
            client = redis.from_url(self.config['redis_url'], decode_responses=True)
            client.ping()
            return client
        except Exception as e:
            logger.warning(f"Redis not available for MFA: {e}")
            return None
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for MFA secrets"""
        key_str = self.config.get('encryption_key')
        if key_str:
            return base64.urlsafe_b64decode(key_str.encode())
        else:
            # Generate a new key (in production, this should be persistent)
            key = Fernet.generate_key()
            logger.warning("MFA encryption key not configured, using generated key (not persistent)")
            return key
    
    # TOTP (Time-based One-Time Password) Methods
    
    def setup_totp(self, user_id: str, device_name: str = "Authenticator App") -> Dict[str, Any]:
        """Set up TOTP for a user"""
        # Generate secret
        secret = pyotp.random_base32()
        
        # Create TOTP instance
        totp = pyotp.TOTP(secret, issuer=self.totp_issuer, digits=self.totp_digits, interval=self.totp_period)
        
        # Generate QR code
        provisioning_uri = totp.provisioning_uri(
            name=f"{user_id}@{self.totp_issuer.lower()}",
            issuer_name=self.totp_issuer
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Generate QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format='PNG')
        qr_code_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Create MFA device (pending setup)
        device = MFADevice(
            device_id=self._generate_device_id(),
            user_id=user_id,
            method=MFAMethod.TOTP,
            name=device_name,
            secret=self._encrypt_secret(secret),
            status=MFAStatus.PENDING_SETUP
        )
        
        # Store device temporarily (until verified)
        if self.redis_client:
            self._store_pending_device(device)
        
        logger.info(f"TOTP setup initiated for user {user_id}")
        
        return {
            'device_id': device.device_id,
            'secret': secret,  # Return plaintext secret for manual entry
            'qr_code': qr_code_base64,
            'provisioning_uri': provisioning_uri,
            'backup_codes': None  # Will be generated after verification
        }
    
    def verify_totp_setup(self, user_id: str, device_id: str, token: str) -> Tuple[bool, Optional[List[str]]]:
        """Verify TOTP setup with provided token"""
        device = self._get_pending_device(device_id)
        if not device or device.user_id != user_id or device.method != MFAMethod.TOTP:
            return False, None
        
        # Decrypt secret
        secret = self._decrypt_secret(device.secret)
        
        # Verify token
        totp = pyotp.TOTP(secret, digits=self.totp_digits, interval=self.totp_period)
        
        if totp.verify(token, valid_window=1):  # Allow 1 time step tolerance
            # Generate backup codes
            backup_codes = self._generate_backup_codes()
            
            # Update device status and add backup codes
            device.status = MFAStatus.ENABLED
            device.backup_codes = [self._hash_backup_code(code) for code in backup_codes]
            
            # Store the device permanently
            if self.redis_client:
                self._store_mfa_device(device)
                self._remove_pending_device(device_id)
            
            logger.info(f"TOTP setup completed for user {user_id}")
            return True, backup_codes
        
        return False, None
    
    def validate_totp(self, user_id: str, device_id: str, token: str) -> bool:
        """Validate TOTP token"""
        device = self._get_mfa_device(device_id)
        if not device or device.user_id != user_id or device.method != MFAMethod.TOTP:
            return False
        
        if device.status != MFAStatus.ENABLED:
            return False
        
        # Decrypt secret
        secret = self._decrypt_secret(device.secret)
        
        # Verify token
        totp = pyotp.TOTP(secret, digits=self.totp_digits, interval=self.totp_period)
        
        if totp.verify(token, valid_window=1):
            # Update last used timestamp
            device.last_used = datetime.now(timezone.utc)
            if self.redis_client:
                self._store_mfa_device(device)
            
            logger.info(f"TOTP validation successful for user {user_id}, device {device_id}")
            return True
        
        return False
    
    # Backup Codes Methods
    
    def regenerate_backup_codes(self, user_id: str) -> List[str]:
        """Regenerate backup codes for a user"""
        backup_codes = self._generate_backup_codes()
        
        # Find user's devices and update backup codes
        user_devices = self.get_user_devices(user_id)
        for device in user_devices:
            if device.method in [MFAMethod.TOTP, MFAMethod.BACKUP_CODES]:
                device.backup_codes = [self._hash_backup_code(code) for code in backup_codes]
                if self.redis_client:
                    self._store_mfa_device(device)
        
        logger.info(f"Backup codes regenerated for user {user_id}")
        return backup_codes
    
    def validate_backup_code(self, user_id: str, code: str) -> bool:
        """Validate backup code"""
        user_devices = self.get_user_devices(user_id)
        
        for device in user_devices:
            if device.backup_codes:
                code_hash = self._hash_backup_code(code)
                if code_hash in device.backup_codes:
                    # Remove used backup code
                    device.backup_codes.remove(code_hash)
                    device.last_used = datetime.now(timezone.utc)
                    
                    if self.redis_client:
                        self._store_mfa_device(device)
                    
                    logger.info(f"Backup code used for user {user_id}")
                    return True
        
        return False
    
    # Security Key (WebAuthn) Methods
    
    def setup_security_key(self, user_id: str, device_name: str = "Security Key") -> Dict[str, Any]:
        """Set up WebAuthn security key"""
        try:
            # Generate registration options
            options = generate_registration_options(
                rp_id=self.webauthn_rp_id,
                rp_name=self.webauthn_rp_name,
                user_id=user_id.encode('utf-8'),
                user_name=f"user_{user_id}",
                user_display_name=f"User {user_id}",
                authenticator_selection=AuthenticatorSelectionCriteria(
                    authenticator_attachment=AuthenticatorAttachment.CROSS_PLATFORM,
                    user_verification=UserVerificationRequirement.PREFERRED,
                    resident_key=ResidentKeyRequirement.PREFERRED,
                )
            )
            
            # Create pending challenge
            challenge = MFAChallenge(
                challenge_id=self._generate_challenge_id(),
                user_id=user_id,
                method=MFAMethod.SECURITY_KEY,
                challenge_data={
                    'challenge': base64.urlsafe_b64encode(options.challenge).decode(),
                    'device_name': device_name,
                    'options': options.__dict__
                },
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=self.challenge_timeout)
            )
            
            if self.redis_client:
                self._store_challenge(challenge)
            
            logger.info(f"Security key setup initiated for user {user_id}")
            
            return {
                'challenge_id': challenge.challenge_id,
                'options': options.__dict__
            }
            
        except Exception as e:
            logger.error(f"Error setting up security key for user {user_id}: {e}")
            raise
    
    def verify_security_key_setup(self, challenge_id: str, credential_response: Dict[str, Any]) -> bool:
        """Verify security key setup"""
        try:
            challenge = self._get_challenge(challenge_id)
            if not challenge or challenge.method != MFAMethod.SECURITY_KEY:
                return False
            
            if challenge.is_expired():
                self._remove_challenge(challenge_id)
                return False
            
            # Verify registration response
            verification = verify_registration_response(
                credential=credential_response,
                expected_challenge=base64.urlsafe_b64decode(challenge.challenge_data['challenge']),
                expected_origin=self.webauthn_origin,
                expected_rp_id=self.webauthn_rp_id,
            )
            
            if verification.verified:
                # Create MFA device
                device = MFADevice(
                    device_id=self._generate_device_id(),
                    user_id=challenge.user_id,
                    method=MFAMethod.SECURITY_KEY,
                    name=challenge.challenge_data['device_name'],
                    credential_id=base64.urlsafe_b64encode(verification.credential_id).decode(),
                    public_key=base64.urlsafe_b64encode(verification.credential_public_key).decode(),
                    counter=verification.sign_count,
                    status=MFAStatus.ENABLED
                )
                
                if self.redis_client:
                    self._store_mfa_device(device)
                    self._remove_challenge(challenge_id)
                
                logger.info(f"Security key setup completed for user {challenge.user_id}")
                return True
            
        except Exception as e:
            logger.error(f"Error verifying security key setup: {e}")
        
        return False
    
    def create_security_key_challenge(self, user_id: str) -> Dict[str, Any]:
        """Create authentication challenge for security key"""
        try:
            # Get user's security keys
            devices = [d for d in self.get_user_devices(user_id) if d.method == MFAMethod.SECURITY_KEY]
            
            if not devices:
                raise ValueError("No security keys registered for user")
            
            # Create allowed credentials
            allowed_credentials = []
            for device in devices:
                allowed_credentials.append({
                    'id': base64.urlsafe_b64decode(device.credential_id),
                    'type': 'public-key'
                })
            
            # Generate authentication options
            options = generate_authentication_options(
                rp_id=self.webauthn_rp_id,
                allow_credentials=allowed_credentials,
                user_verification=UserVerificationRequirement.PREFERRED
            )
            
            # Create challenge
            challenge = MFAChallenge(
                challenge_id=self._generate_challenge_id(),
                user_id=user_id,
                method=MFAMethod.SECURITY_KEY,
                challenge_data={
                    'challenge': base64.urlsafe_b64encode(options.challenge).decode(),
                    'options': options.__dict__
                },
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=self.challenge_timeout)
            )
            
            if self.redis_client:
                self._store_challenge(challenge)
            
            return {
                'challenge_id': challenge.challenge_id,
                'options': options.__dict__
            }
            
        except Exception as e:
            logger.error(f"Error creating security key challenge for user {user_id}: {e}")
            raise
    
    def validate_security_key_response(self, challenge_id: str, credential_response: Dict[str, Any]) -> bool:
        """Validate security key authentication response"""
        try:
            challenge = self._get_challenge(challenge_id)
            if not challenge or challenge.method != MFAMethod.SECURITY_KEY:
                return False
            
            if challenge.is_expired():
                self._remove_challenge(challenge_id)
                return False
            
            # Find the device
            credential_id = credential_response.get('id', '')
            device = None
            
            for d in self.get_user_devices(challenge.user_id):
                if d.method == MFAMethod.SECURITY_KEY and d.credential_id == credential_id:
                    device = d
                    break
            
            if not device:
                return False
            
            # Verify authentication response
            verification = verify_authentication_response(
                credential=credential_response,
                expected_challenge=base64.urlsafe_b64decode(challenge.challenge_data['challenge']),
                expected_origin=self.webauthn_origin,
                expected_rp_id=self.webauthn_rp_id,
                credential_public_key=base64.urlsafe_b64decode(device.public_key),
                credential_current_sign_count=device.counter,
            )
            
            if verification.verified:
                # Update counter
                device.counter = verification.new_sign_count
                device.last_used = datetime.now(timezone.utc)
                
                if self.redis_client:
                    self._store_mfa_device(device)
                    self._remove_challenge(challenge_id)
                
                logger.info(f"Security key validation successful for user {challenge.user_id}")
                return True
            
        except Exception as e:
            logger.error(f"Error validating security key response: {e}")
        
        return False
    
    # Device Management Methods
    
    def get_user_devices(self, user_id: str) -> List[MFADevice]:
        """Get all MFA devices for a user"""
        devices = []
        
        if self.redis_client:
            device_keys = self.redis_client.keys(f'mfa:device:{user_id}:*')
            
            for key in device_keys:
                device_data = self.redis_client.get(key)
                if device_data:
                    device_dict = json.loads(device_data)
                    device = self._dict_to_mfa_device(device_dict)
                    if device and device.status == MFAStatus.ENABLED:
                        devices.append(device)
        
        return devices
    
    def remove_device(self, user_id: str, device_id: str) -> bool:
        """Remove an MFA device"""
        device = self._get_mfa_device(device_id)
        if not device or device.user_id != user_id:
            return False
        
        if self.redis_client:
            self.redis_client.delete(f'mfa:device:{user_id}:{device_id}')
        
        logger.info(f"MFA device {device_id} removed for user {user_id}")
        return True
    
    def is_mfa_enabled(self, user_id: str) -> bool:
        """Check if MFA is enabled for a user"""
        devices = self.get_user_devices(user_id)
        return len(devices) > 0
    
    def get_available_methods(self, user_id: str) -> List[MFAMethod]:
        """Get available MFA methods for a user"""
        devices = self.get_user_devices(user_id)
        methods = set()
        
        for device in devices:
            methods.add(device.method)
            if device.backup_codes:
                methods.add(MFAMethod.BACKUP_CODES)
        
        return list(methods)
    
    # General Validation Method
    
    def validate_mfa(self, user_id: str, method: MFAMethod, credential: Dict[str, Any]) -> bool:
        """General MFA validation method"""
        try:
            if method == MFAMethod.TOTP:
                device_id = credential.get('device_id')
                token = credential.get('token')
                return self.validate_totp(user_id, device_id, token)
            
            elif method == MFAMethod.BACKUP_CODES:
                code = credential.get('code')
                return self.validate_backup_code(user_id, code)
            
            elif method == MFAMethod.SECURITY_KEY:
                challenge_id = credential.get('challenge_id')
                response = credential.get('response')
                return self.validate_security_key_response(challenge_id, response)
            
            else:
                logger.warning(f"Unsupported MFA method: {method}")
                return False
                
        except Exception as e:
            logger.error(f"Error validating MFA for user {user_id}: {e}")
            return False
    
    # Recovery Methods
    
    def generate_recovery_token(self, user_id: str) -> str:
        """Generate a recovery token for MFA reset"""
        token = secrets.token_urlsafe(32)
        
        if self.redis_client:
            self.redis_client.setex(
                f'mfa:recovery:{token}',
                3600,  # 1 hour expiry
                json.dumps({
                    'user_id': user_id,
                    'created_at': datetime.now(timezone.utc).isoformat()
                })
            )
        
        logger.info(f"Recovery token generated for user {user_id}")
        return token
    
    def validate_recovery_token(self, token: str) -> Optional[str]:
        """Validate recovery token and return user ID"""
        if self.redis_client:
            data = self.redis_client.get(f'mfa:recovery:{token}')
            if data:
                recovery_data = json.loads(data)
                return recovery_data['user_id']
        
        return None
    
    def reset_user_mfa(self, user_id: str, recovery_token: str) -> bool:
        """Reset all MFA for a user using recovery token"""
        if not self.validate_recovery_token(recovery_token):
            return False
        
        # Remove all devices
        devices = self.get_user_devices(user_id)
        for device in devices:
            self.remove_device(user_id, device.device_id)
        
        # Remove recovery token
        if self.redis_client:
            self.redis_client.delete(f'mfa:recovery:{recovery_token}')
        
        logger.warning(f"MFA reset completed for user {user_id}")
        return True
    
    # Helper Methods
    
    def _generate_device_id(self) -> str:
        """Generate unique device ID"""
        return secrets.token_urlsafe(16)
    
    def _generate_challenge_id(self) -> str:
        """Generate unique challenge ID"""
        return secrets.token_urlsafe(16)
    
    def _generate_backup_codes(self) -> List[str]:
        """Generate backup codes"""
        codes = []
        for _ in range(self.backup_codes_count):
            code = ''.join(secrets.choice('0123456789') for _ in range(8))
            codes.append(f"{code[:4]}-{code[4:]}")  # Format as XXXX-XXXX
        return codes
    
    def _hash_backup_code(self, code: str) -> str:
        """Hash backup code for storage"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def _encrypt_secret(self, secret: str) -> str:
        """Encrypt MFA secret"""
        f = Fernet(self.encryption_key)
        encrypted = f.encrypt(secret.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def _decrypt_secret(self, encrypted_secret: str) -> str:
        """Decrypt MFA secret"""
        f = Fernet(self.encryption_key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_secret.encode())
        decrypted = f.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def _store_mfa_device(self, device: MFADevice):
        """Store MFA device in Redis"""
        if self.redis_client:
            device_dict = asdict(device)
            # Convert datetime objects to ISO strings
            device_dict['created_at'] = device.created_at.isoformat()
            if device.last_used:
                device_dict['last_used'] = device.last_used.isoformat()
            device_dict['method'] = device.method.value
            device_dict['status'] = device.status.value
            
            key = f'mfa:device:{device.user_id}:{device.device_id}'
            self.redis_client.set(key, json.dumps(device_dict))
    
    def _get_mfa_device(self, device_id: str) -> Optional[MFADevice]:
        """Get MFA device from Redis"""
        if self.redis_client:
            # Search across all users (this could be optimized with better key structure)
            keys = self.redis_client.keys(f'mfa:device:*:{device_id}')
            if keys:
                device_data = self.redis_client.get(keys[0])
                if device_data:
                    device_dict = json.loads(device_data)
                    return self._dict_to_mfa_device(device_dict)
        
        return None
    
    def _store_pending_device(self, device: MFADevice):
        """Store pending MFA device"""
        if self.redis_client:
            device_dict = asdict(device)
            device_dict['created_at'] = device.created_at.isoformat()
            device_dict['method'] = device.method.value
            device_dict['status'] = device.status.value
            
            key = f'mfa:pending:{device.device_id}'
            self.redis_client.setex(key, 300, json.dumps(device_dict))  # 5 minutes
    
    def _get_pending_device(self, device_id: str) -> Optional[MFADevice]:
        """Get pending MFA device"""
        if self.redis_client:
            device_data = self.redis_client.get(f'mfa:pending:{device_id}')
            if device_data:
                device_dict = json.loads(device_data)
                return self._dict_to_mfa_device(device_dict)
        
        return None
    
    def _remove_pending_device(self, device_id: str):
        """Remove pending MFA device"""
        if self.redis_client:
            self.redis_client.delete(f'mfa:pending:{device_id}')
    
    def _store_challenge(self, challenge: MFAChallenge):
        """Store MFA challenge"""
        if self.redis_client:
            challenge_dict = asdict(challenge)
            challenge_dict['created_at'] = challenge.created_at.isoformat()
            challenge_dict['expires_at'] = challenge.expires_at.isoformat()
            challenge_dict['method'] = challenge.method.value
            
            key = f'mfa:challenge:{challenge.challenge_id}'
            ttl = int((challenge.expires_at - datetime.now(timezone.utc)).total_seconds())
            self.redis_client.setex(key, ttl, json.dumps(challenge_dict))
    
    def _get_challenge(self, challenge_id: str) -> Optional[MFAChallenge]:
        """Get MFA challenge"""
        if self.redis_client:
            challenge_data = self.redis_client.get(f'mfa:challenge:{challenge_id}')
            if challenge_data:
                challenge_dict = json.loads(challenge_data)
                return MFAChallenge(
                    challenge_id=challenge_dict['challenge_id'],
                    user_id=challenge_dict['user_id'],
                    method=MFAMethod(challenge_dict['method']),
                    challenge_data=challenge_dict['challenge_data'],
                    created_at=datetime.fromisoformat(challenge_dict['created_at']),
                    expires_at=datetime.fromisoformat(challenge_dict['expires_at']),
                    attempts=challenge_dict['attempts'],
                    max_attempts=challenge_dict['max_attempts']
                )
        
        return None
    
    def _remove_challenge(self, challenge_id: str):
        """Remove MFA challenge"""
        if self.redis_client:
            self.redis_client.delete(f'mfa:challenge:{challenge_id}')
    
    def _dict_to_mfa_device(self, device_dict: Dict[str, Any]) -> Optional[MFADevice]:
        """Convert dictionary to MFADevice object"""
        try:
            return MFADevice(
                device_id=device_dict['device_id'],
                user_id=device_dict['user_id'],
                method=MFAMethod(device_dict['method']),
                name=device_dict['name'],
                secret=device_dict.get('secret'),
                backup_codes=device_dict.get('backup_codes'),
                public_key=device_dict.get('public_key'),
                credential_id=device_dict.get('credential_id'),
                counter=device_dict.get('counter', 0),
                created_at=datetime.fromisoformat(device_dict['created_at']),
                last_used=datetime.fromisoformat(device_dict['last_used']) if device_dict.get('last_used') else None,
                status=MFAStatus(device_dict['status']),
                metadata=device_dict.get('metadata', {})
            )
        except Exception as e:
            logger.error(f"Error converting dict to MFADevice: {e}")
            return None


# Utility functions

def create_mfa_manager(config: Dict[str, Any] = None) -> MFAManager:
    """Factory function to create MFA manager"""
    return MFAManager(config)
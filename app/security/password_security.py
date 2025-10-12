"""
AdCopySurge Advanced Password Security System
Comprehensive password security with strength validation, breach checking, and secure storage
"""

import os
import re
import hashlib
import secrets
import requests
import redis
import argon2
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import math
import string
import json
import zxcvbn
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PasswordStrength(Enum):
    VERY_WEAK = 0
    WEAK = 1
    FAIR = 2
    GOOD = 3
    STRONG = 4

class PasswordPolicy(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
    ENTERPRISE = "enterprise"

@dataclass
class PasswordStrengthResult:
    """Password strength analysis result"""
    score: int  # 0-4
    strength: PasswordStrength
    entropy: float
    feedback: List[str]
    suggestions: List[str]
    crack_time: str
    is_common: bool
    is_breached: Optional[bool] = None
    breach_count: Optional[int] = None

@dataclass
class PasswordHistoryEntry:
    """Password history entry"""
    password_hash: str
    created_at: datetime
    ip_address: str
    user_agent: str

class PasswordSecurityManager:
    """Advanced password security management system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.redis_client = self._init_redis()
        
        # Initialize Argon2 hasher
        self.argon2_hasher = argon2.PasswordHasher(
            time_cost=self.config.get('argon2_time_cost', 3),
            memory_cost=self.config.get('argon2_memory_cost', 102400),  # 100 MB
            parallelism=self.config.get('argon2_parallelism', 8),
            hash_len=self.config.get('argon2_hash_len', 32),
            salt_len=self.config.get('argon2_salt_len', 16)
        )
        
        # Password policies
        self.password_policies = self._load_password_policies()
        
        # Load common passwords and patterns
        self.common_passwords = self._load_common_passwords()
        self.keyboard_patterns = self._load_keyboard_patterns()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default password security configuration"""
        return {
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/3'),
            'hibp_api_enabled': True,  # Have I Been Pwned API
            'hibp_api_timeout': 5,
            'password_history_count': 12,  # Remember last 12 passwords
            'password_expiry_days': 90,
            'account_lockout_attempts': 5,
            'account_lockout_duration': 1800,  # 30 minutes
            'argon2_time_cost': 3,
            'argon2_memory_cost': 102400,  # 100 MB
            'argon2_parallelism': 8,
            'argon2_hash_len': 32,
            'argon2_salt_len': 16,
            'enable_password_strength_meter': True,
            'enable_breach_checking': True,
            'enable_common_password_check': True,
            'enable_personal_info_check': True,
            'min_entropy_bits': 50
        }
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for password data"""
        try:
            client = redis.from_url(self.config['redis_url'], decode_responses=True)
            client.ping()
            return client
        except Exception as e:
            logger.warning(f"Redis not available for password security: {e}")
            return None
    
    def _load_password_policies(self) -> Dict[PasswordPolicy, Dict[str, Any]]:
        """Load password policy configurations"""
        return {
            PasswordPolicy.BASIC: {
                'min_length': 8,
                'require_uppercase': False,
                'require_lowercase': False,
                'require_digits': False,
                'require_symbols': False,
                'max_length': 128,
                'min_entropy': 30,
                'allow_common_passwords': True,
                'require_breach_check': False
            },
            PasswordPolicy.STANDARD: {
                'min_length': 10,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_symbols': False,
                'max_length': 128,
                'min_entropy': 40,
                'allow_common_passwords': False,
                'require_breach_check': True
            },
            PasswordPolicy.STRICT: {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_symbols': True,
                'max_length': 128,
                'min_entropy': 50,
                'allow_common_passwords': False,
                'require_breach_check': True,
                'forbidden_patterns': ['123', 'abc', 'qwe', 'password']
            },
            PasswordPolicy.ENTERPRISE: {
                'min_length': 14,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_symbols': True,
                'max_length': 128,
                'min_entropy': 60,
                'allow_common_passwords': False,
                'require_breach_check': True,
                'forbidden_patterns': ['123', 'abc', 'qwe', 'password', 'admin'],
                'max_repeated_chars': 2,
                'min_unique_chars': 4
            }
        }
    
    def _load_common_passwords(self) -> set:
        """Load common passwords list"""
        # In production, load from a comprehensive list like SecLists or HaveIBeenPwned
        common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123', 
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'hello', 'freedom', 'whatever',
            'qazwsx', 'trustno1', '000000', '111111', '666666',
            '123123', '1234567890', 'superman', 'batman', 'football'
        }
        
        try:
            # Try to load from file if available
            common_passwords_file = self.config.get('common_passwords_file')
            if common_passwords_file and os.path.exists(common_passwords_file):
                with open(common_passwords_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        password = line.strip().lower()
                        if password:
                            common_passwords.add(password)
        except Exception as e:
            logger.warning(f"Could not load common passwords file: {e}")
        
        return common_passwords
    
    def _load_keyboard_patterns(self) -> List[str]:
        """Load keyboard pattern sequences"""
        return [
            # QWERTY rows
            'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
            # Number sequences
            '1234567890', '0987654321',
            # Common patterns
            'abcdefghijklmnopqrstuvwxyz',
            'zyxwvutsrqponmlkjihgfedcba'
        ]
    
    def hash_password(self, password: str, user_id: str = None) -> str:
        """Hash password using Argon2"""
        try:
            # Use Argon2id (hybrid) for maximum security
            hashed = self.argon2_hasher.hash(password)
            
            # Log password change (without the actual password)
            if user_id:
                logger.info(f"Password hashed for user {user_id}")
            
            return hashed
            
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    def verify_password(self, password: str, hashed_password: str, user_id: str = None) -> bool:
        """Verify password against hash using Argon2"""
        try:
            self.argon2_hasher.verify(hashed_password, password)
            
            # Check if rehashing is needed (parameters changed)
            if self.argon2_hasher.check_needs_rehash(hashed_password):
                logger.info(f"Password hash needs rehashing for user {user_id}")
                # Return a flag to indicate rehashing is needed
                return True
            
            return True
            
        except argon2.exceptions.VerifyMismatchError:
            return False
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def analyze_password_strength(self, password: str, user_info: Dict[str, str] = None) -> PasswordStrengthResult:
        """Comprehensive password strength analysis"""
        try:
            # Use zxcvbn for advanced password analysis
            zxcvbn_result = zxcvbn.zxcvbn(password, user_inputs=list(user_info.values()) if user_info else None)
            
            # Calculate entropy
            entropy = self._calculate_entropy(password)
            
            # Check if password is in common passwords list
            is_common = password.lower() in self.common_passwords
            
            # Collect feedback and suggestions
            feedback = []
            suggestions = []
            
            # Add zxcvbn feedback
            if zxcvbn_result.get('feedback'):
                zxcvbn_feedback = zxcvbn_result['feedback']
                if zxcvbn_feedback.get('warning'):
                    feedback.append(zxcvbn_feedback['warning'])
                if zxcvbn_feedback.get('suggestions'):
                    suggestions.extend(zxcvbn_feedback['suggestions'])
            
            # Add custom feedback
            custom_feedback = self._get_custom_feedback(password, user_info)
            feedback.extend(custom_feedback['feedback'])
            suggestions.extend(custom_feedback['suggestions'])
            
            # Determine strength
            score = zxcvbn_result['score']
            strength = PasswordStrength(score)
            
            # Format crack time
            crack_time = self._format_crack_time(zxcvbn_result.get('crack_times_seconds', {}).get('offline_slow_hashing_1e4_per_second', 0))
            
            result = PasswordStrengthResult(
                score=score,
                strength=strength,
                entropy=entropy,
                feedback=feedback,
                suggestions=suggestions,
                crack_time=crack_time,
                is_common=is_common
            )
            
            # Check for breaches if enabled
            if self.config.get('enable_breach_checking'):
                breach_info = self.check_password_breach(password)
                result.is_breached = breach_info['is_breached']
                result.breach_count = breach_info['count']
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing password strength: {e}")
            # Return a basic result
            return PasswordStrengthResult(
                score=0,
                strength=PasswordStrength.VERY_WEAK,
                entropy=0,
                feedback=["Unable to analyze password"],
                suggestions=["Please try again"],
                crack_time="Unknown",
                is_common=True
            )
    
    def validate_password_policy(self, password: str, policy: PasswordPolicy, user_info: Dict[str, str] = None) -> Tuple[bool, List[str]]:
        """Validate password against specified policy"""
        policy_config = self.password_policies[policy]
        errors = []
        
        # Length checks
        if len(password) < policy_config['min_length']:
            errors.append(f"Password must be at least {policy_config['min_length']} characters long")
        
        if len(password) > policy_config['max_length']:
            errors.append(f"Password must not exceed {policy_config['max_length']} characters")
        
        # Character requirements
        if policy_config.get('require_uppercase') and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if policy_config.get('require_lowercase') and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if policy_config.get('require_digits') and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        if policy_config.get('require_symbols') and not any(c in string.punctuation for c in password):
            errors.append("Password must contain at least one special character")
        
        # Entropy check
        entropy = self._calculate_entropy(password)
        if entropy < policy_config['min_entropy']:
            errors.append(f"Password is not complex enough (entropy: {entropy:.1f}, required: {policy_config['min_entropy']})")
        
        # Common password check
        if not policy_config.get('allow_common_passwords') and password.lower() in self.common_passwords:
            errors.append("Password is too common")
        
        # Forbidden patterns
        forbidden_patterns = policy_config.get('forbidden_patterns', [])
        for pattern in forbidden_patterns:
            if pattern.lower() in password.lower():
                errors.append(f"Password contains forbidden pattern: {pattern}")
        
        # Repeated characters check
        max_repeated = policy_config.get('max_repeated_chars')
        if max_repeated and self._has_excessive_repetition(password, max_repeated):
            errors.append(f"Password has too many repeated characters (max: {max_repeated})")
        
        # Unique characters check
        min_unique = policy_config.get('min_unique_chars')
        if min_unique and len(set(password)) < min_unique:
            errors.append(f"Password must have at least {min_unique} unique characters")
        
        # Personal information check
        if user_info and self.config.get('enable_personal_info_check'):
            personal_errors = self._check_personal_info(password, user_info)
            errors.extend(personal_errors)
        
        # Breach check
        if policy_config.get('require_breach_check') and self.config.get('enable_breach_checking'):
            breach_info = self.check_password_breach(password)
            if breach_info['is_breached']:
                errors.append(f"Password has been found in {breach_info['count']} data breaches")
        
        return len(errors) == 0, errors
    
    def check_password_breach(self, password: str) -> Dict[str, Any]:
        """Check if password has been in a data breach using HaveIBeenPwned API"""
        if not self.config.get('hibp_api_enabled'):
            return {'is_breached': False, 'count': 0}
        
        try:
            # Hash password with SHA-1
            sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            hash_prefix = sha1_hash[:5]
            hash_suffix = sha1_hash[5:]
            
            # Check cache first
            cache_key = f"password_breach:{hash_prefix}"
            if self.redis_client:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    cached_data = json.loads(cached_result)
                    if hash_suffix in cached_data:
                        return {
                            'is_breached': True,
                            'count': cached_data[hash_suffix]
                        }
                    else:
                        return {'is_breached': False, 'count': 0}
            
            # Query HaveIBeenPwned API
            url = f"https://api.pwnedpasswords.com/range/{hash_prefix}"
            headers = {
                'User-Agent': 'AdCopySurge-Password-Checker/1.0'
            }
            
            response = requests.get(
                url, 
                headers=headers,
                timeout=self.config.get('hibp_api_timeout', 5)
            )
            
            if response.status_code == 200:
                # Parse response
                breach_data = {}
                for line in response.text.splitlines():
                    suffix, count = line.split(':')
                    breach_data[suffix] = int(count)
                
                # Cache result
                if self.redis_client:
                    self.redis_client.setex(cache_key, 3600, json.dumps(breach_data))  # Cache for 1 hour
                
                # Check if our password hash suffix is in the results
                if hash_suffix in breach_data:
                    return {
                        'is_breached': True,
                        'count': breach_data[hash_suffix]
                    }
                else:
                    return {'is_breached': False, 'count': 0}
            
            else:
                logger.warning(f"HaveIBeenPwned API error: {response.status_code}")
                return {'is_breached': False, 'count': 0}
                
        except Exception as e:
            logger.error(f"Error checking password breach: {e}")
            return {'is_breached': False, 'count': 0}
    
    def store_password_history(self, user_id: str, password_hash: str, ip_address: str, user_agent: str):
        """Store password in user's password history"""
        if not self.redis_client:
            return
        
        try:
            history_key = f"password_history:{user_id}"
            
            # Create history entry
            entry = {
                'password_hash': password_hash,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'ip_address': ip_address,
                'user_agent': user_agent
            }
            
            # Add to history list
            self.redis_client.lpush(history_key, json.dumps(entry))
            
            # Trim to configured limit
            history_count = self.config.get('password_history_count', 12)
            self.redis_client.ltrim(history_key, 0, history_count - 1)
            
            # Set expiration (e.g., 2 years)
            self.redis_client.expire(history_key, 86400 * 730)
            
            logger.info(f"Password history updated for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error storing password history: {e}")
    
    def check_password_reuse(self, user_id: str, new_password: str) -> bool:
        """Check if password has been used before by the user"""
        if not self.redis_client:
            return False
        
        try:
            history_key = f"password_history:{user_id}"
            history = self.redis_client.lrange(history_key, 0, -1)
            
            for entry_json in history:
                entry = json.loads(entry_json)
                old_hash = entry['password_hash']
                
                # Verify against old password
                if self.verify_password(new_password, old_hash):
                    logger.info(f"Password reuse detected for user {user_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking password reuse: {e}")
            return False
    
    def generate_secure_password(self, length: int = 16, include_symbols: bool = True) -> str:
        """Generate a cryptographically secure password"""
        try:
            # Character sets
            lowercase = string.ascii_lowercase
            uppercase = string.ascii_uppercase
            digits = string.digits
            symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if include_symbols else ""
            
            # Ensure at least one character from each required set
            password_chars = [
                secrets.choice(lowercase),
                secrets.choice(uppercase),
                secrets.choice(digits)
            ]
            
            if include_symbols:
                password_chars.append(secrets.choice(symbols))
            
            # Fill remaining length
            all_chars = lowercase + uppercase + digits + symbols
            remaining_length = length - len(password_chars)
            
            for _ in range(remaining_length):
                password_chars.append(secrets.choice(all_chars))
            
            # Shuffle the password
            secrets.SystemRandom().shuffle(password_chars)
            
            return ''.join(password_chars)
            
        except Exception as e:
            logger.error(f"Error generating secure password: {e}")
            raise
    
    def get_password_suggestions(self, failed_password: str, policy: PasswordPolicy) -> List[str]:
        """Get specific suggestions for improving password"""
        suggestions = []
        policy_config = self.password_policies[policy]
        
        if len(failed_password) < policy_config['min_length']:
            suggestions.append(f"Make password at least {policy_config['min_length']} characters long")
        
        if policy_config.get('require_uppercase') and not any(c.isupper() for c in failed_password):
            suggestions.append("Add uppercase letters (A-Z)")
        
        if policy_config.get('require_lowercase') and not any(c.islower() for c in failed_password):
            suggestions.append("Add lowercase letters (a-z)")
        
        if policy_config.get('require_digits') and not any(c.isdigit() for c in failed_password):
            suggestions.append("Add numbers (0-9)")
        
        if policy_config.get('require_symbols') and not any(c in string.punctuation for c in failed_password):
            suggestions.append("Add special characters (!@#$%^&*)")
        
        # Entropy suggestions
        entropy = self._calculate_entropy(failed_password)
        if entropy < policy_config['min_entropy']:
            suggestions.append("Use a more random combination of characters")
            suggestions.append("Avoid common words and predictable patterns")
        
        # Add general suggestions
        suggestions.extend([
            "Consider using a passphrase with multiple words",
            "Use a password manager to generate and store secure passwords",
            "Avoid personal information like names, birthdays, or addresses"
        ])
        
        return suggestions
    
    # Private helper methods
    
    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits"""
        if not password:
            return 0
        
        # Determine character set size
        charset_size = 0
        if any(c.islower() for c in password):
            charset_size += 26  # lowercase
        if any(c.isupper() for c in password):
            charset_size += 26  # uppercase
        if any(c.isdigit() for c in password):
            charset_size += 10  # digits
        if any(c in string.punctuation for c in password):
            charset_size += len(string.punctuation)  # symbols
        if any(c.isspace() for c in password):
            charset_size += 1  # space
        
        # Calculate entropy: log2(charset_size^length)
        if charset_size > 0:
            entropy = len(password) * math.log2(charset_size)
            return entropy
        
        return 0
    
    def _get_custom_feedback(self, password: str, user_info: Dict[str, str] = None) -> Dict[str, List[str]]:
        """Get custom password feedback"""
        feedback = []
        suggestions = []
        
        # Check for keyboard patterns
        for pattern in self.keyboard_patterns:
            if self._contains_sequence(password.lower(), pattern, 4):
                feedback.append("Password contains keyboard patterns")
                suggestions.append("Avoid keyboard patterns like 'qwerty' or '123456'")
                break
        
        # Check for repeated characters
        if self._has_excessive_repetition(password, 3):
            feedback.append("Password has too many repeated characters")
            suggestions.append("Reduce repeated characters")
        
        # Check for common substitutions
        common_subs = {'@': 'a', '3': 'e', '1': 'i', '0': 'o', '5': 's', '7': 't'}
        normalized = password.lower()
        for sub, letter in common_subs.items():
            normalized = normalized.replace(sub, letter)
        
        if normalized in self.common_passwords:
            feedback.append("Password is a common word with simple substitutions")
            suggestions.append("Avoid simple character substitutions (@ for a, 3 for e, etc.)")
        
        # Check personal information
        if user_info:
            personal_issues = self._check_personal_info(password, user_info)
            if personal_issues:
                feedback.extend(personal_issues)
                suggestions.append("Don't use personal information in passwords")
        
        return {'feedback': feedback, 'suggestions': suggestions}
    
    def _contains_sequence(self, password: str, pattern: str, min_length: int = 3) -> bool:
        """Check if password contains a sequence from a pattern"""
        for i in range(len(pattern) - min_length + 1):
            sequence = pattern[i:i + min_length]
            if sequence in password:
                return True
            # Check reverse
            if sequence[::-1] in password:
                return True
        return False
    
    def _has_excessive_repetition(self, password: str, max_repeated: int) -> bool:
        """Check for excessive character repetition"""
        count = 1
        for i in range(1, len(password)):
            if password[i] == password[i-1]:
                count += 1
                if count > max_repeated:
                    return True
            else:
                count = 1
        return False
    
    def _check_personal_info(self, password: str, user_info: Dict[str, str]) -> List[str]:
        """Check if password contains personal information"""
        errors = []
        password_lower = password.lower()
        
        for field, value in user_info.items():
            if not value:
                continue
            
            value_lower = str(value).lower()
            
            # Skip very short values
            if len(value_lower) < 3:
                continue
            
            if value_lower in password_lower:
                errors.append(f"Password contains personal information ({field})")
        
        return errors
    
    def _format_crack_time(self, seconds: float) -> str:
        """Format crack time in human-readable form"""
        if seconds < 60:
            return "less than a minute"
        elif seconds < 3600:
            return f"{int(seconds // 60)} minutes"
        elif seconds < 86400:
            return f"{int(seconds // 3600)} hours"
        elif seconds < 2592000:  # 30 days
            return f"{int(seconds // 86400)} days"
        elif seconds < 31536000:  # 1 year
            return f"{int(seconds // 2592000)} months"
        elif seconds < 3153600000:  # 100 years
            return f"{int(seconds // 31536000)} years"
        else:
            return "centuries"


# Utility functions

def create_password_security_manager(config: Dict[str, Any] = None) -> PasswordSecurityManager:
    """Factory function to create password security manager"""
    return PasswordSecurityManager(config)

def generate_password(length: int = 16, policy: PasswordPolicy = PasswordPolicy.STANDARD) -> str:
    """Quick password generation with policy compliance"""
    manager = create_password_security_manager()
    
    # Generate password based on policy
    policy_config = manager.password_policies[policy]
    include_symbols = policy_config.get('require_symbols', True)
    
    # Ensure minimum length
    min_length = policy_config.get('min_length', 8)
    length = max(length, min_length)
    
    return manager.generate_secure_password(length, include_symbols)

def check_password_strength(password: str, user_info: Dict[str, str] = None) -> PasswordStrengthResult:
    """Quick password strength check"""
    manager = create_password_security_manager()
    return manager.analyze_password_strength(password, user_info)
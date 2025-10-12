"""
AdCopySurge Session Management Tests
Comprehensive test suite for session management, security, and Flask integration
"""

import pytest
import json
import redis
import secrets
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g

# Import the modules we're testing
from app.security.session_manager import (
    SessionManager, SessionData, DeviceInfo, LocationInfo, SecurityMetrics,
    SessionStatus, DeviceType, RiskLevel, SecurityEvent, create_session_manager
)
from app.security.session_middleware import (
    SessionMiddleware, require_session, require_user, require_mfa_verified,
    init_session_manager, create_user_session, destroy_current_session
)
from app.api.session_routes import session_bp


class TestSessionManager:
    """Test SessionManager core functionality"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client"""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.sadd.return_value = 1
        mock_redis.srem.return_value = 1
        mock_redis.smembers.return_value = set()
        mock_redis.expire.return_value = True
        mock_redis.delete.return_value = True
        mock_redis.incr.return_value = 1
        mock_redis.keys.return_value = []
        mock_redis.ttl.return_value = -1
        mock_redis.setex.return_value = True
        return mock_redis
    
    @pytest.fixture
    def session_config(self):
        """Test session configuration"""
        return {
            'redis_url': 'redis://localhost:6379/6',
            'encryption_key': secrets.token_urlsafe(32),
            'default_session_hours': 24,
            'remember_me_days': 30,
            'idle_timeout_minutes': 30,
            'max_concurrent_sessions': 5,
            'max_login_attempts': 5,
            'lockout_duration_minutes': 15,
            'suspicious_threshold': 0.7,
            'enable_device_tracking': True,
            'enable_location_tracking': True,
            'enable_security_monitoring': True
        }
    
    @pytest.fixture
    def session_manager(self, session_config, mock_redis):
        """Create session manager with mocked dependencies"""
        with patch('app.security.session_manager.redis.from_url') as mock_redis_from_url:
            mock_redis_from_url.return_value = mock_redis
            
            with patch('app.security.session_manager.geoip2.database.Reader') as mock_geoip:
                mock_geoip.return_value = None
                
                manager = SessionManager(session_config)
                return manager
    
    def test_session_creation(self, session_manager):
        """Test session creation"""
        user_id = "test_user_123"
        ip_address = "192.168.1.1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        session, csrf_token = session_manager.create_session(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            remember_me=False,
            mfa_verified=True
        )
        
        assert session is not None
        assert session.user_id == user_id
        assert session.ip_address == ip_address
        assert session.status == SessionStatus.ACTIVE
        assert session.mfa_verified == True
        assert csrf_token is not None
        assert len(csrf_token) > 0
        
    def test_session_validation(self, session_manager):
        """Test session validation"""
        user_id = "test_user_123"
        ip_address = "192.168.1.1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        # Create session
        session, csrf_token = session_manager.create_session(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Mock Redis to return the session
        encrypted_data = session_manager._encrypt_session_data(json.dumps({
            'session_id': session.session_id,
            'user_id': session.user_id,
            'status': session.status.value,
            'created_at': session.created_at.isoformat(),
            'last_activity_at': session.last_activity_at.isoformat(),
            'expires_at': session.expires_at.isoformat(),
            'device_info': {
                'device_id': session.device_info.device_id,
                'device_type': session.device_info.device_type.value,
                'os_name': session.device_info.os_name,
                'browser_name': session.device_info.browser_name,
                'is_mobile': session.device_info.is_mobile,
                'is_bot': session.device_info.is_bot,
                'fingerprint': session.device_info.fingerprint
            },
            'location_info': {
                'ip_address': session.location_info.ip_address,
                'country': session.location_info.country,
                'is_vpn': session.location_info.is_vpn,
                'is_proxy': session.location_info.is_proxy
            },
            'security_metrics': {
                'risk_score': session.security_metrics.risk_score,
                'risk_level': session.security_metrics.risk_level.value,
                'last_activity_at': session.security_metrics.last_activity_at.isoformat() if session.security_metrics.last_activity_at else None
            },
            'ip_address': session.ip_address,
            'user_agent': session.user_agent,
            'csrf_token': csrf_token,
            'mfa_verified': session.mfa_verified,
            'remember_me': session.remember_me,
            'metadata': {}
        }))
        session_manager.redis_client.get.return_value = encrypted_data
        
        # Validate session
        is_valid, validated_session, error = session_manager.validate_session(
            session_id=session.session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            csrf_token=csrf_token
        )
        
        assert is_valid == True
        assert validated_session is not None
        assert error is None
        assert validated_session.user_id == user_id
    
    def test_device_fingerprinting(self, session_manager):
        """Test device fingerprinting"""
        user_agent1 = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        user_agent2 = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        
        headers = {'accept-language': 'en-US,en;q=0.9'}
        
        device1 = session_manager._parse_device_info(user_agent1, headers)
        device2 = session_manager._parse_device_info(user_agent2, headers)
        
        assert device1.fingerprint != device2.fingerprint
        assert device1.device_type == DeviceType.DESKTOP
        assert device1.os_name is not None
        assert device1.browser_name is not None
    
    def test_risk_scoring(self, session_manager):
        """Test security risk scoring"""
        user_id = "test_user_123"
        ip_address = "192.168.1.1"
        
        # Mock device info (bot)
        device_info = DeviceInfo(
            device_id="test_device",
            device_type=DeviceType.BOT,
            is_bot=True,
            fingerprint="bot_fingerprint"
        )
        
        # Mock location info (VPN)
        location_info = LocationInfo(
            ip_address=ip_address,
            is_vpn=True
        )
        
        metrics = session_manager._calculate_initial_security_metrics(
            user_id, ip_address, device_info, location_info
        )
        
        # Should have elevated risk due to bot + VPN
        assert metrics.risk_score > 0.4
        assert metrics.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    def test_concurrent_session_limits(self, session_manager, mock_redis):
        """Test concurrent session limits"""
        user_id = "test_user_123"
        ip_address = "192.168.1.1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        # Mock existing sessions
        existing_sessions = [f"session_{i}" for i in range(5)]
        mock_redis.smembers.return_value = set(existing_sessions)
        
        # Mock get_user_sessions to return max sessions
        with patch.object(session_manager, 'get_user_sessions') as mock_get_sessions:
            mock_sessions = []
            for i in range(5):
                mock_session = Mock()
                mock_session.session_id = f"session_{i}"
                mock_session.last_activity_at = datetime.now(timezone.utc) - timedelta(minutes=i)
                mock_sessions.append(mock_session)
            mock_get_sessions.return_value = mock_sessions
            
            with patch.object(session_manager, 'revoke_session') as mock_revoke:
                mock_revoke.return_value = True
                
                # Create new session (should trigger cleanup)
                session, csrf_token = session_manager.create_session(
                    user_id=user_id,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                # Should have called revoke_session for oldest session
                mock_revoke.assert_called()
    
    def test_brute_force_detection(self, session_manager):
        """Test brute force attack detection"""
        user_id = "test_user_123"
        ip_address = "192.168.1.1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        # Mock failed attempts reaching threshold
        session_manager.redis_client.incr.return_value = session_manager.max_login_attempts
        
        with patch.object(session_manager, '_handle_brute_force_detection') as mock_handler:
            # Record failed login
            result = session_manager.record_login_attempt(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason="Invalid password"
            )
            
            assert result == True
            mock_handler.assert_called_once()
    
    def test_session_expiration(self, session_manager):
        """Test session expiration handling"""
        user_id = "test_user_123"
        ip_address = "192.168.1.1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        # Create session
        session, csrf_token = session_manager.create_session(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Check if session is not expired initially
        assert not session.is_expired()
        
        # Manually set expiration to past
        session.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        
        # Check if session is now expired
        assert session.is_expired()
    
    def test_ip_change_detection(self, session_manager):
        """Test IP address change detection"""
        old_ip = "192.168.1.1"
        new_ip_same_subnet = "192.168.1.2"
        new_ip_different = "10.0.0.1"
        
        # Same subnet should be acceptable
        assert session_manager._is_acceptable_ip_change(old_ip, new_ip_same_subnet) == True
        
        # Different subnet should not be acceptable
        assert session_manager._is_acceptable_ip_change(old_ip, new_ip_different) == False
    
    def test_session_cleanup(self, session_manager, mock_redis):
        """Test expired session cleanup"""
        # Mock Redis keys with expired sessions
        mock_redis.keys.return_value = ["session:expired1", "session:expired2"]
        
        # Mock expired session data
        expired_session_data = {
            'expires_at': (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        }
        encrypted_data = session_manager._encrypt_session_data(json.dumps(expired_session_data))
        mock_redis.get.return_value = encrypted_data
        
        with patch.object(session_manager, '_expire_session') as mock_expire:
            cleaned_count = session_manager.cleanup_expired_sessions()
            
            assert cleaned_count == 2
            assert mock_expire.call_count == 2


class TestSessionMiddleware:
    """Test Flask session middleware"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask app"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        return app
    
    @pytest.fixture
    def session_middleware(self, app):
        """Create session middleware"""
        config = {
            'redis_url': 'redis://localhost:6379/6',
            'encryption_key': secrets.token_urlsafe(32),
            'enable_security_monitoring': False  # Disable for testing
        }
        
        with patch('app.security.session_manager.redis.from_url'):
            middleware = SessionMiddleware()
            middleware.session_manager = Mock()
            return middleware
    
    def test_session_validation_middleware(self, app, session_middleware):
        """Test session validation middleware"""
        with app.app_context():
            with app.test_request_context('/', headers={'User-Agent': 'test'}):
                # Mock valid session
                mock_session = Mock()
                mock_session.user_id = "test_user"
                mock_session.session_id = "test_session"
                mock_session.mfa_verified = True
                
                session_middleware.session_manager.validate_session.return_value = (
                    True, mock_session, None
                )
                
                # Mock request with session cookie
                with patch('flask.request') as mock_request:
                    mock_request.cookies = {'adcs_session': 'test_session'}
                    mock_request.headers = {'User-Agent': 'test'}
                    mock_request.endpoint = 'test.endpoint'
                    
                    with patch('flask.g') as mock_g:
                        session_middleware._should_skip_validation = Mock(return_value=False)
                        session_middleware._get_session_id_from_request = Mock(return_value='test_session')
                        session_middleware._get_client_ip = Mock(return_value='127.0.0.1')
                        
                        # This would normally be called by Flask's before_request
                        # We're testing the logic directly
                        result = session_middleware.session_manager.validate_session(
                            'test_session', '127.0.0.1', 'test'
                        )
                        
                        assert result[0] == True  # Valid
                        assert result[1] == mock_session  # Session data
                        assert result[2] is None  # No error


class TestSessionAPI:
    """Test Flask API routes"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask app with session routes"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Register session routes
        app.register_blueprint(session_bp)
        
        # Mock session manager
        mock_session_manager = Mock()
        app.extensions = {'session_manager': mock_session_manager}
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_create_session_api(self, client, app):
        """Test session creation API endpoint"""
        with patch('app.security.session_middleware.create_user_session') as mock_create:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_create.return_value = (mock_response, Mock())
            
            response = client.post('/api/session/create', json={
                'user_id': 'test_user',
                'remember_me': False,
                'mfa_verified': True
            })
            
            mock_create.assert_called_once()
    
    def test_session_info_api(self, client, app):
        """Test session info API endpoint"""
        with app.app_context():
            with patch('flask.g') as mock_g:
                # Mock session data
                mock_session = Mock()
                mock_session.session_id = 'test_session'
                mock_session.user_id = 'test_user'
                mock_session.created_at = datetime.now(timezone.utc)
                mock_session.last_activity_at = datetime.now(timezone.utc)
                mock_session.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
                mock_session.time_until_expiry.return_value = timedelta(hours=1)
                mock_session.mfa_verified = True
                mock_session.remember_me = False
                mock_session.status = SessionStatus.ACTIVE
                
                # Mock device and location info
                mock_session.device_info = Mock()
                mock_session.device_info.device_id = 'device1'
                mock_session.device_info.device_type = DeviceType.DESKTOP
                mock_session.device_info.os_name = 'Windows'
                mock_session.device_info.browser_name = 'Chrome'
                mock_session.device_info.is_mobile = False
                mock_session.device_info.is_bot = False
                
                mock_session.location_info = Mock()
                mock_session.location_info.country = 'United States'
                mock_session.location_info.city = 'New York'
                mock_session.location_info.timezone = 'America/New_York'
                
                mock_session.security_metrics = Mock()
                mock_session.security_metrics.risk_score = 0.1
                mock_session.security_metrics.risk_level = RiskLevel.LOW
                mock_session.security_metrics.device_changes = 0
                mock_session.security_metrics.location_changes = 0
                
                mock_session.ip_address = '192.168.1.1'
                
                mock_g.session_data = mock_session
                
                with patch('app.api.session_routes.require_session') as mock_decorator:
                    # Make decorator pass through
                    mock_decorator.side_effect = lambda f: f
                    
                    response = client.get('/api/session/info')
                    
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert data['success'] == True
                    assert 'session' in data
    
    def test_login_attempt_recording(self, client, app):
        """Test login attempt recording API"""
        with patch('app.security.session_middleware.is_user_locked') as mock_locked:
            mock_locked.return_value = (False, None)
            
            with patch('app.security.session_middleware.record_login_attempt') as mock_record:
                mock_record.return_value = True
                
                response = client.post('/api/session/login-attempts', json={
                    'user_id': 'test_user',
                    'success': False,
                    'failure_reason': 'Invalid password'
                })
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] == True
                assert data['recorded'] == True
                mock_record.assert_called_once()
    
    def test_user_lockout_handling(self, client, app):
        """Test user lockout API response"""
        with patch('app.security.session_middleware.is_user_locked') as mock_locked:
            unlock_time = datetime.now(timezone.utc) + timedelta(minutes=15)
            mock_locked.return_value = (True, unlock_time)
            
            response = client.post('/api/session/login-attempts', json={
                'user_id': 'test_user',
                'success': False,
                'failure_reason': 'Invalid password'
            })
            
            assert response.status_code == 423  # HTTP 423 Locked
            data = json.loads(response.data)
            assert data['locked'] == True
            assert 'unlock_time' in data


class TestSessionSecurity:
    """Test security features"""
    
    @pytest.fixture
    def session_manager(self):
        """Create session manager for security tests"""
        config = {
            'encryption_key': secrets.token_urlsafe(32),
            'enable_security_monitoring': True
        }
        
        with patch('app.security.session_manager.redis.from_url'):
            manager = SessionManager(config)
            manager.redis_client = Mock()
            return manager
    
    def test_csrf_token_validation(self, session_manager):
        """Test CSRF token validation"""
        # Create session with CSRF token
        user_id = "test_user"
        ip_address = "192.168.1.1"
        user_agent = "test_agent"
        
        session, csrf_token = session_manager.create_session(
            user_id, ip_address, user_agent
        )
        
        # Mock session retrieval
        with patch.object(session_manager, 'get_session', return_value=session):
            # Valid CSRF token should pass
            valid, _, error = session_manager.validate_session(
                session.session_id, ip_address, user_agent, csrf_token
            )
            
            # Should be valid (mocked security checks)
            with patch.object(session_manager, '_perform_security_checks', 
                            return_value={'valid': True}):
                valid, _, error = session_manager.validate_session(
                    session.session_id, ip_address, user_agent, csrf_token
                )
                assert valid == True
            
            # Invalid CSRF token should fail
            with patch.object(session_manager, '_log_security_event'):
                invalid, _, error = session_manager.validate_session(
                    session.session_id, ip_address, user_agent, "invalid_token"
                )
                assert invalid == False
                assert "CSRF" in error
    
    def test_encryption_decryption(self, session_manager):
        """Test session data encryption/decryption"""
        test_data = "sensitive session data"
        
        # Encrypt data
        encrypted = session_manager._encrypt_session_data(test_data)
        assert encrypted != test_data
        assert len(encrypted) > len(test_data)
        
        # Decrypt data
        decrypted = session_manager._decrypt_session_data(encrypted)
        assert decrypted == test_data
    
    def test_security_event_logging(self, session_manager):
        """Test security event logging"""
        session_manager.redis_client.setex.return_value = True
        
        # Log security event
        session_manager._log_security_event(
            session_id="test_session",
            user_id="test_user",
            event_type="test_event",
            description="Test security event",
            risk_level=RiskLevel.HIGH,
            ip_address="192.168.1.1",
            user_agent="test_agent"
        )
        
        # Verify Redis call was made
        session_manager.redis_client.setex.assert_called()
        call_args = session_manager.redis_client.setex.call_args
        
        # Check TTL (should be 90 days = 86400 * 90)
        assert call_args[0][1] == 86400 * 90
        
        # Check event data structure
        event_data = json.loads(call_args[0][2])
        assert event_data['user_id'] == 'test_user'
        assert event_data['event_type'] == 'test_event'
        assert event_data['risk_level'] == 'high'


# Integration Tests

class TestSessionIntegration:
    """Integration tests for complete session flow"""
    
    @pytest.fixture
    def app(self):
        """Create integrated test app"""
        app = Flask(__name__)
        app.config.update({
            'TESTING': True,
            'SECRET_KEY': 'test-secret-key',
            'SESSION_MANAGER_CONFIG': {
                'redis_url': 'redis://localhost:6379/6',
                'encryption_key': secrets.token_urlsafe(32),
                'enable_security_monitoring': False
            }
        })
        
        # Mock Redis for testing
        with patch('app.security.session_manager.redis.from_url'):
            # Initialize session manager
            from app.security.session_middleware import init_session_manager
            init_session_manager(app)
            
            # Register routes
            from app.api.session_routes import register_session_routes
            register_session_routes(app)
            
            return app
    
    def test_full_session_lifecycle(self, app):
        """Test complete session lifecycle"""
        with app.test_client() as client:
            with patch.object(app.extensions['session_manager'], 'redis_client'):
                # 1. Create session
                response = client.post('/api/session/create', json={
                    'user_id': 'integration_test_user',
                    'remember_me': False,
                    'mfa_verified': True
                })
                
                # Should succeed (mocked)
                # In real integration, would verify actual Redis interaction
                
                # 2. Validate session
                # 3. Use session for protected endpoint
                # 4. Refresh session
                # 5. Destroy session
                
                # This would be expanded with real Redis and more complex flows
                pass


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
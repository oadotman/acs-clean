"""
AdCopySurge Session Management Flask Integration
Middleware and decorators for Flask application session handling
"""

import functools
from typing import Dict, Optional, Any, Callable
from flask import Flask, request, session, g, jsonify, make_response, current_app
from werkzeug.exceptions import Unauthorized, Forbidden, BadRequest
import logging
from datetime import datetime, timezone

from .session_manager import SessionManager, SessionData, create_session_manager

logger = logging.getLogger(__name__)

class SessionMiddleware:
    """Flask middleware for session management"""
    
    def __init__(self, app: Flask = None, session_manager: SessionManager = None):
        self.session_manager = session_manager
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize session middleware with Flask app"""
        app.config.setdefault('SESSION_MANAGER_CONFIG', {})
        
        if not self.session_manager:
            self.session_manager = create_session_manager(app.config['SESSION_MANAGER_CONFIG'])
        
        # Register session cleanup task
        @app.before_first_request
        def setup_session_cleanup():
            # This could be enhanced with background task scheduling
            pass
        
        # Register session validation for all requests
        @app.before_request
        def validate_session():
            g.session_data = None
            g.session_valid = False
            g.user_id = None
            
            # Skip validation for certain endpoints
            if self._should_skip_validation(request.endpoint):
                return
            
            # Get session ID from cookie or header
            session_id = self._get_session_id_from_request()
            if not session_id:
                return
            
            # Validate session
            is_valid, session_data, error_message = self.session_manager.validate_session(
                session_id=session_id,
                ip_address=self._get_client_ip(),
                user_agent=request.headers.get('User-Agent', ''),
                csrf_token=request.headers.get('X-CSRF-Token')
            )
            
            if is_valid and session_data:
                g.session_data = session_data
                g.session_valid = True
                g.user_id = session_data.user_id
                
                # Refresh session activity
                self.session_manager.refresh_session(session_id, extend_expiry=False)
            else:
                # Clear invalid session cookie
                if session_id:
                    self._clear_session_cookie()
                
                # Log invalid session attempt
                if error_message:
                    logger.warning(f"Invalid session attempt: {error_message}")
    
    def _should_skip_validation(self, endpoint: str) -> bool:
        """Check if session validation should be skipped for endpoint"""
        skip_endpoints = [
            'auth.login',
            'auth.register',
            'auth.forgot_password',
            'health',
            'static',
            'api.health'
        ]
        
        return endpoint in skip_endpoints or (endpoint and endpoint.startswith('static'))
    
    def _get_session_id_from_request(self) -> Optional[str]:
        """Get session ID from request (cookie or header)"""
        # Try cookie first
        cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'adcs_session')
        session_id = request.cookies.get(cookie_name)
        
        # Try Authorization header as fallback
        if not session_id:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                session_id = auth_header[7:]
        
        return session_id
    
    def _get_client_ip(self) -> str:
        """Get client IP address from request"""
        # Check for forwarded headers (behind proxy/load balancer)
        forwarded_ips = request.headers.get('X-Forwarded-For')
        if forwarded_ips:
            # Take the first IP (client IP)
            return forwarded_ips.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr or '127.0.0.1'
    
    def _clear_session_cookie(self):
        """Clear session cookie"""
        cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'adcs_session')
        response = make_response()
        response.set_cookie(cookie_name, '', expires=0)
        return response

# Decorators

def require_session(f: Callable) -> Callable:
    """Decorator to require valid session for endpoint"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(g, 'session_valid', False):
            return jsonify({'error': 'Valid session required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_user(f: Callable) -> Callable:
    """Decorator to require authenticated user"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(g, 'user_id', None):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_mfa_verified(f: Callable) -> Callable:
    """Decorator to require MFA-verified session"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        session_data = getattr(g, 'session_data', None)
        if not session_data or not session_data.mfa_verified:
            return jsonify({'error': 'MFA verification required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_low_risk_session(f: Callable) -> Callable:
    """Decorator to require low-risk session"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        session_data = getattr(g, 'session_data', None)
        if not session_data:
            return jsonify({'error': 'Valid session required'}), 401
        
        from .session_manager import RiskLevel
        if session_data.security_metrics.risk_level not in [RiskLevel.LOW, RiskLevel.MEDIUM]:
            return jsonify({'error': 'High-risk session not allowed for this operation'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def optional_session(f: Callable) -> Callable:
    """Decorator for endpoints that work with or without session"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Session data is available in g.session_data if present
        # No requirement for valid session
        return f(*args, **kwargs)
    return decorated_function

# Session Management Helper Functions

def create_user_session(user_id: str, 
                       remember_me: bool = False, 
                       mfa_verified: bool = False,
                       additional_headers: Dict[str, str] = None) -> tuple:
    """Create a new session for user"""
    try:
        session_manager = current_app.extensions.get('session_manager')
        if not session_manager:
            raise RuntimeError("Session manager not initialized")
        
        # Create session
        session_data, csrf_token = session_manager.create_session(
            user_id=user_id,
            ip_address=_get_client_ip_from_request(),
            user_agent=request.headers.get('User-Agent', ''),
            remember_me=remember_me,
            mfa_verified=mfa_verified,
            additional_headers=additional_headers or _get_device_headers()
        )
        
        # Create response with session cookie
        response = make_response(jsonify({
            'success': True,
            'user_id': user_id,
            'session_id': session_data.session_id,
            'csrf_token': csrf_token,
            'expires_at': session_data.expires_at.isoformat(),
            'mfa_verified': mfa_verified
        }))
        
        # Set session cookie
        _set_session_cookie(response, session_data.session_id, session_data.expires_at)
        
        # Set CSRF token header
        response.headers['X-CSRF-Token'] = csrf_token
        
        return response, session_data
        
    except Exception as e:
        logger.error(f"Error creating session for user {user_id}: {e}")
        return jsonify({'error': 'Failed to create session'}), 500

def destroy_current_session() -> dict:
    """Destroy current user session"""
    try:
        session_data = getattr(g, 'session_data', None)
        if not session_data:
            return {'success': False, 'message': 'No active session'}
        
        session_manager = current_app.extensions.get('session_manager')
        if not session_manager:
            return {'success': False, 'message': 'Session manager not available'}
        
        # Revoke session
        success = session_manager.revoke_session(
            session_data.session_id,
            reason="User logout"
        )
        
        if success:
            # Clear session cookie
            response = make_response(jsonify({'success': True, 'message': 'Session ended'}))
            _clear_session_cookie(response)
            return response
        else:
            return {'success': False, 'message': 'Failed to end session'}
            
    except Exception as e:
        logger.error(f"Error destroying session: {e}")
        return {'success': False, 'message': 'Session destruction error'}

def destroy_all_user_sessions(user_id: str, except_current: bool = True) -> dict:
    """Destroy all sessions for a user"""
    try:
        session_manager = current_app.extensions.get('session_manager')
        if not session_manager:
            return {'success': False, 'message': 'Session manager not available'}
        
        current_session_id = None
        if except_current:
            session_data = getattr(g, 'session_data', None)
            if session_data:
                current_session_id = session_data.session_id
        
        # Revoke all sessions
        revoked_count = session_manager.revoke_all_user_sessions(
            user_id=user_id,
            except_session=current_session_id,
            reason="Revoke all sessions requested"
        )
        
        return {
            'success': True,
            'message': f'Revoked {revoked_count} sessions',
            'revoked_count': revoked_count
        }
        
    except Exception as e:
        logger.error(f"Error destroying all sessions for user {user_id}: {e}")
        return {'success': False, 'message': 'Failed to revoke sessions'}

def get_user_sessions(user_id: str, active_only: bool = True) -> dict:
    """Get all sessions for a user"""
    try:
        session_manager = current_app.extensions.get('session_manager')
        if not session_manager:
            return {'success': False, 'message': 'Session manager not available'}
        
        sessions = session_manager.get_user_sessions(user_id, active_only)
        
        # Convert sessions to JSON-serializable format
        session_list = []
        for sess in sessions:
            session_info = {
                'session_id': sess.session_id,
                'created_at': sess.created_at.isoformat(),
                'last_activity_at': sess.last_activity_at.isoformat(),
                'expires_at': sess.expires_at.isoformat(),
                'device_info': {
                    'device_type': sess.device_info.device_type.value,
                    'os_name': sess.device_info.os_name,
                    'browser_name': sess.device_info.browser_name,
                    'is_mobile': sess.device_info.is_mobile
                },
                'location_info': {
                    'country': sess.location_info.country,
                    'city': sess.location_info.city,
                    'ip_address': sess.ip_address[:sess.ip_address.rfind('.')] + '.xxx'  # Mask last octet
                },
                'security_metrics': {
                    'risk_level': sess.security_metrics.risk_level.value,
                    'risk_score': sess.security_metrics.risk_score
                },
                'mfa_verified': sess.mfa_verified,
                'is_current': getattr(g, 'session_data', None) and g.session_data.session_id == sess.session_id
            }
            session_list.append(session_info)
        
        return {
            'success': True,
            'sessions': session_list,
            'total_count': len(session_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting sessions for user {user_id}: {e}")
        return {'success': False, 'message': 'Failed to get sessions'}

def record_login_attempt(user_id: str, success: bool, failure_reason: str = None) -> bool:
    """Record login attempt"""
    try:
        session_manager = current_app.extensions.get('session_manager')
        if not session_manager:
            return False
        
        return session_manager.record_login_attempt(
            user_id=user_id,
            ip_address=_get_client_ip_from_request(),
            user_agent=request.headers.get('User-Agent', ''),
            success=success,
            failure_reason=failure_reason
        )
        
    except Exception as e:
        logger.error(f"Error recording login attempt: {e}")
        return False

def is_user_locked(user_id: str) -> tuple:
    """Check if user is locked due to failed login attempts"""
    try:
        session_manager = current_app.extensions.get('session_manager')
        if not session_manager:
            return False, None
        
        return session_manager.is_user_locked(user_id)
        
    except Exception as e:
        logger.error(f"Error checking user lock status: {e}")
        return False, None

# Helper Functions

def _get_client_ip_from_request() -> str:
    """Get client IP from current request"""
    forwarded_ips = request.headers.get('X-Forwarded-For')
    if forwarded_ips:
        return forwarded_ips.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    return request.remote_addr or '127.0.0.1'

def _get_device_headers() -> Dict[str, str]:
    """Extract device-related headers from request"""
    return {
        'accept-language': request.headers.get('Accept-Language', ''),
        'accept-encoding': request.headers.get('Accept-Encoding', ''),
        'accept': request.headers.get('Accept', ''),
        'screen-resolution': request.headers.get('Screen-Resolution', ''),
        'timezone': request.headers.get('Timezone', '')
    }

def _set_session_cookie(response, session_id: str, expires_at: datetime):
    """Set session cookie on response"""
    cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'adcs_session')
    cookie_secure = current_app.config.get('SESSION_COOKIE_SECURE', True)
    cookie_httponly = current_app.config.get('SESSION_COOKIE_HTTPONLY', True)
    cookie_samesite = current_app.config.get('SESSION_COOKIE_SAMESITE', 'Strict')
    
    response.set_cookie(
        cookie_name,
        session_id,
        expires=expires_at,
        secure=cookie_secure,
        httponly=cookie_httponly,
        samesite=cookie_samesite,
        path='/'
    )

def _clear_session_cookie(response):
    """Clear session cookie from response"""
    cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'adcs_session')
    response.set_cookie(cookie_name, '', expires=0, path='/')

# Background Tasks (can be integrated with Celery or similar)

def cleanup_expired_sessions():
    """Background task to cleanup expired sessions"""
    try:
        session_manager = current_app.extensions.get('session_manager')
        if session_manager:
            cleaned_count = session_manager.cleanup_expired_sessions()
            logger.info(f"Cleaned up {cleaned_count} expired sessions")
            return cleaned_count
        return 0
    except Exception as e:
        logger.error(f"Error during session cleanup: {e}")
        return 0

# Flask CLI Commands

def register_session_commands(app: Flask):
    """Register session management CLI commands"""
    
    @app.cli.command()
    def cleanup_sessions():
        """Clean up expired sessions"""
        with app.app_context():
            count = cleanup_expired_sessions()
            print(f"Cleaned up {count} expired sessions")
    
    @app.cli.command()
    @app.cli.argument('user_id')
    def revoke_user_sessions(user_id):
        """Revoke all sessions for a user"""
        with app.app_context():
            session_manager = app.extensions.get('session_manager')
            if session_manager:
                count = session_manager.revoke_all_user_sessions(user_id, reason="CLI revocation")
                print(f"Revoked {count} sessions for user {user_id}")
            else:
                print("Session manager not available")
    
    @app.cli.command()
    @app.cli.argument('user_id')
    def show_user_sessions(user_id):
        """Show all sessions for a user"""
        with app.app_context():
            result = get_user_sessions(user_id, active_only=False)
            if result['success']:
                sessions = result['sessions']
                print(f"Found {len(sessions)} sessions for user {user_id}:")
                for session in sessions:
                    print(f"  Session: {session['session_id'][:8]}...")
                    print(f"    Created: {session['created_at']}")
                    print(f"    Last Activity: {session['last_activity_at']}")
                    print(f"    Device: {session['device_info']['device_type']} - {session['device_info']['browser_name']}")
                    print(f"    Risk: {session['security_metrics']['risk_level']}")
                    print()
            else:
                print(f"Error: {result['message']}")

# Extension Registration

def init_session_manager(app: Flask, config: Dict[str, Any] = None):
    """Initialize session manager extension with Flask app"""
    session_manager = create_session_manager(config)
    
    # Store in app extensions
    if not hasattr(app, 'extensions'):
        app.extensions = {}
    app.extensions['session_manager'] = session_manager
    
    # Initialize middleware
    SessionMiddleware(app, session_manager)
    
    # Register CLI commands
    register_session_commands(app)
    
    return session_manager
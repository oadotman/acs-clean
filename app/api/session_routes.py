"""
AdCopySurge Session Management API Routes
Flask API endpoints for session management operations
"""

from flask import Blueprint, request, jsonify, g
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden
import logging

from ..security.session_middleware import (
    require_session, require_user, require_mfa_verified,
    create_user_session, destroy_current_session, destroy_all_user_sessions,
    get_user_sessions, record_login_attempt, is_user_locked
)

logger = logging.getLogger(__name__)

# Create blueprint
session_bp = Blueprint('session', __name__, url_prefix='/api/session')

@session_bp.route('/create', methods=['POST'])
def create_session():
    """Create a new user session"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        remember_me = data.get('remember_me', False)
        mfa_verified = data.get('mfa_verified', False)
        additional_headers = data.get('additional_headers', {})
        
        # Create session
        response, session_data = create_user_session(
            user_id=user_id,
            remember_me=remember_me,
            mfa_verified=mfa_verified,
            additional_headers=additional_headers
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({'error': 'Failed to create session'}), 500

@session_bp.route('/destroy', methods=['POST'])
@require_session
def destroy_session():
    """Destroy current session"""
    try:
        response = destroy_current_session()
        return response
        
    except Exception as e:
        logger.error(f"Error destroying session: {e}")
        return jsonify({'error': 'Failed to destroy session'}), 500

@session_bp.route('/destroy-all', methods=['POST'])
@require_user
def destroy_all_sessions():
    """Destroy all sessions for current user"""
    try:
        data = request.get_json() or {}
        except_current = data.get('except_current', True)
        
        result = destroy_all_user_sessions(g.user_id, except_current=except_current)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error destroying all sessions: {e}")
        return jsonify({'error': 'Failed to destroy sessions'}), 500

@session_bp.route('/info', methods=['GET'])
@require_session
def get_session_info():
    """Get current session information"""
    try:
        session_data = g.session_data
        if not session_data:
            return jsonify({'error': 'No active session'}), 404
        
        session_info = {
            'session_id': session_data.session_id,
            'user_id': session_data.user_id,
            'created_at': session_data.created_at.isoformat(),
            'last_activity_at': session_data.last_activity_at.isoformat(),
            'expires_at': session_data.expires_at.isoformat(),
            'time_until_expiry': str(session_data.time_until_expiry()),
            'device_info': {
                'device_id': session_data.device_info.device_id,
                'device_type': session_data.device_info.device_type.value,
                'os_name': session_data.device_info.os_name,
                'os_version': session_data.device_info.os_version,
                'browser_name': session_data.device_info.browser_name,
                'browser_version': session_data.device_info.browser_version,
                'is_mobile': session_data.device_info.is_mobile,
                'is_bot': session_data.device_info.is_bot
            },
            'location_info': {
                'country': session_data.location_info.country,
                'country_code': session_data.location_info.country_code,
                'region': session_data.location_info.region,
                'city': session_data.location_info.city,
                'timezone': session_data.location_info.timezone,
                'ip_address': session_data.ip_address[:session_data.ip_address.rfind('.')] + '.xxx'  # Mask IP
            },
            'security_metrics': {
                'risk_score': session_data.security_metrics.risk_score,
                'risk_level': session_data.security_metrics.risk_level.value,
                'device_changes': session_data.security_metrics.device_changes,
                'location_changes': session_data.security_metrics.location_changes,
                'concurrent_sessions': session_data.security_metrics.concurrent_sessions
            },
            'mfa_verified': session_data.mfa_verified,
            'remember_me': session_data.remember_me,
            'status': session_data.status.value
        }
        
        return jsonify({
            'success': True,
            'session': session_info
        })
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        return jsonify({'error': 'Failed to get session info'}), 500

@session_bp.route('/list', methods=['GET'])
@require_user
def list_user_sessions():
    """List all sessions for current user"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        result = get_user_sessions(g.user_id, active_only=active_only)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return jsonify({'error': 'Failed to list sessions'}), 500

@session_bp.route('/revoke/<session_id>', methods=['POST'])
@require_user
def revoke_session(session_id):
    """Revoke a specific session"""
    try:
        from flask import current_app
        
        session_manager = current_app.extensions.get('session_manager')
        if not session_manager:
            return jsonify({'error': 'Session manager not available'}), 500
        
        # Check if session belongs to current user
        user_sessions = session_manager.get_user_sessions(g.user_id, active_only=False)
        target_session = None
        
        for sess in user_sessions:
            if sess.session_id == session_id:
                target_session = sess
                break
        
        if not target_session:
            return jsonify({'error': 'Session not found or not owned by user'}), 404
        
        # Revoke session
        success = session_manager.revoke_session(session_id, reason="User revocation")
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Session revoked successfully'
            })
        else:
            return jsonify({'error': 'Failed to revoke session'}), 500
            
    except Exception as e:
        logger.error(f"Error revoking session {session_id}: {e}")
        return jsonify({'error': 'Failed to revoke session'}), 500

@session_bp.route('/validate', methods=['POST'])
def validate_session():
    """Validate current session"""
    try:
        if g.session_valid and g.session_data:
            return jsonify({
                'valid': True,
                'user_id': g.user_id,
                'session_id': g.session_data.session_id,
                'expires_at': g.session_data.expires_at.isoformat(),
                'mfa_verified': g.session_data.mfa_verified,
                'risk_level': g.session_data.security_metrics.risk_level.value
            })
        else:
            return jsonify({
                'valid': False,
                'message': 'No valid session found'
            }), 401
            
    except Exception as e:
        logger.error(f"Error validating session: {e}")
        return jsonify({'error': 'Session validation error'}), 500

@session_bp.route('/refresh', methods=['POST'])
@require_session
def refresh_session():
    """Refresh current session"""
    try:
        from flask import current_app
        
        session_manager = current_app.extensions.get('session_manager')
        if not session_manager:
            return jsonify({'error': 'Session manager not available'}), 500
        
        data = request.get_json() or {}
        extend_expiry = data.get('extend_expiry', True)
        
        success = session_manager.refresh_session(
            g.session_data.session_id,
            extend_expiry=extend_expiry
        )
        
        if success:
            # Get updated session info
            updated_session = session_manager.get_session(g.session_data.session_id)
            
            return jsonify({
                'success': True,
                'message': 'Session refreshed',
                'expires_at': updated_session.expires_at.isoformat() if updated_session else None
            })
        else:
            return jsonify({'error': 'Failed to refresh session'}), 500
            
    except Exception as e:
        logger.error(f"Error refreshing session: {e}")
        return jsonify({'error': 'Failed to refresh session'}), 500

@session_bp.route('/security/events', methods=['GET'])
@require_user
@require_mfa_verified
def get_security_events():
    """Get security events for current user"""
    try:
        from flask import current_app
        import json
        
        session_manager = current_app.extensions.get('session_manager')
        if not session_manager or not session_manager.redis_client:
            return jsonify({'error': 'Security events not available'}), 503
        
        # Get security events for user from Redis
        events = []
        
        # Search for events in the last 30 days
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        for days_back in range(30):
            date_key = (end_date - timedelta(days=days_back)).strftime('%Y%m%d')
            pattern = f"security_event:{date_key}:*"
            
            event_keys = session_manager.redis_client.keys(pattern)
            
            for key in event_keys:
                try:
                    event_data = session_manager.redis_client.get(key)
                    if event_data:
                        event = json.loads(event_data)
                        if event.get('user_id') == g.user_id:
                            events.append(event)
                except Exception as e:
                    logger.warning(f"Error parsing security event {key}: {e}")
        
        # Sort by timestamp (most recent first)
        events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limit to last 50 events
        events = events[:50]
        
        return jsonify({
            'success': True,
            'events': events,
            'total_count': len(events)
        })
        
    except Exception as e:
        logger.error(f"Error getting security events: {e}")
        return jsonify({'error': 'Failed to get security events'}), 500

@session_bp.route('/login-attempts', methods=['POST'])
def record_login():
    """Record login attempt"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        user_id = data.get('user_id')
        success = data.get('success', False)
        failure_reason = data.get('failure_reason')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Check if user is locked
        is_locked, unlock_time = is_user_locked(user_id)
        if is_locked:
            return jsonify({
                'error': 'Account is locked due to too many failed attempts',
                'locked': True,
                'unlock_time': unlock_time.isoformat() if unlock_time else None
            }), 423  # HTTP 423 Locked
        
        # Record attempt
        recorded = record_login_attempt(user_id, success, failure_reason)
        
        if recorded:
            # Check if user is now locked after this attempt
            is_locked, unlock_time = is_user_locked(user_id)
            
            return jsonify({
                'success': True,
                'recorded': True,
                'locked': is_locked,
                'unlock_time': unlock_time.isoformat() if unlock_time else None
            })
        else:
            return jsonify({'error': 'Failed to record login attempt'}), 500
            
    except Exception as e:
        logger.error(f"Error recording login attempt: {e}")
        return jsonify({'error': 'Failed to record login attempt'}), 500

@session_bp.route('/user-status/<user_id>', methods=['GET'])
def get_user_status(user_id):
    """Get user account status (locked, etc.)"""
    try:
        is_locked, unlock_time = is_user_locked(user_id)
        
        return jsonify({
            'user_id': user_id,
            'locked': is_locked,
            'unlock_time': unlock_time.isoformat() if unlock_time else None
        })
        
    except Exception as e:
        logger.error(f"Error getting user status: {e}")
        return jsonify({'error': 'Failed to get user status'}), 500

@session_bp.route('/cleanup', methods=['POST'])
@require_user
@require_mfa_verified
def cleanup_sessions():
    """Cleanup expired sessions (admin endpoint)"""
    try:
        from flask import current_app
        
        # This should be restricted to admin users in production
        # For now, requiring MFA verification
        
        session_manager = current_app.extensions.get('session_manager')
        if not session_manager:
            return jsonify({'error': 'Session manager not available'}), 500
        
        cleaned_count = session_manager.cleanup_expired_sessions()
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {cleaned_count} expired sessions',
            'cleaned_count': cleaned_count
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        return jsonify({'error': 'Failed to cleanup sessions'}), 500

@session_bp.route('/stats', methods=['GET'])
@require_user
def get_session_stats():
    """Get session statistics for current user"""
    try:
        from flask import current_app
        
        session_manager = current_app.extensions.get('session_manager')
        if not session_manager:
            return jsonify({'error': 'Session manager not available'}), 500
        
        # Get user sessions
        all_sessions = session_manager.get_user_sessions(g.user_id, active_only=False)
        active_sessions = session_manager.get_user_sessions(g.user_id, active_only=True)
        
        # Calculate stats
        total_sessions = len(all_sessions)
        active_count = len(active_sessions)
        
        device_types = {}
        risk_levels = {}
        
        for session in all_sessions:
            # Count device types
            device_type = session.device_info.device_type.value
            device_types[device_type] = device_types.get(device_type, 0) + 1
            
            # Count risk levels
            risk_level = session.security_metrics.risk_level.value
            risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total_sessions': total_sessions,
                'active_sessions': active_count,
                'expired_sessions': total_sessions - active_count,
                'device_types': device_types,
                'risk_levels': risk_levels,
                'current_session': {
                    'session_id': g.session_data.session_id,
                    'risk_level': g.session_data.security_metrics.risk_level.value,
                    'mfa_verified': g.session_data.mfa_verified
                } if g.session_data else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting session stats: {e}")
        return jsonify({'error': 'Failed to get session statistics'}), 500

# Error handlers for the blueprint

@session_bp.errorhandler(BadRequest)
def handle_bad_request(e):
    return jsonify({'error': 'Bad request', 'message': str(e)}), 400

@session_bp.errorhandler(Unauthorized)
def handle_unauthorized(e):
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

@session_bp.errorhandler(Forbidden)
def handle_forbidden(e):
    return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403

@session_bp.errorhandler(Exception)
def handle_general_error(e):
    logger.error(f"Unhandled error in session API: {e}")
    return jsonify({'error': 'Internal server error'}), 500

# Register the blueprint with the Flask app
def register_session_routes(app):
    """Register session management routes with Flask app"""
    app.register_blueprint(session_bp)
"""
Background tasks for AdCopySurge using Celery.
"""

import time
from typing import Dict, Any, List
from app.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)

@celery_app.task(bind=True)
def analyze_ad_copy_background(self, user_id: int, ad_data: Dict[str, Any], competitor_ads: List[Dict] = None) -> Dict[str, Any]:
    """
    Analyze ad copy using AI services in the background.
    
    Args:
        ad_data: Dictionary containing ad copy and analysis parameters
    
    Returns:
        Dictionary with analysis results
    """
    try:
        logger.info(f"Starting ad copy analysis for task {self.request.id}, user: {user_id}")
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'status': 'Initializing analysis...'}
        )
        
        # Import here to avoid circular imports
        from app.services.ad_analysis_service_enhanced import EnhancedAdAnalysisService
        from app.schemas.ads import AdInput, CompetitorAd
        from app.core.database import SessionLocal
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'current': 30, 'total': 100, 'status': 'Running AI analysis...'}
            )
            
            # Convert ad_data to AdInput schema
            ad_input = AdInput(**ad_data)
            competitor_list = [CompetitorAd(**comp) for comp in (competitor_ads or [])]
            
            # Initialize analysis service - use Enhanced version with AI improvements
            analysis_service = EnhancedAdAnalysisService(db)
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'current': 70, 'total': 100, 'status': 'Generating insights...'}
            )
            
            # Perform analysis (run async function in sync context)
            import asyncio
            try:
                # Get or create event loop
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            analysis_result = loop.run_until_complete(
                analysis_service.analyze_ad(user_id, ad_input, competitor_list)
            )
            
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={'current': 90, 'total': 100, 'status': 'Finalizing results...'}
            )
            
            result = {
                'task_id': self.request.id,
                'analysis_id': analysis_result.analysis_id,
                'user_id': user_id,
                'status': 'completed',
                'scores': analysis_result.scores.dict(),
                'feedback': analysis_result.feedback,
                'alternatives_count': len(analysis_result.alternatives),
                'quick_wins_count': len(analysis_result.quick_wins)
            }
            
            logger.info(f"Completed ad copy analysis for task {self.request.id}")
            return result
            
        finally:
            db.close()
        
    except Exception as exc:
        logger.error(f"Error in analyze_ad_copy task {self.request.id}: {exc}")
        self.update_state(
            state='FAILURE',
            meta={'current': 100, 'total': 100, 'status': str(exc)}
        )
        raise

@celery_app.task(bind=True)
def generate_report(self, analysis_id: str, user_id: str) -> Dict[str, Any]:
    """
    Generate PDF report from analysis results.
    
    Args:
        analysis_id: ID of the completed analysis
        user_id: ID of the user requesting the report
    
    Returns:
        Dictionary with report generation results
    """
    try:
        logger.info(f"Starting report generation for analysis {analysis_id}")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Preparing report data...'}
        )
        
        # TODO: Replace with actual report generation service
        time.sleep(3)  # Simulate report generation time
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 75, 'total': 100, 'status': 'Generating PDF...'}
        )
        
        time.sleep(1)
        
        result = {
            'task_id': self.request.id,
            'analysis_id': analysis_id,
            'user_id': user_id,
            'report_url': f'/api/reports/{analysis_id}.pdf',
            'status': 'completed'
        }
        
        logger.info(f"Completed report generation for analysis {analysis_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Error in generate_report task {self.request.id}: {exc}")
        self.update_state(
            state='FAILURE',
            meta={'current': 100, 'total': 100, 'status': str(exc)}
        )
        raise

@celery_app.task(bind=True)
def send_email(self, email_type: str, recipient: str, **kwargs) -> Dict[str, Any]:
    """
    Send email notification in the background using Resend API.
    
    Args:
        email_type: Type of email to send (team_invitation, welcome, setup_complete, etc.)
        recipient: Email recipient
        **kwargs: Additional context variables for the email
    
    Returns:
        Dictionary with email sending results
    """
    try:
        from app.services.email_service import email_service
        
        logger.info(f"Sending {email_type} email to {recipient}")
        
        # Route to appropriate email method based on type
        if email_type == "team_invitation":
            result = await email_service.send_team_invitation(
                email=recipient,
                agency_name=kwargs.get('agency_name'),
                invitation_token=kwargs.get('invitation_token'),
                invited_by=kwargs.get('invited_by'),
                role_name=kwargs.get('role_name', 'Team Member'),
                personal_message=kwargs.get('personal_message'),
                white_label_settings=kwargs.get('white_label_settings')
            )
        elif email_type == "welcome":
            result = await email_service.send_welcome_email(
                email=recipient,
                user_name=kwargs.get('user_name'),
                agency_name=kwargs.get('agency_name'),
                is_agency_owner=kwargs.get('is_agency_owner', False),
                white_label_settings=kwargs.get('white_label_settings')
            )
        elif email_type == "setup_complete":
            result = await email_service.send_white_label_setup_complete(
                email=recipient,
                agency_name=kwargs.get('agency_name'),
                custom_domain=kwargs.get('custom_domain'),
                setup_summary=kwargs.get('setup_summary')
            )
        elif email_type == "report_shared":
            result = await email_service.send_analysis_report_shared(
                recipient_email=recipient,
                shared_by=kwargs.get('shared_by'),
                agency_name=kwargs.get('agency_name'),
                analysis_title=kwargs.get('analysis_title'),
                report_url=kwargs.get('report_url'),
                white_label_settings=kwargs.get('white_label_settings')
            )
        elif email_type == "password_reset":
            result = await email_service.send_password_reset(
                email=recipient,
                reset_token=kwargs.get('reset_token'),
                user_name=kwargs.get('user_name'),
                white_label_settings=kwargs.get('white_label_settings')
            )
        else:
            raise ValueError(f"Unknown email type: {email_type}")
        
        # Add task metadata to result
        result.update({
            'task_id': self.request.id,
            'email_type': email_type,
            'recipient': recipient
        })
        
        if result.get('success'):
            logger.info(f"Email {email_type} sent successfully to {recipient}")
        else:
            logger.error(f"Failed to send {email_type} email to {recipient}: {result.get('error')}")
        
        return result
        
    except Exception as exc:
        logger.error(f"Error sending {email_type} email to {recipient}: {exc}")
        self.update_state(
            state='FAILURE',
            meta={'status': str(exc)}
        )
        raise

@celery_app.task
def health_check() -> Dict[str, Any]:
    """
    Simple health check task for monitoring Celery workers.
    
    Returns:
        Dictionary with health check results
    """
    return {
        'status': 'healthy',
        'timestamp': time.time(),
        'worker': 'celery'
    }
"""
Email service implementation using Resend API for production-ready email delivery.
Supports white-label branding, team invitations, and transactional emails.
"""

import httpx
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from pathlib import Path
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Production email service using Resend API with template support and white-label branding."""
    
    def __init__(self):
        """Initialize email service with Resend API and template engine."""
        if not settings.RESEND_API_KEY:
            logger.warning("RESEND_API_KEY not configured - emails will be logged only")
            self._mock_mode = True
        else:
            self.api_key = settings.RESEND_API_KEY
            # Use official Resend API
            self.api_url = 'https://api.resend.com/emails'
            self._mock_mode = False
        
        # Set up Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        if not template_dir.exists():
            template_dir.mkdir(parents=True, exist_ok=True)
            
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
    async def send_team_invitation(self, 
                                 email: str, 
                                 agency_name: str, 
                                 invitation_token: str, 
                                 invited_by: str,
                                 role_name: str = "Team Member",
                                 personal_message: Optional[str] = None,
                                 white_label_settings: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send team invitation email with optional white-label branding.
        
        Args:
            email: Recipient email address
            agency_name: Name of the agency sending invitation
            invitation_token: Secure token for invitation acceptance
            invited_by: Name/email of person sending invitation
            role_name: Role being assigned (Admin, Editor, Viewer, etc.)
            personal_message: Optional personal message from inviter
            white_label_settings: Optional branding customization
            
        Returns:
            Dictionary with send result and metadata
        """
        try:
            # Determine branding settings
            branding = self._get_branding_settings(white_label_settings)
            
            # Generate invitation URL
            base_url = white_label_settings.get('custom_domain', 'https://app.adcopysurge.com') if white_label_settings else 'https://app.adcopysurge.com'
            invitation_url = f"{base_url}/invite/{invitation_token}"
            
            # Prepare template context
            context = {
                'agency_name': agency_name,
                'invited_by': invited_by,
                'role_name': role_name,
                'invitation_url': invitation_url,
                'personal_message': personal_message,
                'branding': branding,
                'current_year': datetime.now().year
            }
            
            # Render email template
            subject = f"You're invited to join {agency_name}"
            if white_label_settings and white_label_settings.get('company_name'):
                subject = f"You're invited to join {white_label_settings['company_name']}"
            
            html_content = await self._render_template('team_invitation.html', context)
            text_content = await self._render_template('team_invitation.txt', context)
            
            return await self._send_email(
                to=email,
                subject=subject,
                html=html_content,
                text=text_content,
                from_email=branding['from_email']
            )
            
        except Exception as e:
            logger.error(f"Failed to send team invitation to {email}: {e}")
            return {'success': False, 'error': str(e)}

    async def send_welcome_email(self,
                               email: str,
                               user_name: str,
                               agency_name: Optional[str] = None,
                               is_agency_owner: bool = False,
                               white_label_settings: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send welcome email to new users with onboarding information.
        
        Args:
            email: New user's email address
            user_name: User's display name
            agency_name: Agency name if applicable
            is_agency_owner: Whether user is creating/owning an agency
            white_label_settings: Optional branding customization
            
        Returns:
            Dictionary with send result and metadata
        """
        try:
            branding = self._get_branding_settings(white_label_settings)
            base_url = white_label_settings.get('custom_domain', 'https://app.adcopysurge.com') if white_label_settings else 'https://app.adcopysurge.com'
            
            context = {
                'user_name': user_name,
                'agency_name': agency_name,
                'is_agency_owner': is_agency_owner,
                'app_url': base_url,
                'branding': branding,
                'current_year': datetime.now().year
            }
            
            subject = f"Welcome to {branding['app_name']}!"
            html_content = await self._render_template('welcome.html', context)
            text_content = await self._render_template('welcome.txt', context)
            
            return await self._send_email(
                to=email,
                subject=subject,
                html=html_content,
                text=text_content,
                from_email=branding['from_email']
            )
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {e}")
            return {'success': False, 'error': str(e)}

    async def send_white_label_setup_complete(self,
                                            email: str,
                                            agency_name: str,
                                            custom_domain: str,
                                            setup_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send confirmation email when white-label setup is completed.
        
        Args:
            email: Agency owner's email
            agency_name: Name of the agency
            custom_domain: Custom domain configured
            setup_summary: Summary of setup configuration
            
        Returns:
            Dictionary with send result and metadata
        """
        try:
            context = {
                'agency_name': agency_name,
                'custom_domain': custom_domain,
                'setup_summary': setup_summary,
                'current_year': datetime.now().year
            }
            
            subject = f"Your white-label setup for {agency_name} is complete!"
            html_content = await self._render_template('setup_complete.html', context)
            text_content = await self._render_template('setup_complete.txt', context)
            
            return await self._send_email(
                to=email,
                subject=subject,
                html=html_content,
                text=text_content,
                from_email=settings.RESEND_FROM_EMAIL
            )
            
        except Exception as e:
            logger.error(f"Failed to send setup complete email to {email}: {e}")
            return {'success': False, 'error': str(e)}

    async def send_analysis_report_shared(self,
                                        recipient_email: str,
                                        shared_by: str,
                                        agency_name: str,
                                        analysis_title: str,
                                        report_url: str,
                                        white_label_settings: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send email when an analysis report is shared.
        
        Args:
            recipient_email: Email of report recipient
            shared_by: Name/email of person sharing
            agency_name: Name of agency sharing the report
            analysis_title: Title of the shared analysis
            report_url: URL to access the report
            white_label_settings: Optional branding customization
            
        Returns:
            Dictionary with send result and metadata
        """
        try:
            branding = self._get_branding_settings(white_label_settings)
            
            context = {
                'shared_by': shared_by,
                'agency_name': agency_name,
                'analysis_title': analysis_title,
                'report_url': report_url,
                'branding': branding,
                'current_year': datetime.now().year
            }
            
            subject = f"{shared_by} shared an analysis report with you"
            html_content = await self._render_template('report_shared.html', context)
            text_content = await self._render_template('report_shared.txt', context)
            
            return await self._send_email(
                to=recipient_email,
                subject=subject,
                html=html_content,
                text=text_content,
                from_email=branding['from_email']
            )
            
        except Exception as e:
            logger.error(f"Failed to send report sharing email to {recipient_email}: {e}")
            return {'success': False, 'error': str(e)}

    async def send_password_reset(self,
                                email: str,
                                reset_token: str,
                                user_name: Optional[str] = None,
                                white_label_settings: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send password reset email (if not handled by Supabase).
        
        Args:
            email: User's email address
            reset_token: Secure reset token
            user_name: User's display name
            white_label_settings: Optional branding customization
            
        Returns:
            Dictionary with send result and metadata
        """
        try:
            branding = self._get_branding_settings(white_label_settings)
            base_url = white_label_settings.get('custom_domain', 'https://app.adcopysurge.com') if white_label_settings else 'https://app.adcopysurge.com'
            reset_url = f"{base_url}/reset-password/{reset_token}"
            
            context = {
                'user_name': user_name or email,
                'reset_url': reset_url,
                'branding': branding,
                'current_year': datetime.now().year
            }
            
            subject = f"Reset your {branding['app_name']} password"
            html_content = await self._render_template('password_reset.html', context)
            text_content = await self._render_template('password_reset.txt', context)
            
            return await self._send_email(
                to=email,
                subject=subject,
                html=html_content,
                text=text_content,
                from_email=branding['from_email']
            )
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            return {'success': False, 'error': str(e)}

    def _get_branding_settings(self, white_label_settings: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get branding settings with fallbacks to default AdCopySurge branding.
        
        Args:
            white_label_settings: Optional white-label configuration
            
        Returns:
            Dictionary with branding configuration
        """
        if not white_label_settings:
            return {
                'app_name': 'AdCopySurge',
                'company_name': 'AdCopySurge',
                'primary_color': '#1976d2',
                'secondary_color': '#dc004e',
                'logo_url': 'https://app.adcopysurge.com/logo.png',
                'from_email': settings.RESEND_FROM_EMAIL,
                'support_email': settings.RESEND_FROM_EMAIL,
                'website_url': 'https://adcopysurge.com'
            }
        
        return {
            'app_name': white_label_settings.get('company_name', 'AdCopySurge'),
            'company_name': white_label_settings.get('company_name', 'AdCopySurge'),
            'primary_color': white_label_settings.get('primary_color', '#1976d2'),
            'secondary_color': white_label_settings.get('secondary_color', '#dc004e'),
            'logo_url': white_label_settings.get('logo_url', 'https://app.adcopysurge.com/logo.png'),
            'from_email': white_label_settings.get('from_email', settings.RESEND_FROM_EMAIL),
            'support_email': white_label_settings.get('support_email', settings.RESEND_FROM_EMAIL),
            'website_url': white_label_settings.get('website_url', 'https://adcopysurge.com')
        }

    async def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render email template with context variables.
        
        Args:
            template_name: Name of template file
            context: Template context variables
            
        Returns:
            Rendered template content
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            # Return simple fallback for critical emails
            if 'invitation' in template_name.lower():
                return self._get_fallback_invitation_template(context)
            return f"Template rendering failed: {str(e)}"
    
    def _get_fallback_invitation_template(self, context: Dict[str, Any]) -> str:
        """Simple fallback template for team invitations when template rendering fails."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>You're invited to join {context.get('agency_name', 'our team')}!</h2>
            <p>{context.get('invited_by', 'A team member')} has invited you to collaborate on ad copy analysis.</p>
            <p>Your role will be: <strong>{context.get('role_name', 'Team Member')}</strong></p>
            {f"<p><em>{context.get('personal_message')}</em></p>" if context.get('personal_message') else ''}
            <p><a href="{context.get('invitation_url', '#')}" style="background-color: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Accept Invitation</a></p>
            <p style="color: #666; font-size: 12px;">This invitation will expire in 7 days.</p>
        </body>
        </html>
        """

    async def _send_email(self,
                         to: str,
                         subject: str,
                         html: str,
                         text: Optional[str] = None,
                         from_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email via Resend API or log in mock mode.
        
        Args:
            to: Recipient email address
            subject: Email subject line
            html: HTML email content
            text: Plain text email content (optional)
            from_email: From email address
            
        Returns:
            Dictionary with send result
        """
        if self._mock_mode:
            logger.info(f"MOCK EMAIL SEND:\nTo: {to}\nSubject: {subject}\nFrom: {from_email or settings.RESEND_FROM_EMAIL}")
            return {
                'success': True,
                'message_id': f'mock-{datetime.now().timestamp()}',
                'mock_mode': True
            }
        
        try:
            # Use official Resend API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json={
                        "from": from_email or settings.RESEND_FROM_EMAIL,
                        "to": [to],
                        "subject": subject,
                        "html": html,
                        "text": text or self._html_to_text(html)
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Email sent successfully to {to} via Resend (ID: {result.get('id')})")
                    return {
                        'success': True,
                        'message_id': result.get('id'),
                        'resend_result': result
                    }
                else:
                    error_msg = f"Resend API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg
                    }
            
        except Exception as e:
            logger.error(f"Failed to send email via Resend to {to}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _html_to_text(self, html: str) -> str:
        """
        Simple HTML to text conversion for plain text email fallback.
        
        Args:
            html: HTML content
            
        Returns:
            Plain text version
        """
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text


# Singleton instance for easy import
email_service = EmailService()
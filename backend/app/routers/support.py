"""
Support contact system API endpoint with rate limiting and email notifications.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import asyncio

from app.core.config import settings
from app.services.email_service import EmailService
from supabase import create_client, Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/support", tags=["support"])

# In-memory rate limiting (for production, use Redis)
rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 3
RATE_LIMIT_WINDOW = timedelta(hours=1)

# Initialize Supabase client
def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    if not settings.REACT_APP_SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(status_code=500, detail="Supabase configuration missing")
    return create_client(settings.REACT_APP_SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

class SupportTicketRequest(BaseModel):
    """Support ticket request model."""
    name: str = Field(..., min_length=2, max_length=100, description="User's name")
    email: EmailStr = Field(..., description="User's email address")
    subject: str = Field(..., min_length=5, max_length=200, description="Ticket subject")
    message: str = Field(..., min_length=20, max_length=5000, description="Ticket message")
    priority: str = Field(default="normal", description="Priority level: normal or urgent")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['normal', 'urgent']:
            raise ValueError('Priority must be either "normal" or "urgent"')
        return v
    
    @validator('subject')
    def validate_subject(cls, v):
        allowed_subjects = [
            'Bug Report',
            'Feature Request',
            'Billing Issue',
            'General Question',
            'Technical Support',
            'Account Issue'
        ]
        if v not in allowed_subjects:
            # Allow custom subjects but log them
            logger.info(f"Custom subject received: {v}")
        return v

class SupportTicketResponse(BaseModel):
    """Support ticket response model."""
    success: bool
    message: str
    ticket_id: Optional[str] = None

def check_rate_limit(identifier: str) -> bool:
    """
    Check if the user has exceeded rate limits.
    
    Args:
        identifier: Email or IP address for rate limiting
        
    Returns:
        True if within limits, False if exceeded
    """
    now = datetime.utcnow()
    cutoff = now - RATE_LIMIT_WINDOW
    
    # Clean old entries
    rate_limit_store[identifier] = [
        timestamp for timestamp in rate_limit_store[identifier]
        if timestamp > cutoff
    ]
    
    # Check limit
    if len(rate_limit_store[identifier]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add new timestamp
    rate_limit_store[identifier].append(now)
    return True

@router.post("/send", response_model=SupportTicketResponse)
async def send_support_ticket(
    ticket: SupportTicketRequest,
    request: Request
):
    """
    Submit a support ticket via email and store in database.
    
    Rate limited to 3 requests per hour per user (by email).
    """
    try:
        # Rate limiting
        rate_limit_id = ticket.email
        if not check_rate_limit(rate_limit_id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please wait before submitting another ticket. Maximum 3 tickets per hour."
            )
        
        # Initialize services
        email_service = EmailService()
        supabase = get_supabase_client()
        
        # Store ticket in database
        ticket_data = {
            "user_id": ticket.user_id,
            "name": ticket.name,
            "email": ticket.email,
            "subject": ticket.subject,
            "message": ticket.message,
            "priority": ticket.priority,
            "status": "open",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Insert into Supabase
        result = supabase.table('support_tickets').insert(ticket_data).execute()
        
        if not result.data:
            logger.error("Failed to insert support ticket into database")
            raise HTTPException(status_code=500, detail="Failed to create support ticket")
        
        ticket_id = result.data[0]['id']
        logger.info(f"Support ticket created with ID: {ticket_id}")
        
        # Prepare email content
        priority_emoji = "🚨" if ticket.priority == "urgent" else "📧"
        email_subject = f"{priority_emoji} New Support Ticket: {ticket.subject}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 12px 12px; }}
                .ticket-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #7C3AED; }}
                .label {{ font-weight: 600; color: #7C3AED; margin-bottom: 5px; }}
                .value {{ color: #333; margin-bottom: 15px; }}
                .message-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .priority-urgent {{ color: #ef4444; font-weight: bold; }}
                .priority-normal {{ color: #10b981; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 30px; color: #6b7280; font-size: 14px; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #7C3AED; color: white; text-decoration: none; border-radius: 8px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 New Support Ticket</h1>
                    <p>Ticket ID: #{ticket_id}</p>
                </div>
                <div class="content">
                    <div class="ticket-info">
                        <div class="label">From:</div>
                        <div class="value">{ticket.name} ({ticket.email})</div>
                        
                        <div class="label">Subject:</div>
                        <div class="value">{ticket.subject}</div>
                        
                        <div class="label">Priority:</div>
                        <div class="value {'priority-urgent' if ticket.priority == 'urgent' else 'priority-normal'}">
                            {ticket.priority.upper()}
                        </div>
                        
                        <div class="label">User ID:</div>
                        <div class="value">{ticket.user_id if ticket.user_id else 'Not authenticated'}</div>
                        
                        <div class="label">Submitted:</div>
                        <div class="value">{datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}</div>
                    </div>
                    
                    <div class="label">Message:</div>
                    <div class="message-box">
                        {ticket.message.replace(chr(10), '<br>')}
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="mailto:{ticket.email}?subject=Re: {ticket.subject}" class="button">
                            Reply to Customer
                        </a>
                    </div>
                    
                    <div class="footer">
                        <p>This ticket was submitted via AdCopy Surge Support Widget</p>
                        <p>Ticket ID: {ticket_id}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
New Support Ticket Received
━━━━━━━━━━━━━━━━━━━━━━━━━━

Ticket ID: #{ticket_id}

FROM: {ticket.name} ({ticket.email})
SUBJECT: {ticket.subject}
PRIORITY: {ticket.priority.upper()}
USER ID: {ticket.user_id if ticket.user_id else 'Not authenticated'}
SUBMITTED: {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}

MESSAGE:
{ticket.message}

━━━━━━━━━━━━━━━━━━━━━━━━━━

Reply to: {ticket.email}
        """
        
        # Send email using Resend
        try:
            email_result = await email_service._send_email(
                to=settings.RESEND_FROM_EMAIL,  # Send to your support email
                subject=email_subject,
                html=html_content,
                text=text_content,
                from_email=settings.RESEND_FROM_EMAIL
            )
        except Exception as email_error:
            logger.error(f"Email service error: {str(email_error)}", exc_info=True)
            email_result = {'success': False, 'error': str(email_error)}
        
        if not email_result.get('success'):
            logger.error(f"Failed to send support email: {email_result.get('error')}")
            # Don't fail the request if email fails, ticket is already saved
            return SupportTicketResponse(
                success=True,
                message="Ticket created but email notification failed. We'll respond to your email directly.",
                ticket_id=str(ticket_id)
            )
        
        logger.info(f"Support email sent successfully for ticket {ticket_id}")
        
        return SupportTicketResponse(
            success=True,
            message="Message sent! We'll respond within 24 hours.",
            ticket_id=str(ticket_id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing support ticket: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to submit support ticket. Please try again later."
        )

@router.get("/status/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    """Get the status of a support ticket."""
    try:
        supabase = get_supabase_client()
        result = supabase.table('support_tickets').select('*').eq('id', ticket_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return result.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch ticket status")

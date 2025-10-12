"""
AdCopySurge Integration API Endpoints
Handles Zapier webhooks, API keys, and integration management
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import json
import sqlite3
import secrets
import hashlib
import hmac
import httpx
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])
security = HTTPBearer()

# Database connection
def get_db():
    conn = sqlite3.connect('adcopysurge.db')
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models
class ZapierWebhookConfig(BaseModel):
    webhook_url: HttpUrl
    data_format: str = "summary"  # full, summary, scores_only
    events: List[str] = ["analysis_completed"]

class SlackWebhookConfig(BaseModel):
    webhook_url: HttpUrl
    channel: Optional[str] = None
    mention_users: Optional[str] = None

class WebhookConfig(BaseModel):
    webhook_url: HttpUrl
    secret_token: Optional[str] = None
    events: List[str] = ["analysis_completed"]

class IntegrationCreate(BaseModel):
    integration_type: str
    name: str
    config: Dict[str, Any]

class IntegrationUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class WebhookPayload(BaseModel):
    event: str
    timestamp: str
    user_id: str
    data: Dict[str, Any]

# Utility functions
def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"acs_{secrets.token_urlsafe(32)}"

def hash_api_key(api_key: str) -> str:
    """Hash API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify webhook signature"""
    if not secret or not signature:
        return True  # Skip verification if no secret
    
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract user from JWT token"""
    # TODO: Implement proper JWT validation
    # For now, return a mock user ID
    return {"id": "user123", "email": "test@example.com"}

@router.post("/webhook/zapier")
async def zapier_webhook(
    payload: WebhookPayload,
    x_signature: Optional[str] = None
):
    """
    Receive webhooks from Zapier
    This endpoint will be called by Zapier when triggered
    """
    try:
        logger.info(f"Received Zapier webhook: {payload.event}")
        
        # Log the webhook for debugging
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO integration_logs (
                user_integration_id, action, status, message, data_sent,
                started_at, completed_at, duration_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "zapier-webhook", "receive_webhook", "success",
            f"Received {payload.event} webhook from Zapier",
            json.dumps(payload.dict()), 
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            0
        ))
        
        db.commit()
        db.close()
        
        return {"status": "success", "message": "Webhook received"}
        
    except Exception as e:
        logger.error(f"Zapier webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_integrations(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all integrations for a user"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT ui.*, i.name as integration_name, i.category, i.features
            FROM user_integrations ui
            JOIN integrations i ON ui.integration_type = i.id
            WHERE ui.user_id = ?
            ORDER BY ui.created_at DESC
        """, (user_id,))
        
        integrations = []
        for row in cursor.fetchall():
            integration = dict(row)
            integration['config'] = json.loads(integration['config']) if integration['config'] else {}
            integration['features'] = json.loads(integration['features']) if integration['features'] else []
            integrations.append(integration)
        
        db.close()
        return integrations
        
    except Exception as e:
        logger.error(f"Error fetching user integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user/{user_id}")
async def create_integration(
    user_id: str,
    integration: IntegrationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new integration for user"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Generate API key if it's an API integration
        if integration.integration_type == "api_access":
            api_key = generate_api_key()
            integration.config['api_key'] = api_key
            integration.config['api_key_hash'] = hash_api_key(api_key)
        
        cursor.execute("""
            INSERT INTO user_integrations (
                user_id, integration_type, name, config, status, enabled, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            integration.integration_type,
            integration.name,
            json.dumps(integration.config),
            "active",
            True,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        integration_id = cursor.lastrowid
        db.commit()
        
        # Test the integration
        await test_integration(integration_id, integration.integration_type, integration.config)
        
        db.close()
        
        return {
            "id": integration_id,
            "status": "created",
            "api_key": integration.config.get('api_key') if integration.integration_type == "api_access" else None
        }
        
    except Exception as e:
        logger.error(f"Error creating integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{integration_id}")
async def update_integration(
    integration_id: int,
    integration_update: IntegrationUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing integration"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Build update query dynamically
        updates = []
        params = []
        
        if integration_update.name:
            updates.append("name = ?")
            params.append(integration_update.name)
            
        if integration_update.config:
            updates.append("config = ?")
            params.append(json.dumps(integration_update.config))
            
        if integration_update.status:
            updates.append("status = ?")
            params.append(integration_update.status)
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(integration_id)
        
        cursor.execute(f"""
            UPDATE user_integrations 
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        
        db.commit()
        db.close()
        
        return {"status": "updated"}
        
    except Exception as e:
        logger.error(f"Error updating integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete an integration"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM user_integrations WHERE id = ?", (integration_id,))
        db.commit()
        db.close()
        
        return {"status": "deleted"}
        
    except Exception as e:
        logger.error(f"Error deleting integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{integration_id}/test")
async def test_integration_endpoint(
    integration_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Test an integration connection"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT integration_type, config FROM user_integrations WHERE id = ?
        """, (integration_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration_type = row[0]
        config = json.loads(row[1])
        
        result = await test_integration(integration_id, integration_type, config)
        
        db.close()
        return result
        
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def test_integration(integration_id: int, integration_type: str, config: dict):
    """Test integration connectivity"""
    try:
        if integration_type == "zapier":
            return await test_zapier_webhook(config)
        elif integration_type == "slack":
            return await test_slack_webhook(config)
        elif integration_type == "webhook":
            return await test_generic_webhook(config)
        else:
            return {"status": "success", "message": "Integration type doesn't require testing"}
            
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        return {"status": "error", "message": str(e)}

async def test_zapier_webhook(config: dict):
    """Test Zapier webhook"""
    test_payload = {
        "event": "test_connection",
        "timestamp": datetime.now().isoformat(),
        "user_id": "test_user",
        "data": {
            "message": "Test connection from AdCopySurge",
            "analysis": {
                "score": 8.5,
                "platform": "facebook",
                "insights": ["Test insight 1", "Test insight 2"]
            }
        }
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            str(config["webhook_url"]),
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return {"status": "success", "message": "Zapier webhook test successful"}
        else:
            return {"status": "error", "message": f"Webhook returned {response.status_code}"}

async def test_slack_webhook(config: dict):
    """Test Slack webhook"""
    slack_payload = {
        "text": "🎉 AdCopySurge integration test successful!",
        "channel": config.get("channel"),
        "username": "AdCopySurge",
        "icon_emoji": ":rocket:",
        "attachments": [{
            "color": "good",
            "fields": [{
                "title": "Status",
                "value": "Connection verified",
                "short": True
            }]
        }]
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            str(config["webhook_url"]),
            json=slack_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return {"status": "success", "message": "Slack webhook test successful"}
        else:
            return {"status": "error", "message": f"Slack webhook returned {response.status_code}"}

async def test_generic_webhook(config: dict):
    """Test generic webhook"""
    test_payload = {
        "event": "test_connection",
        "timestamp": datetime.now().isoformat(),
        "data": {"message": "Test from AdCopySurge"}
    }
    
    headers = {"Content-Type": "application/json"}
    if config.get("secret_token"):
        signature = hmac.new(
            config["secret_token"].encode(),
            json.dumps(test_payload).encode(),
            hashlib.sha256
        ).hexdigest()
        headers["X-AdCopySurge-Signature"] = f"sha256={signature}"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            str(config["webhook_url"]),
            json=test_payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return {"status": "success", "message": "Webhook test successful"}
        else:
            return {"status": "error", "message": f"Webhook returned {response.status_code}"}

@router.post("/send-to-integrations")
async def send_to_integrations(
    user_id: str,
    event_type: str,
    data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Send data to all active user integrations"""
    background_tasks.add_task(process_integrations, user_id, event_type, data)
    return {"status": "processing"}

async def process_integrations(user_id: str, event_type: str, data: Dict[str, Any]):
    """Background task to process integrations"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT id, integration_type, config FROM user_integrations 
            WHERE user_id = ? AND status = 'active' AND enabled = 1
        """, (user_id,))
        
        integrations = cursor.fetchall()
        
        for integration in integrations:
            integration_id, integration_type, config_json = integration
            config = json.loads(config_json)
            
            try:
                await send_to_integration(integration_id, integration_type, config, event_type, data)
                
                # Log success
                cursor.execute("""
                    INSERT INTO integration_logs (
                        user_integration_id, action, status, message,
                        started_at, completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    integration_id, "send_data", "success", f"Sent {event_type} event",
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
                
            except Exception as e:
                logger.error(f"Failed to send to integration {integration_id}: {e}")
                
                # Log error
                cursor.execute("""
                    INSERT INTO integration_logs (
                        user_integration_id, action, status, message, error_details,
                        started_at, completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    integration_id, "send_data", "error", str(e), json.dumps({"error": str(e)}),
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
        
        db.commit()
        db.close()
        
    except Exception as e:
        logger.error(f"Error processing integrations: {e}")

async def send_to_integration(integration_id: int, integration_type: str, config: dict, event_type: str, data: dict):
    """Send data to a specific integration"""
    if integration_type == "zapier":
        await send_to_zapier(config, event_type, data)
    elif integration_type == "slack":
        await send_to_slack(config, event_type, data)
    elif integration_type == "webhook":
        await send_to_webhook(config, event_type, data)

async def send_to_zapier(config: dict, event_type: str, data: dict):
    """Send data to Zapier webhook"""
    # Format data based on config
    data_format = config.get("data_format", "summary")
    
    if data_format == "scores_only":
        payload_data = {
            "score": data.get("score"),
            "platform": data.get("platform"),
            "improvement": data.get("improvement")
        }
    elif data_format == "full":
        payload_data = data
    else:  # summary
        payload_data = {
            "score": data.get("score"),
            "platform": data.get("platform"),
            "improvement": data.get("improvement"),
            "top_insights": data.get("insights", [])[:3]
        }
    
    payload = {
        "event": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": payload_data
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post(str(config["webhook_url"]), json=payload)

async def send_to_slack(config: dict, event_type: str, data: dict):
    """Send notification to Slack"""
    if event_type == "analysis_completed":
        score = data.get("score", 0)
        platform = data.get("platform", "Unknown")
        
        color = "good" if score >= 8 else "warning" if score >= 6 else "danger"
        
        slack_payload = {
            "text": f"📊 New ad analysis completed for {platform.title()}",
            "channel": config.get("channel"),
            "username": "AdCopySurge",
            "icon_emoji": ":rocket:",
            "attachments": [{
                "color": color,
                "fields": [
                    {"title": "Score", "value": f"{score}/10", "short": True},
                    {"title": "Platform", "value": platform.title(), "short": True},
                    {"title": "Improvement", "value": f"+{data.get('improvement', 0)}%", "short": True}
                ]
            }]
        }
        
        if config.get("mention_users"):
            slack_payload["text"] += f" {config['mention_users']}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post(str(config["webhook_url"]), json=slack_payload)

async def send_to_webhook(config: dict, event_type: str, data: dict):
    """Send data to generic webhook"""
    if event_type not in config.get("events", []):
        return  # Event not subscribed
    
    payload = {
        "event": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    headers = {"Content-Type": "application/json"}
    if config.get("secret_token"):
        signature = hmac.new(
            config["secret_token"].encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        headers["X-AdCopySurge-Signature"] = f"sha256={signature}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        await client.post(str(config["webhook_url"]), json=payload, headers=headers)
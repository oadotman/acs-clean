try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import Field, validator
from typing import List, Optional, Union
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
# Get the directory where this config.py file is located
CONFIG_DIR = Path(__file__).resolve().parent
# Go up to backend directory and load .env file
BACKEND_DIR = CONFIG_DIR.parent.parent
ENV_FILE = BACKEND_DIR / ".env"

# Load .env file if it exists (for local development)
# Railway and other production platforms inject environment variables directly
if ENV_FILE.exists():
    print(f"Loading .env file from {ENV_FILE}")
    load_dotenv(dotenv_path=ENV_FILE)
else:
    print(f"No .env file found at {ENV_FILE} - using system environment variables")

# Debug: Print environment detection
print(f"Environment detection: ENVIRONMENT={os.environ.get('ENVIRONMENT', 'not_set')}")
print(f"SECRET_KEY available: {'SECRET_KEY' in os.environ}")
print(f"DATABASE_URL available: {'DATABASE_URL' in os.environ}")

class Settings(BaseSettings):
    # Environment Configuration
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    LOG_LEVEL: str = Field(default="info", description="Logging level")
    
    # Application Settings
    APP_NAME: str = Field(default="AdCopySurge", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    VERSION: str = Field(default="1.0.0", description="Application version for health checks")
    NODE_ENV: str = Field(default="development", description="Node environment equivalent")
    HOST: str = Field(default="127.0.0.1", description="Host to bind to")
    PORT: int = Field(default=8000, description="Port to bind to")
    
    # Platform-specific configuration
    RENDER_EXTERNAL_HOSTNAME: Optional[str] = Field(None, description="Render external hostname")
    RENDER_EXTERNAL_URL: Optional[str] = Field(None, description="Render external URL")
    
    # VPS Configuration
    SERVER_NAME: Optional[str] = Field(None, description="VPS server domain name")
    
    # Security Configuration
    SECRET_KEY: str = Field(..., min_length=32, description="Secret key for JWT tokens")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="JWT token expiration in minutes")
    
    # Database Configuration  
    DATABASE_URL: Optional[str] = Field(None, description="PostgreSQL database URL")
    
    # Supabase Configuration  
    REACT_APP_SUPABASE_URL: Optional[str] = Field(None, description="Supabase project URL")
    REACT_APP_SUPABASE_ANON_KEY: Optional[str] = Field(None, description="Supabase anon key")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(None, description="Supabase service role key")
    SUPABASE_JWT_SECRET: Optional[str] = Field(None, description="Supabase JWT secret for token verification")
    
    # Enhanced Supabase Configuration
    SUPABASE_URL: Optional[str] = Field(None, description="Supabase project URL (alternative to REACT_APP_SUPABASE_URL)")
    SUPABASE_ANON_KEY: Optional[str] = Field(None, description="Supabase anon key (alternative to REACT_APP_SUPABASE_ANON_KEY)")
    ALLOW_ANON: bool = Field(default=False, description="Allow anonymous users when Supabase auth fails or is not configured")
    
    # CORS Configuration
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default="http://localhost:3000,http://127.0.0.1:3000", 
        description="Allowed CORS origins (comma-separated string or list)"
    )
    ALLOWED_HOSTS: Union[str, List[str]] = Field(
        default="localhost,127.0.0.1", 
        description="Allowed hosts (comma-separated string or list)"
    )
    
    # AI Services Configuration
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
    OPENAI_MAX_TOKENS: int = Field(default=2000, description="OpenAI max tokens per request")
    OPENAI_RATE_LIMIT: int = Field(default=100, description="OpenAI requests per minute")
    HUGGINGFACE_API_KEY: Optional[str] = Field(None, description="HuggingFace API key")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # Email Configuration
    SMTP_SERVER: str = Field(default="smtp.gmail.com", description="SMTP server host")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USERNAME: Optional[str] = Field(None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(None, description="SMTP password")
    MAIL_FROM: str = Field(default="noreply@adcopysurge.com", description="Default from email")
    MAIL_FROM_NAME: str = Field(default="AdCopySurge", description="Default from name")
    
    # Resend Email Service (Production)
    RESEND_API_KEY: Optional[str] = Field(None, description="Resend API key for production email delivery")
    RESEND_FROM_EMAIL: str = Field(default="noreply@adcopysurge.com", description="Default from email for Resend")
    RESEND_FROM_NAME: str = Field(default="AdCopySurge", description="Default from name for Resend")
    
    # Paddle Billing Configuration (New Paddle Billing API)
    PADDLE_VENDOR_ID: Optional[str] = Field(None, description="Paddle vendor/seller ID")
    PADDLE_API_KEY: Optional[str] = Field(None, description="Paddle API key for server-side calls")
    PADDLE_CLIENT_TOKEN: Optional[str] = Field(None, description="Paddle client token for frontend checkout")
    PADDLE_WEBHOOK_SECRET: Optional[str] = Field(None, description="Paddle webhook secret for signature verification")
    PADDLE_WEBHOOK_ID: Optional[str] = Field(None, description="Paddle webhook notification ID")
    PADDLE_ENVIRONMENT: str = Field(default="sandbox", description="Paddle environment: sandbox or production")
    PADDLE_API_URL: str = Field(
        default="https://sandbox-api.paddle.com", 
        description="Paddle API URL (auto-set based on environment)"
    )
    
    # Paddle Product Price IDs - Growth Plan
    PADDLE_GROWTH_MONTHLY_PRICE_ID: Optional[str] = Field(None, description="Growth Monthly Plan Price ID")
    PADDLE_GROWTH_YEARLY_PRICE_ID: Optional[str] = Field(None, description="Growth Yearly Plan Price ID")
    
    # Paddle Product Price IDs - Agency Standard Plan
    PADDLE_AGENCY_STANDARD_MONTHLY_PRICE_ID: Optional[str] = Field(None, description="Agency Standard Monthly Plan Price ID")
    PADDLE_AGENCY_STANDARD_YEARLY_PRICE_ID: Optional[str] = Field(None, description="Agency Standard Yearly Plan Price ID")
    
    # Paddle Product Price IDs - Agency Premium Plan
    PADDLE_AGENCY_PREMIUM_MONTHLY_PRICE_ID: Optional[str] = Field(None, description="Agency Premium Monthly Plan Price ID")
    PADDLE_AGENCY_PREMIUM_YEARLY_PRICE_ID: Optional[str] = Field(None, description="Agency Premium Yearly Plan Price ID")
    
    # Paddle Product Price IDs - Agency Unlimited Plan
    PADDLE_AGENCY_UNLIMITED_MONTHLY_PRICE_ID: Optional[str] = Field(None, description="Agency Unlimited Monthly Plan Price ID")
    PADDLE_AGENCY_UNLIMITED_YEARLY_PRICE_ID: Optional[str] = Field(None, description="Agency Unlimited Yearly Plan Price ID")
    
    # Legacy Paddle Product IDs (for backward compatibility)
    PADDLE_BASIC_MONTHLY_ID: Optional[str] = Field(None, description="[LEGACY] Paddle Basic Monthly Product ID")
    PADDLE_PRO_MONTHLY_ID: Optional[str] = Field(None, description="[LEGACY] Paddle Pro Monthly Product ID")
    PADDLE_BASIC_YEARLY_ID: Optional[str] = Field(None, description="[LEGACY] Paddle Basic Yearly Product ID")
    PADDLE_PRO_YEARLY_ID: Optional[str] = Field(None, description="[LEGACY] Paddle Pro Yearly Product ID")
    
    # Monitoring & Error Tracking
    SENTRY_DSN: Optional[str] = Field(None, description="Sentry DSN for error tracking")
    SENTRY_ENVIRONMENT: Optional[str] = Field(None, description="Sentry environment")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=0.1, description="Sentry traces sample rate")
    
    # Performance & Scaling
    WORKERS: int = Field(default=1, description="Number of worker processes")
    KEEP_ALIVE: int = Field(default=2, description="Keep alive timeout")
    MAX_CONNECTIONS: int = Field(default=100, description="Maximum connections")
    
    # Security Headers
    HSTS_MAX_AGE: int = Field(default=31536000, description="HSTS max age")
    CONTENT_SECURITY_POLICY: str = Field(
        default="default-src 'self'; script-src 'self' 'unsafe-inline' cdn.paddle.com https://www.googletagmanager.com; style-src 'self' 'unsafe-inline'; connect-src 'self' https://www.google-analytics.com https://analytics.google.com",
        description="Content Security Policy"
    )
    
    # Feature Flags
    ENABLE_ANALYTICS: bool = Field(default=True, description="Enable analytics")
    ENABLE_COMPETITOR_ANALYSIS: bool = Field(default=False, description="Enable competitor analysis")
    ENABLE_PDF_REPORTS: bool = Field(default=True, description="Enable PDF report generation")
    ENABLE_RATE_LIMITING: bool = Field(default=True, description="Enable API rate limiting")
    ENABLE_BLOG: bool = Field(default=True, description="Enable blog functionality")
    
    # Blog Configuration
    BLOG_CONTENT_DIR: str = Field(default="content/blog", description="Blog content directory path")
    BLOG_GRACEFUL_DEGRADATION: bool = Field(default=True, description="Enable graceful degradation for blog errors")
    
    # Business Configuration
    BASIC_PLAN_PRICE: int = Field(default=49, description="Basic plan price in USD")
    PRO_PLAN_PRICE: int = Field(default=99, description="Pro plan price in USD")
    FREE_TIER_LIMIT: int = Field(default=5, description="Free tier analysis limit")
    BASIC_TIER_LIMIT: int = Field(default=100, description="Basic tier analysis limit")
    PRO_TIER_LIMIT: int = Field(default=500, description="Pro tier analysis limit")
    
    @validator('CORS_ORIGINS', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('ALLOWED_HOSTS', pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            hosts = [host.strip() for host in v.split(',')]
        else:
            hosts = v
        
        # Add Render domains if detected
        render_url = os.getenv('RENDER_EXTERNAL_URL')
        if render_url:
            # Extract hostname from full URL
            if render_url.startswith('http'):
                from urllib.parse import urlparse
                hostname = urlparse(render_url).hostname
                if hostname and hostname not in hosts:
                    hosts.append(hostname)
            else:
                if render_url not in hosts:
                    hosts.append(render_url)
        
        render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')
        if render_hostname and render_hostname not in hosts:
            hosts.append(render_hostname)
        
        # Add common Render patterns
        if os.getenv('RENDER_EXTERNAL_URL') or os.getenv('RENDER_EXTERNAL_HOSTNAME'):
            onrender_pattern = '*.onrender.com'
            if onrender_pattern not in hosts:
                hosts.append(onrender_pattern)
        
        # Add VPS domain if detected
        server_name = os.getenv('SERVER_NAME')
        if server_name and server_name not in hosts:
            hosts.append(server_name)
        
        return hosts
    
    @validator('DEBUG', pre=True)
    def set_debug_based_on_environment(cls, v, values):
        environment = values.get('ENVIRONMENT', 'development')
        # SECURITY: Force debug off in production and Railway
        if environment in ['production', 'railway'] or os.getenv('RAILWAY_ENVIRONMENT'):
            return False
        # SECURITY: Also check for VPS deployment indicators
        if os.getenv('VPS_DEPLOYMENT') or os.getenv('PRODUCTION_VPS'):
            return False
        return v
    
    @validator('PORT', pre=True)
    def set_port_from_env(cls, v):
        """Set PORT from environment variable (Render sets this automatically)"""
        port = os.getenv('PORT')
        if port:
            try:
                return int(port)
            except ValueError:
                pass
        return v
    
    @validator('HOST', pre=True)
    def set_host_for_production(cls, v, values):
        """Set HOST to 0.0.0.0 in production environments"""
        environment = values.get('ENVIRONMENT', 'development')
        if environment in ['production'] or os.getenv('RENDER_EXTERNAL_URL') or os.getenv('RAILWAY_ENVIRONMENT'):
            return "0.0.0.0"
        return v
    
    @validator('CORS_ORIGINS', pre=True)
    def ensure_platform_cors(cls, v):
        """Automatically add platform domains to CORS if detected"""
        if isinstance(v, str):
            origins = [origin.strip() for origin in v.split(',')]
        else:
            origins = v
        
        # Add Railway domain if we're on Railway
        railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN')
        if railway_url and f"https://{railway_url}" not in origins:
            origins.append(f"https://{railway_url}")
        
        # Add Render domain if we're on Render
        render_url = os.getenv('RENDER_EXTERNAL_URL')
        if render_url:
            # RENDER_EXTERNAL_URL includes the full URL, extract hostname
            if render_url.startswith('http'):
                if render_url not in origins:
                    origins.append(render_url)
            else:
                # If it's just hostname, add https protocol
                if f"https://{render_url}" not in origins:
                    origins.append(f"https://{render_url}")
        
        # Also check for RENDER_EXTERNAL_HOSTNAME
        render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')
        if render_hostname and f"https://{render_hostname}" not in origins:
            origins.append(f"https://{render_hostname}")
        
        # Add VPS domain if configured
        server_name = os.getenv('SERVER_NAME')
        if server_name:
            server_url = f"https://{server_name}"
            if server_url not in origins:
                origins.append(server_url)
        
        # Add common Netlify patterns for frontend deployment
        netlify_patterns = [
            "https://*.netlify.app",
            "https://*.netlify.com",
            "https://adcopysurge.netlify.app",
            "https://adcopysurge-frontend.netlify.app"
        ]
        
        # Check if we have specific Netlify URL set in environment
        netlify_url = os.getenv('NETLIFY_URL') or os.getenv('REACT_APP_NETLIFY_URL')
        if netlify_url:
            if not netlify_url.startswith('http'):
                netlify_url = f"https://{netlify_url}"
            if netlify_url not in origins:
                origins.append(netlify_url)
        
        # Add common patterns for production use
        for pattern in netlify_patterns:
            if pattern not in origins:
                origins.append(pattern)
                
        # Add custom domains that might be used
        custom_domains = [
            "https://app.adcopysurge.com",
            "https://adcopysurge.com"
        ]
        
        for domain in custom_domains:
            if domain not in origins:
                origins.append(domain)
            
        return origins
    
    @validator('PADDLE_API_URL', pre=True)
    def set_paddle_api_url(cls, v, values):
        """Auto-configure Paddle API URL based on environment"""
        environment = values.get('PADDLE_ENVIRONMENT', 'sandbox')
        if environment == 'production':
            return "https://api.paddle.com"  # New Paddle Billing API
        return "https://sandbox-api.paddle.com"  # New Paddle Billing API Sandbox
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def is_render(self) -> bool:
        """Check if running on Render platform"""
        return bool(os.getenv('RENDER_EXTERNAL_URL') or os.getenv('RENDER_EXTERNAL_HOSTNAME'))
    
    @property
    def is_railway(self) -> bool:
        """Check if running on Railway platform"""
        return bool(os.getenv('RAILWAY_ENVIRONMENT'))
    
    @property
    def is_vps(self) -> bool:
        """Check if running on VPS (not a managed platform)"""
        return not (self.is_render or self.is_railway)
    
    class Config:
        # Use absolute path to .env file as fallback
        env_file = str(BACKEND_DIR / ".env") if 'BACKEND_DIR' in globals() else ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        # Allow extra fields to make .env file more flexible
        extra = 'ignore'

settings = Settings()

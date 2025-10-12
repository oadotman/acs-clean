# API module exports for FastAPI router imports
from .auth import router as auth_router
from .ads import router as ads_router  
from .analytics import router as analytics_router
from .subscriptions import router as subscriptions_router

# Import modules directly for compatibility with "from app.api import auth" style imports
from . import auth
from . import ads
from . import analytics
from . import subscriptions
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class SubscriptionTier(enum.Enum):
    FREE = "free"
    GROWTH = "growth"
    AGENCY_STANDARD = "agency_standard"
    AGENCY_PREMIUM = "agency_premium"
    AGENCY_UNLIMITED = "agency_unlimited"
    # Legacy values for backward compatibility
    BASIC = "basic"  # Maps to GROWTH
    PRO = "pro"      # Maps to AGENCY_UNLIMITED

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    company = Column(String, nullable=True)
    
    # Subscription info
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    monthly_analyses = Column(Integer, default=0)
    subscription_active = Column(Boolean, default=True)
    
    # Legacy Stripe fields (will be removed after migration)
    stripe_customer_id = Column(String, nullable=True)
    
    # Supabase integration field (for hybrid auth approach)
    supabase_user_id = Column(String, nullable=True, unique=True, index=True)
    
    # Paddle billing fields
    paddle_subscription_id = Column(String, nullable=True, index=True)
    paddle_plan_id = Column(String, nullable=True)
    paddle_checkout_id = Column(String, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analyses = relationship("AdAnalysis", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email='{self.email}', subscription='{self.subscription_tier.value}')>"

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.models.user import User, SubscriptionTier
from app.core.config import settings

class AuthService:
    """Authentication and user management service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, email: str, password: str, full_name: str, 
                   company: Optional[str] = None) -> User:
        """Create a new user"""
        hashed_password = self.get_password_hash(password)
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            company=company,
            subscription_tier=SubscriptionTier.FREE
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
            if email is None:
                return None
        except JWTError:
            return None
        
        user = self.get_user_by_email(email)
        return user
    
    def update_user_subscription(self, user_id: int, tier: SubscriptionTier, 
                               stripe_customer_id: Optional[str] = None) -> User:
        """Update user subscription tier"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.subscription_tier = tier
        if stripe_customer_id:
            user.stripe_customer_id = stripe_customer_id
        
        # Reset monthly analysis count on upgrade
        user.monthly_analyses = 0
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def increment_user_analyses(self, user_id: int) -> None:
        """Increment user's monthly analysis count"""
        user = self.get_user_by_id(user_id)
        if user:
            user.monthly_analyses += 1
            self.db.commit()

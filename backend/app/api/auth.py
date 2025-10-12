from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService
from pydantic import BaseModel, EmailStr

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    company: Optional[str] = None
    subscription_tier: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    auth_service = AuthService(db)
    
    # Check if user already exists
    if auth_service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    user = auth_service.create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        company=user_data.company
    )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        subscription_tier=user.subscription_tier,
        is_active=user.is_active
    )

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user information"""
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        subscription_tier=user.subscription_tier,
        is_active=user.is_active
    )


# Dependency functions for authentication
async def get_current_user_dep(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current user as dependency for other endpoints"""
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def require_admin(current_user: User = Depends(get_current_user_dep)) -> User:
    """Require admin role for blog management"""
    # For now, we'll use email-based admin check
    # In production, you'd want to add an is_admin field to the User model
    admin_emails = [
        "admin@adcopysurge.com",
        "blog@adcopysurge.com",
        # Add more admin emails as needed
    ]
    
    if current_user.email not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user

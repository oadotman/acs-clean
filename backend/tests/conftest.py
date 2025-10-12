import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.core.database import get_db, Base
from app.models.user import User
from app.models.ad_analysis import AdAnalysis

# Test database URL (SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def db_engine():
    """Create database tables for testing."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a fresh database session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client() -> Generator:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "company": "Test Company"
    }


@pytest.fixture
def sample_ad_data():
    """Sample ad data for testing."""
    return {
        "headline": "Amazing Product Launch!",
        "body_text": "Discover the future of productivity with our revolutionary new app.",
        "cta": "Get Started Now",
        "platform": "facebook",
        "target_audience": "professionals",
        "industry": "technology"
    }


@pytest.fixture
def authenticated_headers(client: TestClient, sample_user_data: dict):
    """Get authentication headers for testing."""
    # Register user
    client.post("/api/auth/register", json=sample_user_data)
    
    # Login to get token
    login_data = {
        "username": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    response = client.post("/api/auth/token", data=login_data)
    token_data = response.json()
    
    return {"Authorization": f"Bearer {token_data['access_token']}"}


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

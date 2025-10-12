from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os
import time
import logging
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type

# Create both sync and async engines for Railway compatibility
logger = logging.getLogger(__name__)

@retry(
    wait=wait_fixed(2),
    stop=stop_after_attempt(10),
    retry=retry_if_exception_type((Exception,))
)
def test_database_connection(engine):
    """Test database connection with retries for Railway startup delays"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.warning(f"Database connection test failed: {e}")
        raise

try:
    # Check if DATABASE_URL is available
    if not settings.DATABASE_URL:
        logger.warning("DATABASE_URL not set - database will not be available")
        raise ValueError("DATABASE_URL is required")
    
    # Sync engine for compatibility with existing code
    sync_database_url = settings.DATABASE_URL
    if sync_database_url.startswith("postgresql://"):
        sync_database_url = sync_database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    # Enhanced connection settings for Railway
    engine = create_engine(
        sync_database_url,
        pool_pre_ping=True,      # Handle connection drops
        pool_recycle=3600,       # Recycle connections every hour
        pool_timeout=20,         # Wait up to 20 seconds for connection
        pool_size=5,             # Smaller pool for Railway memory limits
        max_overflow=10,         # Allow extra connections when needed
        echo=False,              # Set to True for SQL logging in dev
        connect_args={
            "connect_timeout": 10,   # PostgreSQL connection timeout
            "application_name": "adcopysurge-api"
        }
    )
    
    # Test connection with retries (important for Railway cold starts)
    if os.getenv("ENVIRONMENT") == "production":
        logger.info("Testing database connection with retries...")
        test_database_connection(engine)
        logger.info("Database connection verified")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Async engine for async endpoints (only for PostgreSQL)
    async_database_url = settings.DATABASE_URL
    if async_database_url and async_database_url.startswith("postgresql://"):
        async_database_url = async_database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        try:
            async_engine = create_async_engine(
                async_database_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_timeout=20,
                pool_size=5,
                max_overflow=10,
                echo=False
            )
            AsyncSessionLocal = sessionmaker(
                bind=async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            logger.info("Async PostgreSQL engine created successfully")
        except Exception as async_err:
            logger.warning(f"Async engine creation failed, falling back to sync: {async_err}")
            async_engine = None
            AsyncSessionLocal = None
    else:
        # SQLite or other non-async databases - don't create async engine
        logger.info("Non-PostgreSQL database detected - async engine disabled")
        async_engine = None
        AsyncSessionLocal = None
    
except Exception as e:
    # Handle database connection issues gracefully
    logger.warning(f"Database engine creation failed: {e}")
    print(f"⚠️ Database not available: {e}")
    print("Application will continue without database functionality")
    engine = None
    async_engine = None
    SessionLocal = None
    AsyncSessionLocal = None

Base = declarative_base()

def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not available - ensure PostgreSQL is configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

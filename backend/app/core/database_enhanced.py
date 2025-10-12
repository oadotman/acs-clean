"""
Enhanced database module with proper async/sync handling and graceful degradation
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import time
import logging
from typing import Generator, Optional
from contextlib import asynccontextmanager
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type

try:
    from app.core.config import settings
except ImportError:
    class MockSettings:
        DATABASE_URL = "sqlite:///./test.db"
        ENVIRONMENT = "development"
    settings = MockSettings()

logger = logging.getLogger(__name__)

# Global database objects
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None
Base = declarative_base()

class DatabaseManager:
    """Centralized database management with async/sync support"""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        self.is_async_supported = False
        self.is_connected = False
        
    @retry(
        wait=wait_fixed(2),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((Exception,))
    )
    def test_connection(self, engine) -> bool:
        """Test database connection with retries"""
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.warning(f"Database connection test failed: {e}")
            raise
    
    def initialize_sync_engine(self) -> bool:
        """Initialize synchronous database engine"""
        try:
            if not settings.DATABASE_URL:
                logger.warning("DATABASE_URL not configured")
                return False
            
            sync_url = settings.DATABASE_URL
            connect_args = {}
            
            # Handle SQLite special case
            if sync_url.startswith("sqlite"):
                connect_args = {
                    "check_same_thread": False
                }
                # Use StaticPool for SQLite to avoid threading issues
                self.engine = create_engine(
                    sync_url,
                    echo=False,
                    connect_args=connect_args,
                    poolclass=StaticPool,
                    pool_pre_ping=True
                )
            else:
                # PostgreSQL configuration
                if sync_url.startswith("postgresql://"):
                    sync_url = sync_url.replace("postgresql://", "postgresql+psycopg2://", 1)
                
                connect_args = {
                    "connect_timeout": 10,
                    "application_name": "adcopysurge-api"
                }
                
                self.engine = create_engine(
                    sync_url,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    pool_timeout=20,
                    pool_size=5,
                    max_overflow=10,
                    echo=False,
                    connect_args=connect_args
                )
            
            # Test connection (skip timeout test for SQLite)
            if settings.ENVIRONMENT == "production" and not sync_url.startswith("sqlite"):
                self.test_connection(self.engine)
            
            self.SessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=self.engine
            )
            
            self.is_connected = True
            logger.info(f"Sync database engine initialized: {sync_url.split('://')[0]}")
            return True
            
        except Exception as e:
            logger.error(f"Sync engine initialization failed: {e}")
            self.engine = None
            self.SessionLocal = None
            return False
    
    def initialize_async_engine(self) -> bool:
        """Initialize asynchronous database engine (PostgreSQL only)"""
        try:
            if not settings.DATABASE_URL:
                return False
            
            # Only PostgreSQL supports async
            if not settings.DATABASE_URL.startswith("postgresql"):
                logger.info("Async engine only supported for PostgreSQL")
                return False
            
            async_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            
            self.async_engine = create_async_engine(
                async_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_timeout=20,
                pool_size=5,
                max_overflow=10,
                echo=False
            )
            
            self.AsyncSessionLocal = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self.is_async_supported = True
            logger.info("Async PostgreSQL engine initialized successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Async engine initialization failed: {e}")
            self.async_engine = None
            self.AsyncSessionLocal = None
            self.is_async_supported = False
            return False
    
    def initialize(self) -> dict:
        """Initialize all database engines and return status"""
        status = {
            "sync": False,
            "async": False,
            "database_type": "unknown",
            "error": None
        }
        
        try:
            # Initialize sync engine first (required)
            status["sync"] = self.initialize_sync_engine()
            
            if status["sync"]:
                # Determine database type
                db_url = settings.DATABASE_URL.lower()
                if db_url.startswith("sqlite"):
                    status["database_type"] = "sqlite"
                elif db_url.startswith("postgresql"):
                    status["database_type"] = "postgresql"
                    # Try to initialize async engine for PostgreSQL
                    status["async"] = self.initialize_async_engine()
                else:
                    status["database_type"] = "other"
            
        except Exception as e:
            status["error"] = str(e)
            logger.error(f"Database initialization failed: {e}")
        
        return status
    
    def get_sync_session(self):
        """Get synchronous database session"""
        if not self.SessionLocal:
            raise RuntimeError("Sync database not initialized")
        return self.SessionLocal()
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get asynchronous database session"""
        if not self.AsyncSessionLocal:
            raise RuntimeError("Async database not initialized")
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    
    def get_health_status(self) -> dict:
        """Get database health status"""
        return {
            "connected": self.is_connected,
            "sync_available": self.engine is not None,
            "async_available": self.async_engine is not None,
            "async_supported": self.is_async_supported,
            "session_factory": self.SessionLocal is not None
        }

# Global database manager instance
db_manager = DatabaseManager()

# Initialize on module import
init_status = db_manager.initialize()
logger.info(f"Database initialization status: {init_status}")

# Set global variables for backward compatibility
engine = db_manager.engine
async_engine = db_manager.async_engine
SessionLocal = db_manager.SessionLocal
AsyncSessionLocal = db_manager.AsyncSessionLocal

def get_db() -> Generator:
    """FastAPI dependency for sync database sessions"""
    if not db_manager.SessionLocal:
        raise RuntimeError("Database not available - ensure DATABASE_URL is configured")
    
    db = db_manager.get_sync_session()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """FastAPI dependency for async database sessions"""
    if not db_manager.AsyncSessionLocal:
        raise RuntimeError("Async database not available")
    
    async with db_manager.get_async_session() as session:
        yield session

def get_database_health() -> dict:
    """Get comprehensive database health information"""
    health = db_manager.get_health_status()
    health["initialization_status"] = init_status
    return health

# Migration helper function
def create_all_tables():
    """Create all database tables"""
    if engine:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    else:
        logger.warning("Cannot create tables - database engine not available")

# Export commonly used objects
__all__ = [
    'engine', 'async_engine', 'SessionLocal', 'AsyncSessionLocal', 'Base',
    'get_db', 'get_async_db', 'get_database_health', 'create_all_tables',
    'db_manager'
]
#!/usr/bin/env python3
"""
AdCopySurge Database Initialization Script
Run this script to initialize the database for production
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_tables():
    """Create database tables if they don't exist"""
    try:
        # For SQLite, we'll create basic tables
        import sqlite3
        
        db_path = os.getenv("DATABASE_URL", "sqlite:///./adcopysurge.db")
        if db_path.startswith("sqlite:///"):
            db_file = db_path.replace("sqlite:///", "")
            
            logger.info(f"Creating SQLite database: {db_file}")
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Create projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    target_audience TEXT,
                    industry TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create ad_analyses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ad_analyses (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    headline TEXT NOT NULL,
                    body_text TEXT NOT NULL,
                    cta TEXT NOT NULL,
                    platform TEXT DEFAULT 'facebook',
                    overall_score REAL,
                    clarity_score REAL,
                    persuasion_score REAL,
                    emotion_score REAL,
                    cta_strength REAL,
                    platform_fit_score REAL,
                    feedback TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''')
            
            # Create alternatives table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ad_alternatives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    variant_type TEXT NOT NULL,
                    headline TEXT NOT NULL,
                    body_text TEXT NOT NULL,
                    cta TEXT NOT NULL,
                    improvement_reason TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES ad_analyses (id)
                )
            ''')
            
            # Create users table (for future use)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    full_name TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    subscription_tier TEXT DEFAULT 'free',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ad_analyses_project_id ON ad_analyses(project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ad_analyses_created_at ON ad_analyses(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Database tables created successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def seed_initial_data():
    """Seed the database with initial data if needed"""
    try:
        db_path = os.getenv("DATABASE_URL", "sqlite:///./adcopysurge.db")
        if db_path.startswith("sqlite:///"):
            db_file = db_path.replace("sqlite:///", "")
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Check if we need to seed data
            cursor.execute("SELECT COUNT(*) FROM projects")
            project_count = cursor.fetchone()[0]
            
            if project_count == 0:
                logger.info("Seeding initial data...")
                
                # Add a sample project
                cursor.execute('''
                    INSERT INTO projects (id, name, description, target_audience, industry)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    'sample_project_001',
                    'Sample Marketing Campaign',
                    'A sample project to demonstrate AdCopySurge capabilities',
                    'Small business owners',
                    'Marketing'
                ))
                
                conn.commit()
                logger.info("✅ Initial data seeded successfully!")
            
            conn.close()
            return True
            
    except Exception as e:
        logger.error(f"❌ Data seeding failed: {e}")
        return False

def main():
    """Main initialization function"""
    logger.info("🚀 Starting AdCopySurge database initialization...")
    
    # Load environment variables if .env file exists
    if os.path.exists('.env'):
        from python_decouple import config
        logger.info("Loading environment variables from .env file")
    
    # Create database tables
    if not create_database_tables():
        sys.exit(1)
    
    # Seed initial data
    if not seed_initial_data():
        logger.warning("⚠️  Data seeding failed, but continuing...")
    
    logger.info("✅ Database initialization completed!")

if __name__ == "__main__":
    main()

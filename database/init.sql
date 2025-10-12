-- AdCopySurge Database Initialization
-- Basic setup for PostgreSQL

-- Create database if not exists (handled by Docker)
-- CREATE DATABASE adcopysurge;

-- Connect to the database
\c adcopysurge;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable logging
SET log_statement = 'all';

-- Simple table structure will be created by SQLAlchemy migrations
-- This init script just ensures the database is ready

-- Success message
SELECT 'AdCopySurge database initialized successfully!' as message;

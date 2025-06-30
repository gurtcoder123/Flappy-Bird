#!/usr/bin/env python3
"""
Database migration script for external deployment
Supports both SQLite (development) and PostgreSQL (production)
"""
import os
import sys
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_type():
    """Determine database type from DATABASE_URL"""
    database_url = os.getenv('DATABASE_URL', '')
    if database_url.startswith('postgresql://') or database_url.startswith('postgres://'):
        return 'postgresql'
    else:
        return 'sqlite'

def create_postgresql_tables():
    """Create PostgreSQL tables for production deployment"""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found for PostgreSQL setup")
    
    logger.info("Setting up PostgreSQL database...")
    
    # Parse database URL
    parsed = urlparse(database_url)
    
    conn = psycopg2.connect(database_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Create tables with PostgreSQL syntax
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_verified BOOLEAN DEFAULT FALSE,
            verification_token VARCHAR(255),
            reset_token VARCHAR(255),
            reset_token_expires TIMESTAMP,
            coins INTEGER DEFAULT 0,
            selected_character INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS game_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            score INTEGER NOT NULL,
            play_time INTEGER NOT NULL,
            character_used INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_unlocks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            item_type VARCHAR(50) NOT NULL,
            item_id INTEGER NOT NULL,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, item_type, item_id)
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_game_history_user_id ON game_history(user_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_game_history_score ON game_history(score DESC);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_user_unlocks_user_id ON user_unlocks(user_id);
        """
    ]
    
    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            logger.info(f"Executed: {table_sql.strip()[:50]}...")
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise
    
    cursor.close()
    conn.close()
    logger.info("PostgreSQL database setup complete!")

def create_sqlite_tables():
    """Create SQLite tables for development"""
    import sqlite3
    
    logger.info("Setting up SQLite database...")
    
    conn = sqlite3.connect('flappy_bird.db')
    cursor = conn.cursor()
    
    # Create tables with SQLite syntax
    tables = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            verification_token TEXT,
            reset_token TEXT,
            reset_token_expires TEXT,
            coins INTEGER DEFAULT 0,
            selected_character INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            score INTEGER NOT NULL,
            play_time INTEGER NOT NULL,
            character_used INTEGER DEFAULT 0,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_unlocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            item_type TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, item_type, item_id)
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_game_history_user_id ON game_history(user_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_game_history_score ON game_history(score DESC);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_user_unlocks_user_id ON user_unlocks(user_id);
        """
    ]
    
    for table_sql in tables:
        try:
            cursor.execute(table_sql)
            logger.info(f"Executed: {table_sql.strip()[:50]}...")
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise
    
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("SQLite database setup complete!")

def migrate_database():
    """Run database migration based on environment"""
    try:
        db_type = get_database_type()
        logger.info(f"Detected database type: {db_type}")
        
        if db_type == 'postgresql':
            create_postgresql_tables()
        else:
            create_sqlite_tables()
            
        logger.info("Database migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
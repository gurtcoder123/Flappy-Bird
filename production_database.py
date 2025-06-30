"""
Production-ready database adapter for external deployment
Supports both SQLite (development) and PostgreSQL (production)
"""
import os
import hashlib
import secrets
import logging
from urllib.parse import urlparse
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ProductionDatabase:
    def __init__(self):
        self.db_type = self._get_database_type()
        self.connection = None
        self._init_connection()
    
    def _get_database_type(self):
        """Determine database type from DATABASE_URL"""
        database_url = os.getenv('DATABASE_URL', '')
        if database_url.startswith('postgresql://') or database_url.startswith('postgres://'):
            return 'postgresql'
        else:
            return 'sqlite'
    
    def _init_connection(self):
        """Initialize database connection based on type"""
        if self.db_type == 'postgresql':
            self._init_postgresql()
        else:
            self._init_sqlite()
    
    def _init_postgresql(self):
        """Initialize PostgreSQL connection"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL not found for PostgreSQL")
            
            self.connection = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            logger.info("PostgreSQL connection established")
            
        except ImportError:
            logger.error("psycopg2 not installed. Install with: pip install psycopg2-binary")
            raise
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            raise
    
    def _init_sqlite(self):
        """Initialize SQLite connection"""
        import sqlite3
        
        db_path = "flappy_bird.db"
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        logger.info(f"SQLite connection established: {db_path}")
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Execute database query with proper error handling"""
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_one:
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch_all:
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Database query failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            cursor.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self, length=32):
        """Generate random token"""
        return secrets.token_urlsafe(length)
    
    def create_user(self, email, username, password):
        """Create new user account"""
        password_hash = self.hash_password(password)
        verification_token = self.generate_token()
        
        if self.db_type == 'postgresql':
            query = """
                INSERT INTO users (email, username, password_hash, verification_token)
                VALUES (%s, %s, %s, %s) RETURNING id
            """
        else:
            query = """
                INSERT INTO users (email, username, password_hash, verification_token)
                VALUES (?, ?, ?, ?)
            """
        
        try:
            if self.db_type == 'postgresql':
                result = self.execute_query(query, (email, username, password_hash, verification_token), fetch_one=True)
                user_id = result['id'] if result else None
            else:
                self.execute_query(query, (email, username, password_hash, verification_token))
                user_id = self.connection.lastrowid
            
            logger.info(f"User created successfully: {username}")
            return user_id, verification_token
            
        except Exception as e:
            if "UNIQUE constraint failed" in str(e) or "duplicate key value" in str(e):
                if "email" in str(e):
                    raise ValueError("Email address already registered")
                else:
                    raise ValueError("Username already taken")
            raise
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        password_hash = self.hash_password(password)
        
        if self.db_type == 'postgresql':
            query = "SELECT * FROM users WHERE email = %s AND password_hash = %s AND is_verified = TRUE"
        else:
            query = "SELECT * FROM users WHERE email = ? AND password_hash = ? AND is_verified = 1"
        
        user = self.execute_query(query, (email, password_hash), fetch_one=True)
        
        if user:
            logger.info(f"User authenticated: {user['username']}")
            return user
        else:
            logger.warning(f"Authentication failed for email: {email}")
            return None
    
    def verify_user(self, token):
        """Verify user email with token"""
        if self.db_type == 'postgresql':
            query = "UPDATE users SET is_verified = TRUE, verification_token = NULL WHERE verification_token = %s"
        else:
            query = "UPDATE users SET is_verified = 1, verification_token = NULL WHERE verification_token = ?"
        
        rows_affected = self.execute_query(query, (token,))
        success = rows_affected > 0
        
        if success:
            logger.info("User verified successfully")
        else:
            logger.warning(f"Verification failed for token: {token}")
        
        return success
    
    def save_game_score(self, user_id, score, play_time, character_used=0):
        """Save game score to history"""
        if self.db_type == 'postgresql':
            query = """
                INSERT INTO game_history (user_id, score, play_time, character_used)
                VALUES (%s, %s, %s, %s)
            """
        else:
            query = """
                INSERT INTO game_history (user_id, score, play_time, character_used)
                VALUES (?, ?, ?, ?)
            """
        
        self.execute_query(query, (user_id, score, play_time, character_used))
        logger.info(f"Game score saved: User {user_id}, Score {score}")
    
    def get_leaderboard(self, limit=100):
        """Get top players leaderboard"""
        if self.db_type == 'postgresql':
            query = """
                SELECT u.username, g.score, g.timestamp, g.character_used
                FROM game_history g
                JOIN users u ON g.user_id = u.id
                ORDER BY g.score DESC
                LIMIT %s
            """
        else:
            query = """
                SELECT u.username, g.score, g.timestamp, g.character_used
                FROM game_history g
                JOIN users u ON g.user_id = u.id
                ORDER BY g.score DESC
                LIMIT ?
            """
        
        return self.execute_query(query, (limit,), fetch_all=True)
    
    def get_user_history(self, user_id):
        """Get user's game history"""
        if self.db_type == 'postgresql':
            query = """
                SELECT score, play_time, character_used, timestamp
                FROM game_history
                WHERE user_id = %s
                ORDER BY timestamp DESC
            """
        else:
            query = """
                SELECT score, play_time, character_used, timestamp
                FROM game_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """
        
        return self.execute_query(query, (user_id,), fetch_all=True)
    
    def update_user_coins(self, user_id, coins):
        """Update user's coin balance"""
        if self.db_type == 'postgresql':
            query = "UPDATE users SET coins = %s WHERE id = %s"
        else:
            query = "UPDATE users SET coins = ? WHERE id = ?"
        
        self.execute_query(query, (coins, user_id))
        logger.info(f"Updated coins for user {user_id}: {coins}")
    
    def unlock_character(self, user_id, character_id):
        """Unlock character for user"""
        if self.db_type == 'postgresql':
            query = """
                INSERT INTO user_unlocks (user_id, item_type, item_id)
                VALUES (%s, 'character', %s)
                ON CONFLICT (user_id, item_type, item_id) DO NOTHING
            """
        else:
            query = """
                INSERT OR IGNORE INTO user_unlocks (user_id, item_type, item_id)
                VALUES (?, 'character', ?)
            """
        
        self.execute_query(query, (user_id, character_id))
        logger.info(f"Character {character_id} unlocked for user {user_id}")
    
    def get_user_unlocks(self, user_id):
        """Get user's unlocked items"""
        if self.db_type == 'postgresql':
            query = "SELECT item_type, item_id FROM user_unlocks WHERE user_id = %s"
        else:
            query = "SELECT item_type, item_id FROM user_unlocks WHERE user_id = ?"
        
        return self.execute_query(query, (user_id,), fetch_all=True)
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
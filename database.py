import sqlite3
import hashlib
import random
import string
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path="flappy_bird.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE,
                verification_token TEXT,
                reset_token TEXT,
                reset_token_expires DATETIME,
                coins INTEGER DEFAULT 25,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Game history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                score INTEGER NOT NULL,
                play_time INTEGER NOT NULL,
                played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User unlocks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_unlocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                unlock_type TEXT NOT NULL,
                unlock_name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self, length=32):
        """Generate random token"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def create_user(self, email, username, password):
        """Create new user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            verification_token = self.generate_token()
            
            cursor.execute('''
                INSERT INTO users (email, username, password_hash, verification_token)
                VALUES (?, ?, ?, ?)
            ''', (email, username, password_hash, verification_token))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id, verification_token
        except sqlite3.IntegrityError:
            raise ValueError("Email or username already exists")
        finally:
            conn.close()
    
    def verify_user(self, token):
        """Verify user email with token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET is_verified = TRUE, verification_token = NULL
            WHERE verification_token = ?
        ''', (token,))
        
        result = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return result
    
    def verify_user_by_id(self, user_id):
        """Verify user by ID (for automatic verification)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET is_verified = TRUE, verification_token = NULL
            WHERE id = ?
        ''', (user_id,))
        
        result = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return result
    
    def authenticate_user(self, email, password, skip_password_check=False):
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if skip_password_check:
            # Just get user by email (for internal use)
            cursor.execute('''
                SELECT id, username, is_verified, coins FROM users
                WHERE email = ?
            ''', (email,))
        else:
            # Normal authentication with password
            password_hash = self.hash_password(password)
            cursor.execute('''
                SELECT id, username, is_verified, coins FROM users
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and user[2]:  # Check if verified
            return {
                'id': user[0],
                'username': user[1],
                'email': email,
                'coins': user[3]
            }
        return None
    
    def request_password_reset(self, email):
        """Request password reset"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        reset_token = self.generate_token()
        expires = datetime.now() + timedelta(hours=1)
        
        cursor.execute('''
            UPDATE users SET reset_token = ?, reset_token_expires = ?
            WHERE email = ? AND is_verified = TRUE
        ''', (reset_token, expires, email))
        
        result = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return reset_token if result else None
    
    def reset_password(self, token, new_password):
        """Reset password with token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(new_password)
        cursor.execute('''
            UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expires = NULL
            WHERE reset_token = ? AND reset_token_expires > ?
        ''', (password_hash, token, datetime.now()))
        
        result = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return result
    
    def save_game_score(self, user_id, score, play_time):
        """Save game score to history"""
        if user_id is None:  # Guest user
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO game_history (user_id, score, play_time)
            VALUES (?, ?, ?)
        ''', (user_id, score, play_time))
        
        # Award coins (1 point = 1 coin)
        cursor.execute('''
            UPDATE users SET coins = coins + ?
            WHERE id = ?
        ''', (score, user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_history(self, user_id):
        """Get user's game history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT score, play_time, played_at FROM game_history
            WHERE user_id = ?
            ORDER BY played_at DESC
            LIMIT 50
        ''', (user_id,))
        
        history = cursor.fetchall()
        conn.close()
        return history
    
    def get_leaderboard(self, limit=100):
        """Get top players leaderboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.username, MAX(gh.score) as best_score
            FROM users u
            JOIN game_history gh ON u.id = gh.user_id
            GROUP BY u.id, u.username
            ORDER BY best_score DESC
            LIMIT ?
        ''', (limit,))
        
        leaderboard = cursor.fetchall()
        conn.close()
        return leaderboard
    
    def get_user_rank(self, user_id):
        """Get user's rank in leaderboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            WITH user_scores AS (
                SELECT u.id, u.username, MAX(gh.score) as best_score
                FROM users u
                JOIN game_history gh ON u.id = gh.user_id
                GROUP BY u.id, u.username
            ),
            ranked_scores AS (
                SELECT id, username, best_score,
                       ROW_NUMBER() OVER (ORDER BY best_score DESC) as rank
                FROM user_scores
            )
            SELECT rank FROM ranked_scores WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_user_coins(self, user_id):
        """Get user's current coin balance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT coins FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0
    
    def update_user_coins(self, user_id, coins):
        """Update user's coin balance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET coins = ?
            WHERE id = ?
        ''', (coins, user_id))
        
        conn.commit()
        conn.close()
    
    def unlock_character(self, user_id, character_id):
        """Unlock character for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO user_unlocks (user_id, unlock_type, unlock_name)
            VALUES (?, 'character', ?)
        ''', (user_id, str(character_id)))
        
        conn.commit()
        conn.close()
    
    def get_user_unlocks(self, user_id):
        """Get user's unlocked characters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT unlock_name FROM user_unlocks 
            WHERE user_id = ? AND unlock_type = 'character'
        ''', (user_id,))
        
        unlocks = cursor.fetchall()
        conn.close()
        return [int(unlock[0]) for unlock in unlocks]
    
    def close(self):
        """Close database connection"""
        pass  # Using context managers, no persistent connection

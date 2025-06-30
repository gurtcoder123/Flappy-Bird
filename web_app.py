from flask import Flask, render_template, jsonify, request, session
import json
import secrets
from database import Database
from email_service import EmailService
import re
import time
import os

app = Flask(__name__)
# Use production secret key (prioritize SECRET_KEY, fallback to SESSION_SECRET, then generate)
app.secret_key = os.getenv('SECRET_KEY') or os.getenv('SESSION_SECRET') or secrets.token_hex(32)

# Production configuration
app.config['ENV'] = 'production' if os.getenv('REPLIT_DEPLOYMENT') else 'development'
app.config['DEBUG'] = False if os.getenv('REPLIT_DEPLOYMENT') else True

# Additional production optimizations
if os.getenv('REPLIT_DEPLOYMENT'):
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    
# Disable expensive operations during production initialization
if os.getenv('REPLIT_DEPLOYMENT'):
    # Lazy load database to avoid startup delays
    database = None
    email_service = None
else:
    # Initialize systems for development
    database = Database()
    email_service = EmailService()

def get_database():
    """Lazy load database connection"""
    global database
    if database is None:
        database = Database()
    return database

def get_email_service():
    """Lazy load email service"""
    global email_service
    if email_service is None:
        email_service = EmailService()
    return email_service

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Optimized health check endpoint for fast deployment verification"""
    import time
    
    # Fast response for basic health check
    health_status = {
        'status': 'ok',
        'service': 'flappy-bird',
        'timestamp': int(time.time()),
        'version': '1.0.0'
    }
    
    # Quick database connectivity test (optimized for speed)
    try:
        db = get_database()
        # Minimal database test - just check if file exists and is accessible
        if os.path.exists(db.db_path) and os.access(db.db_path, os.R_OK):
            health_status['database'] = 'connected'
        else:
            health_status['database'] = 'initializing'
            # Initialize database if needed
            db.init_database()
            health_status['database'] = 'connected'
    except Exception as e:
        health_status['database'] = 'error'
        health_status['error'] = str(e)[:100]  # Truncate error message
        health_status['status'] = 'degraded'
    
    # Deployment platform detection
    if os.getenv('REPLIT_DEPLOYMENT'):
        health_status['platform'] = 'production'
    else:
        health_status['platform'] = 'development'
    
    response = jsonify(health_status)
    response.headers.update({
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Content-Type': 'application/json'
    })
    return response, 200

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    # Validation
    if not all([email, username, password, confirm_password]):
        return jsonify({'success': False, 'message': 'Please fill in all fields'})
    
    if not is_valid_email(email):
        return jsonify({'success': False, 'message': 'Please enter a valid email address'})
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'})
    
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match'})
    
    # Create user (automatically verified)
    try:
        user_id, _ = get_database().create_user(email, username, password)
        if user_id:
            # Automatically verify the user
            get_database().verify_user_by_id(user_id)
            return jsonify({'success': True, 'message': 'Account created successfully! You can now sign in.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to create account'})
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Email or username already exists'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Please fill in all fields'})
    
    if not is_valid_email(email):
        return jsonify({'success': False, 'message': 'Please enter a valid email address'})
    
    user = get_database().authenticate_user(email, password)
    if user:
        session['user'] = user
        return jsonify({'success': True, 'message': 'Login successful!', 'user': user})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'})

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'success': False, 'message': 'Please enter your email address'})
    
    if not is_valid_email(email):
        return jsonify({'success': False, 'message': 'Please enter a valid email address'})
    
    reset_token = get_database().request_password_reset(email)
    if reset_token:
        try:
            email_sent = get_email_service().send_password_reset_email(email, reset_token)
            if email_sent:
                return jsonify({'success': True, 'message': 'Password reset email sent!'})
            else:
                return jsonify({'success': False, 'message': 'Failed to send reset email. Please check server logs for details.'})
        except Exception as e:
            print(f"Password reset email error: {str(e)}")
            return jsonify({'success': False, 'message': f'Email service error: {str(e)}'})
    else:
        return jsonify({'success': False, 'message': 'Email not found or not verified'})

@app.route('/api/guest-login', methods=['POST'])
def guest_login():
    session['guest'] = True
    return jsonify({'success': True, 'message': 'Playing as guest'})

@app.route('/api/save-score', methods=['POST'])
def save_score():
    data = request.get_json() or {}
    score = data.get('score', 0)
    play_time = data.get('play_time', 0)
    
    if 'user' not in session:
        return jsonify({'success': True, 'message': 'Score not saved for guest'})
    
    user_id = session['user']['id']
    username = session['user']['username']
    
    print(f"[COIN DEBUG] User {username} (ID: {user_id}) scored {score} points")
    
    # Get current coins directly from database (source of truth)
    current_coins = get_database().get_user_coins(user_id)
    print(f"[COIN DEBUG] Current coins from database: {current_coins}")
    
    # Calculate new coin total
    new_coins = current_coins + score
    print(f"[COIN DEBUG] Adding {score} coins: {current_coins} + {score} = {new_coins}")
    
    # Save score and update coins in database
    get_database().save_game_score(user_id, score, play_time)
    get_database().update_user_coins(user_id, new_coins)
    
    # Update session with fresh data
    session['user']['coins'] = new_coins
    
    print(f"[COIN DEBUG] Successfully updated coins to {new_coins}")
    return jsonify({'success': True, 'coins': new_coins})

@app.route('/api/leaderboard')
def leaderboard():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Login required'})
    
    leaders = get_database().get_leaderboard()
    user_rank = get_database().get_user_rank(session['user']['id'])
    
    return jsonify({
        'success': True, 
        'leaderboard': leaders,
        'user_rank': user_rank
    })

@app.route('/api/history')
def history():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Login required'})
    
    user_history_raw = get_database().get_user_history(session['user']['id'])
    
    # Convert tuples to objects for frontend
    user_history = []
    for row in user_history_raw:
        user_history.append({
            'score': row[0],
            'play_time': row[1],
            'played_at': row[2]
        })
    
    return jsonify({'success': True, 'history': user_history})



@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/get-unlocks')
def get_unlocks():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    try:
        unlocked_characters = get_database().get_user_unlocks(session['user']['id'])
        return jsonify({'success': True, 'unlocked_characters': unlocked_characters})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to get unlocks'})

@app.route('/api/unlock-character', methods=['POST'])
def unlock_character():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json() or {}
    character_id = data.get('character_id')
    cost = data.get('cost', 0)
    
    if character_id is None:
        return jsonify({'success': False, 'message': 'Character ID required'})
    
    # Get current coins from database (source of truth)
    current_coins = get_database().get_user_coins(session['user']['id'])
    
    print(f"[UNLOCK DEBUG] User {session['user']['username']} trying to unlock character {character_id}")
    print(f"[UNLOCK DEBUG] Cost: {cost}, Current coins: {current_coins}")
    
    # Check if user has enough coins
    if current_coins < cost:
        print(f"[UNLOCK DEBUG] Not enough coins: {current_coins} < {cost}")
        return jsonify({'success': False, 'message': 'Not enough coins'})
    
    print(f"[UNLOCK DEBUG] Sufficient coins, proceeding with unlock")
    
    try:
        # Deduct coins
        new_coins = current_coins - cost
        get_database().update_user_coins(session['user']['id'], new_coins)
        session['user']['coins'] = new_coins  # Update session
        
        # Unlock character
        get_database().unlock_character(session['user']['id'], character_id)
        
        return jsonify({'success': True, 'coins': new_coins})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to unlock character'})

@app.route('/api/get-coins')
def get_coins():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    try:
        current_coins = get_database().get_user_coins(session['user']['id'])
        session['user']['coins'] = current_coins  # Sync session
        return jsonify({'success': True, 'coins': current_coins})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to get coins'})

@app.route('/api/update-coins', methods=['POST'])
def update_coins():
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json() or {}
    coins = data.get('coins', 0)
    
    try:
        get_database().update_user_coins(session['user']['id'], coins)
        session['user']['coins'] = coins  # Update session too
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to update coins'})

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    debug_mode = not bool(os.getenv('REPLIT_DEPLOYMENT'))
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
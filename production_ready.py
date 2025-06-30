#!/usr/bin/env python3
"""
Production-ready entry point for Jumpy Bird web application
Comprehensive error handling and optimization for deployment platforms
"""
import os
import sys
import logging
import signal
import time

# Force production environment settings
os.environ['REPLIT_DEPLOYMENT'] = '1'
os.environ['HOST'] = '0.0.0.0'
os.environ['PYTHONUNBUFFERED'] = '1'

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

def validate_environment():
    """Validate critical environment variables and configuration"""
    issues = []
    
    # Check for essential environment variables
    port = int(os.getenv('PORT', 5000))
    if port < 1 or port > 65535:
        issues.append(f"Invalid port: {port}")
    
    # Validate host configuration
    host = os.getenv('HOST', '0.0.0.0')
    if host not in ['0.0.0.0', '127.0.0.1', 'localhost']:
        issues.append(f"Potentially problematic host: {host}")
    
    return issues, port

def main():
    """Production entry point with comprehensive error handling"""
    start_time = time.time()
    logger.info("=== Production Deployment Starting ===")
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize port variable
    port = 5000
    
    try:
        # Environment validation
        issues, port = validate_environment()
        if issues:
            logger.warning(f"Environment validation issues: {', '.join(issues)}")
        
        logger.info(f"Configuration validated - Port: {port}")
        
        # Import Flask application with detailed error handling
        logger.info("Importing Flask application...")
        try:
            from web_app import app
            logger.info("Flask application imported successfully")
        except ImportError as e:
            logger.error(f"Critical error: Cannot import Flask app - {e}")
            logger.error("Ensure all dependencies are installed and paths are correct")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error during Flask import: {e}")
            sys.exit(1)
        
        # Configure Flask for production deployment
        app.config.update({
            'ENV': 'production',
            'DEBUG': False,
            'TESTING': False,
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': False,
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax'
        })
        
        # Ensure SECRET_KEY is set for production
        if not app.secret_key:
            import secrets
            app.secret_key = secrets.token_hex(32)
            logger.info("Generated new secret key for session management")
        
        startup_time = time.time() - start_time
        logger.info(f"Application ready in {startup_time:.2f}s")
        logger.info(f"Starting Flask server on 0.0.0.0:{port}")
        logger.info("Health check available at /health")
        
        # Start Flask application
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        sys.exit(0)
    except OSError as e:
        current_port = int(os.getenv('PORT', 5000))
        if "Address already in use" in str(e):
            logger.error(f"Port {current_port} is already in use")
            logger.error("Try setting a different PORT environment variable")
        else:
            logger.error(f"Network error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Critical deployment error: {e}")
        logger.error("Full traceback:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
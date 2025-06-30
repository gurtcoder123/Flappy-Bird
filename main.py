#!/usr/bin/env python3
"""
Main entry point for deployment - works for both Replit and Cloud Run
Simplified and reliable configuration for all containerized environments
"""
import os
import logging
import sys

# Set production mode
os.environ['REPLIT_DEPLOYMENT'] = '1'
os.environ['HOST'] = '0.0.0.0'

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Universal deployment entry point"""
    try:
        # Get port from environment
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"Starting Jumpy Bird Flask application")
        logger.info(f"Host: {host}, Port: {port}")
        logger.info(f"Environment: Production")
        
        # Import Flask app
        from web_app import app
        
        # Configure Flask for production
        app.config.update({
            'ENV': 'production',
            'DEBUG': False,
            'TESTING': False,
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': False
        })
        
        logger.info("Flask application configured for production")
        logger.info(f"Starting server on {host}:{port}")
        
        # Start the application
        app.run(
            host=host,
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start Flask application: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
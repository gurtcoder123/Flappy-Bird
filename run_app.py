#!/usr/bin/env python3
"""
Dedicated Flask application runner for Replit deployment
Ensures proper binding to 0.0.0.0 and correct port configuration
"""
import os
import logging
import sys

# Set environment variables for production
os.environ['HOST'] = '0.0.0.0'
os.environ['REPLIT_DEPLOYMENT'] = '1'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point optimized for Replit deployment"""
    try:
        # Get port configuration
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        
        # Import Flask application
        from web_app import app
        
        logger.info(f"Starting Jumpy Bird Flask application")
        logger.info(f"Host: {host}, Port: {port}")
        logger.info(f"Environment: {'Production' if os.getenv('REPLIT_DEPLOYMENT') else 'Development'}")
        
        # Configure Flask for production
        app.config.update({
            'ENV': 'production',
            'DEBUG': False,
            'TESTING': False,
            'JSON_SORT_KEYS': False,
            'JSONIFY_PRETTYPRINT_REGULAR': False
        })
        
        # Start the Flask application
        app.run(
            host=host,
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start Flask application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""
import os
import sys
import logging

# Set production environment early
os.environ['REPLIT_DEPLOYMENT'] = '1'

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    from web_app import app
    
    # WSGI application entry point
    application = app
    
    # Configure for production
    app.config['ENV'] = 'production'
    app.config['DEBUG'] = False
    
    logging.info("WSGI application initialized successfully")
    
except Exception as e:
    logging.error(f"Failed to initialize WSGI application: {e}")
    sys.exit(1)

if __name__ == "__main__":
    # Direct run mode for testing
    try:
        port = int(os.getenv('PORT', 5000))
        logging.info(f"Starting application on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        sys.exit(1)
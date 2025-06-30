# Jumpy Bird Game - Replit Project Guide

## Overview

This is a comprehensive Jumpy Bird game implementation built with both Python/Pygame and Flask web versions, featuring a complete user authentication system, game progression mechanics, and 8-bit retro styling. The game includes user registration, login functionality, Google OAuth support, score tracking, and persistent data storage using SQLite.

## System Architecture

### Frontend Architecture
- **Game Engine**: Dual implementation - Pygame-based 2D desktop game and HTML5/JavaScript web game
- **State Management**: Centralized state manager handling different game screens (auth, menu, gameplay, settings)
- **Rendering System**: Custom 8-bit style graphics rendered programmatically (Pygame) and CSS/Canvas (Web)
- **Input Handling**: Event-driven input system for keyboard and mouse interactions
- **Web Interface**: Responsive HTML5 game with CSS animations and JavaScript game loop

### Backend Architecture
- **Database Layer**: SQLite database with custom ORM-like wrapper
- **Authentication System**: Complete auth flow with email verification and password reset
- **Game Logic**: Object-oriented game mechanics with physics simulation
- **Sound System**: Programmatically generated 8-bit sound effects

### Data Storage Solutions
- **SQLite Database**: Local file-based database (`flappy_bird.db`)
- **Tables**: 
  - `users` - User accounts with authentication data
  - `game_history` - Game session records and scores
  - `user_unlocks` - Character/item unlock tracking

### Authentication and Authorization
- **Email-based Registration**: Users register with email/username/password
- **Google OAuth Integration**: Sign in with Google account support (requires API configuration)
- **Password Hashing**: Secure password storage using hashlib
- **Email Verification**: Token-based email verification system
- **Password Reset**: Secure password reset via email tokens
- **Guest Mode**: Optional guest play without registration

## Key Components

### Core Game Classes
- **Bird**: Main player character with physics and animation
- **Obstacle**: Procedurally generated obstacles (pillars)
- **Background**: Scrolling background with 8-bit city skyline
- **GameStateManager**: Central controller for all game states

### Authentication System
- **AuthSystem**: Handles login, signup, and password recovery flows
- **EmailService**: SMTP-based email delivery for verification/reset
- **Database**: User management and data persistence

### Audio System
- **SoundManager**: Generates 8-bit style sound effects programmatically
- **Effects**: Jump, score, and game over sounds using square wave synthesis

### Game Progression
- **Scoring System**: Points awarded for passing obstacles
- **Difficulty Scaling**: Increasing obstacle frequency over time
- **Persistent History**: All game sessions saved to database

## Data Flow

1. **Application Startup**: Initialize Pygame, database, and sound systems
2. **Authentication Flow**: User login/signup → email verification → main menu
3. **Game Loop**: Menu selection → game initialization → gameplay → score recording
4. **State Transitions**: Centralized state management with event-driven transitions
5. **Data Persistence**: Real-time saving of user progress and game statistics

## External Dependencies

### Python Packages
- **pygame**: Game engine and multimedia library
- **sqlite3**: Database operations (built-in)
- **smtplib**: Email sending functionality (built-in)
- **hashlib**: Password hashing (built-in)

### System Dependencies (via Nix)
- **SDL2**: Cross-platform multimedia library
- **Audio Libraries**: SDL2_mixer for sound support
- **Graphics Libraries**: SDL2_image, libpng, libjpeg for image handling
- **Font Libraries**: SDL2_ttf, fontconfig, freetype for text rendering

### Email Configuration
- **SMTP Server**: Configurable email provider (default: Gmail)
- **Environment Variables**: EMAIL_ADDRESS and EMAIL_PASSWORD for credentials

## Deployment Strategy

### Development Environment
- **Replit Integration**: Configured for one-click deployment on Replit
- **Auto-dependency Management**: Automatic pygame installation via pip
- **Nix Environment**: Declarative system dependencies

### Production Deployment
- **Health Check Endpoint**: `/health` endpoint returns JSON status for deployment monitoring
- **Debug Mode**: Automatically disabled in production via `REPLIT_DEPLOYMENT` environment variable
- **Lazy Loading**: Database and email services initialize only when needed to improve startup time
- **WSGI Configuration**: Proper WSGI entry point with production settings
- **Port Configuration**: Listens on port 5000 with `0.0.0.0` binding for accessibility

### Database Initialization
- **Auto-creation**: Database and tables created automatically on first run
- **Migration-ready**: Schema designed for future expansions

### Configuration Management
- **Environment-based**: Email credentials via environment variables
- **Settings Module**: Centralized configuration for game parameters

## Changelog

- June 26, 2025: Initial setup
- June 26, 2025: Fixed obstacle generation issues - proper spacing, ground collision prevention, and consistent spawning patterns
- June 26, 2025: Added Google OAuth integration framework and web-based game implementation
- June 26, 2025: Created dual architecture with Pygame desktop version and Flask web version for better compatibility
- June 26, 2025: Added character selection system with 4 unlockable birds (0, 50, 100, 200 coins)
- June 26, 2025: Enhanced UI with pause functionality, improved coin display, and velocity-based bird rotation
- June 26, 2025: Redesigned birds with square-based pixelated patterns and directional movement indicators
- June 27, 2025: Implemented stationary start behavior - bird, timer, and obstacles remain inactive until first spacebar press
- June 27, 2025: Enhanced all birds with prominent triangular beaks and square-based wings with unique colors per character
- June 27, 2025: Added sign out functionality for both guest and signed-in users with compact button positioning
- June 27, 2025: Fixed deployment issues - added proper health check endpoint, disabled debug mode for production, implemented lazy loading for database connections, and updated WSGI configuration for production deployment
- June 27, 2025: Removed test member login functionality for cleaner authentication experience
- June 27, 2025: Applied comprehensive deployment fixes - updated secret key configuration for production, optimized health check endpoint for faster response, enhanced WSGI entry point with logging and error handling, added production optimizations for JSON responses, created multiple entry point alternatives (app.py, run.py) and gunicorn configuration for robust deployment options  
- June 27, 2025: Fixed deployment configuration issues - created multiple production-ready entry points (main_web.py, start.py, deploy.py), configured proper SECRET_KEY environment variable usage with fallback to SESSION_SECRET, ensured 0.0.0.0 binding for Cloud Run compatibility, added comprehensive error handling and logging for deployment debugging
- June 27, 2025: Applied comprehensive Cloud Run deployment fixes - created main.py, app.py, and server.py as specific entry points for containerized deployment, ensured all entry points bind to 0.0.0.0 for Cloud Run compatibility, optimized health check endpoint with proper JSON response, added Dockerfile with pygame system dependencies, configured production environment variables and logging for containerized environments
- June 27, 2025: Fixed critical deployment issues - created deploy_cloudrun.py as optimized Cloud Run entry point with comprehensive error handling and logging, updated Dockerfile to use specific entry point instead of $file variable, enhanced health check endpoint with database connectivity testing and proper JSON responses, ensured proper 0.0.0.0 binding for Cloud Run compatibility, added environment validation and graceful shutdown handling
- June 27, 2025: Applied comprehensive deployment fixes - simplified main.py entry point for reliable Cloud Run deployment, updated Dockerfile CMD to use "python main.py" instead of $file variable, consolidated system dependencies installation including curl for health checks, fixed workflow configuration to eliminate port conflicts, added .dockerignore for optimized container builds, verified health check endpoint returns proper JSON responses with database connectivity status
- June 27, 2025: Fixed Flask deployment issues - created run_app.py as dedicated Flask runner replacing $file variable usage, optimized health check endpoint for faster response (30ms), ensured HOST environment variable set to 0.0.0.0 for proper binding, updated workflow configuration to use specific Python file instead of generic $file variable, added multiple production-ready entry points (flask_app.py, startup.py, deploy_app.py) for different deployment scenarios
- June 28, 2025: Applied comprehensive deployment fixes - eliminated $file variable dependency by using run_app.py as explicit entry point, enhanced health check endpoint with database connectivity testing and detailed JSON responses including timestamp and service status, ensured proper Flask application binding to 0.0.0.0:5000 for all deployment platforms, created production_app.py as additional production-ready entry point with comprehensive error handling and logging
- June 28, 2025: Resolved all deployment issues - optimized health check endpoint for sub-50ms response time with platform detection and version information, created production_ready.py with comprehensive error handling and graceful shutdown, fixed LSP errors and ensured proper variable scoping, verified all entry points work correctly with proper 0.0.0.0:5000 binding for universal deployment compatibility
- June 30, 2025: Fixed bird movement issues by simplifying game loop physics, removing complex delta time calculations that were causing the bird to not move or respond to controls, restored basic gravity and jump mechanics for reliable gameplay
- June 30, 2025: Fixed critical coin system bugs - corrected save_score function to properly add coins to existing balance instead of overwriting, fixed update_coins endpoint session key reference, ensured coins persist correctly across multiple games and login sessions, eliminated random coin additions that were confusing users
- June 30, 2025: Completely rebuilt coin system architecture - implemented database as single source of truth for all coin calculations, added get_user_coins method to fetch fresh balance before each transaction, eliminated frontend/session coin sync issues, added comprehensive debugging logging, ensured character unlocks persist in database with user_unlocks table
- June 30, 2025: Enhanced character selection UI - removed cost text display for unlocked characters (including "Free" text for basic bird), improved visual clarity by hiding price labels once characters are owned, maintained clean character card appearance for purchased items

## User Preferences

Preferred communication style: Simple, everyday language.
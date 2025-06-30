# Render Deployment Guide

## Quick Deploy to Render

### 1. Upload Files
- Extract this zip file
- Upload all files to your GitHub repository

### 2. Connect to Render
- Go to [render.com](https://render.com)
- Connect your GitHub repository
- Choose "Web Service"

### 3. Configure Service
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python run_app.py`
- **Environment**: Python 3.11

### 4. Set Environment Variables
Required variables:
```
REPLIT_DEPLOYMENT=1
SECRET_KEY=your-secret-key-here
```

Optional for PostgreSQL:
```
DATABASE_URL=postgresql://user:password@host:5432/database
```

### 5. Add Database (Optional)
- In Render dashboard, add PostgreSQL database
- Copy DATABASE_URL to environment variables
- Database tables will be created automatically

### 6. Deploy
- Click "Create Web Service"
- Render will build and deploy automatically
- Your app will be available at https://your-app-name.onrender.com

## Troubleshooting

### Build Fails
- Check that all files are uploaded correctly
- Verify requirements.txt is present
- Check build logs for missing dependencies

### App Won't Start
- Verify start command: `python run_app.py`
- Check environment variables are set
- Review application logs

### Database Issues
- Ensure DATABASE_URL is correctly set
- Check PostgreSQL connection string format
- Verify database is accessible from Render

## Features Included
- ✅ User authentication and registration
- ✅ Game score tracking and leaderboards
- ✅ Character unlocks and coin system
- ✅ Email verification (configure SMTP)
- ✅ PostgreSQL production database support
- ✅ SQLite fallback for development

## Support
Check the logs in Render dashboard for any issues.
The app includes comprehensive error handling and logging.

# External Deployment Guide - Database Setup

## Database Options for External Deployment

### 1. **PostgreSQL (Recommended for Production)**

PostgreSQL is the best choice for external deployment because it's:
- More reliable and scalable than SQLite
- Supported by all major cloud platforms
- Handles concurrent users better
- Provides better data integrity

#### Cloud PostgreSQL Providers:

**Free Tiers Available:**
- **Neon** (PostgreSQL) - 0.5GB free
- **Supabase** - 500MB free + auth features
- **Railway** - $5/month PostgreSQL
- **Heroku Postgres** - 10k rows free

**Paid Options:**
- **AWS RDS** - Starting ~$15/month
- **Google Cloud SQL** - Starting ~$10/month
- **DigitalOcean Managed DB** - Starting ~$15/month

### 2. **SQLite (Development Only)**

SQLite works for development but has limitations:
- Single file database (good for prototyping)
- No concurrent writes (problems with multiple users)
- Not suitable for production deployment

## Setup Instructions

### Option A: PostgreSQL Setup (Recommended)

1. **Get PostgreSQL Database:**
   ```bash
   # Choose one provider and get DATABASE_URL
   # Example: postgresql://user:password@host:port/database
   ```

2. **Set Environment Variable:**
   ```bash
   export DATABASE_URL="postgresql://user:password@host:5432/flappy_bird"
   ```

3. **Install PostgreSQL Driver:**
   ```bash
   pip install psycopg2-binary
   ```

4. **Run Migration:**
   ```bash
   python database_migration.py
   ```

### Option B: Quick SQLite Setup (Development)

1. **No additional setup needed** - SQLite file created automatically
2. **Run Migration:**
   ```bash
   python database_migration.py
   ```

## Database Schema

Your database will store:

### Users Table
- User accounts (email, username, password)
- Verification status
- Coin balance
- Selected character
- Password reset tokens

### Game History Table
- All game sessions
- Scores and play time
- Character used
- Timestamps for analytics

### User Unlocks Table
- Character unlocks
- Achievement tracking
- Purchase history

## Deployment Platform Examples

### Heroku
```bash
# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Get DATABASE_URL (automatically set)
heroku config:get DATABASE_URL

# Deploy with migration
git push heroku main
heroku run python database_migration.py
```

### Railway
```bash
# Add PostgreSQL service in Railway dashboard
# Set DATABASE_URL in environment variables
# Deploy normally - migration runs automatically
```

### Vercel/Netlify (Serverless)
```bash
# Use Neon or Supabase for PostgreSQL
# Set DATABASE_URL in environment variables
# Functions will connect automatically
```

### DigitalOcean App Platform
```yaml
# In .do/app.yaml
databases:
- name: flappy-bird-db
  engine: PG
  version: "14"

envs:
- key: DATABASE_URL
  scope: RUN_AND_BUILD_TIME
  type: SECRET
```

## Migration and Maintenance

### Automatic Migration
The app automatically detects and sets up the correct database:
- PostgreSQL for production (when DATABASE_URL is set)
- SQLite for development

### Manual Migration
```bash
# Run migration script
python database_migration.py

# Check database status
python -c "from production_database import ProductionDatabase; db = ProductionDatabase(); print('Database connected successfully')"
```

### Backup Strategies

**PostgreSQL:**
```bash
# Backup
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

**SQLite:**
```bash
# Backup
cp flappy_bird.db backup_flappy_bird.db

# Restore
cp backup_flappy_bird.db flappy_bird.db
```

## Environment Variables for Production

```bash
# Required
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=your-secret-key-here

# Optional
PORT=5000
REPLIT_DEPLOYMENT=1
```

## Security Considerations

1. **Never commit DATABASE_URL** - Use environment variables
2. **Use strong passwords** - Database credentials should be complex
3. **Enable SSL** - Production databases should use SSL connections
4. **Regular backups** - Set up automated backups
5. **Monitor access** - Watch for unusual database activity

## Cost Estimates

**Free Tier Options:**
- Neon PostgreSQL: Free (0.5GB)
- Supabase: Free (500MB)
- SQLite: Free (file-based)

**Production Options:**
- Railway PostgreSQL: $5/month
- Heroku Postgres: $9/month (hobby tier)
- AWS RDS: $15-30/month
- Google Cloud SQL: $10-25/month

## Troubleshooting

### Connection Issues
```bash
# Test PostgreSQL connection
python -c "import psycopg2; psycopg2.connect('$DATABASE_URL'); print('Connected!')"

# Test SQLite connection
python -c "import sqlite3; sqlite3.connect('flappy_bird.db'); print('Connected!')"
```

### Common Errors
- **"psycopg2 not found"** → Install: `pip install psycopg2-binary`
- **"Connection refused"** → Check DATABASE_URL and network access
- **"Table doesn't exist"** → Run: `python database_migration.py`

The app is now ready for external deployment with proper database support!
# Fly.io Deployment Steps

**Date:** 2026-10-06  
**Status:** Ready for deployment  

---

## Prerequisites

### 1. Authentication
```bash
# You need to be logged in to Fly.io
flyctl auth login

# This will open your browser to authenticate
# Follow the prompts and return to terminal

# Verify you're authenticated
flyctl auth whoami
# Should show your email/username
```

### 2. Check Current Setup
```bash
# List your Fly.io apps
flyctl apps list

# Should show existing apps (if any)
```

---

## Step 1: Create/Check Fly.io App (if needed)

```bash
# If app doesn't exist, create it
flyctl app create sg-property-bot --region sin

# Or if app exists, check its status
flyctl apps info sg-property-bot
```

---

## Step 2: Attach/Create PostgreSQL Database

### Option A: If PostgreSQL cluster already exists
```bash
# List existing PostgreSQL clusters
flyctl postgres list

# Attach to your app
flyctl postgres attach pg-cluster-name --app sg-property-bot
```

### Option B: Create new PostgreSQL cluster
```bash
# Create new PostgreSQL cluster
flyctl postgres create --app sg-property-bot --region sin

# This will prompt for:
# - Cluster name (suggested: sg-property-bot-db)
# - Postgres version (latest recommended)
# - VM size (shared-cpu-1x)

# Wait for cluster to be ready (2-3 minutes)

# Verify
flyctl postgres list
```

---

## Step 3: Get Database Credentials

```bash
# Get connection string
flyctl postgres connect --app sg-property-bot-db

# Or get individual credentials
flyctl postgres info --app sg-property-bot-db
```

Expected output will include:
- DB_HOST (e.g., sg-property-bot-db.internal)
- DB_PORT (usually 5432)
- DB_NAME (e.g., postgres)
- DB_USER (e.g., postgres)
- DB_PASSWORD (will be shown)

---

## Step 4: Create Database & User (if needed)

```bash
# Connect to PostgreSQL
flyctl postgres connect --app sg-property-bot-db

# At psql prompt:
# Create database
CREATE DATABASE propertybot;

# Create dedicated user (optional, for security)
CREATE USER propertybot_user WITH PASSWORD 'strong_password_here';

# Grant permissions
GRANT ALL PRIVILEGES ON DATABASE propertybot TO propertybot_user;

# Exit
\q
```

---

## Step 5: Deploy Database Schema

### Option A: Using Fly App Deployment
The schema will auto-initialize when you run orchestrator_v3.py for the first time.

### Option B: Manual Schema Initialization

```bash
# Connect to Fly PostgreSQL
flyctl postgres connect --app sg-property-bot-db

# Create database if not already created
CREATE DATABASE propertybot;

# Exit and run orchestrator to initialize schema
\q

# Then in your app:
python -c "
from database_persistence import PropertyDatabase

db = PropertyDatabase()
if db.connect():
    db.init_schema()
    print('✓ Schema initialized')
    db.close()
"
```

---

## Step 6: Set Fly.io Secrets

```bash
# Get database connection details
flyctl postgres info --app sg-property-bot-db

# Set secrets (copy values from output above)
flyctl secrets set \
  DB_HOST=sg-property-bot-db.internal \
  DB_PORT=5432 \
  DB_NAME=propertybot \
  DB_USER=postgres \
  DB_PASSWORD='your_password_here' \
  TELEGRAM_BOT_TOKEN='your_token' \
  TELEGRAM_CHAT_ID='your_chat_id' \
  --app sg-property-bot
```

Or set one at a time:
```bash
flyctl secrets set DB_HOST=sg-property-bot-db.internal --app sg-property-bot
flyctl secrets set DB_PORT=5432 --app sg-property-bot
# ... etc
```

### Verify secrets are set
```bash
flyctl secrets list --app sg-property-bot
```

---

## Step 7: Deploy App to Fly.io

```bash
# Deploy the app
flyctl deploy --app sg-property-bot

# This will:
# 1. Build Docker image
# 2. Push to Fly.io registry
# 3. Deploy to your region
# 4. Start the app

# Wait for deployment to complete
```

### Verify deployment
```bash
# Check app status
flyctl status --app sg-property-bot

# Check logs
flyctl logs --app sg-property-bot

# Should see "✅ Pipeline completed"
```

---

## Step 8: Create Scheduled Job for Daily Execution

```bash
# Create machine that runs daily at 06:00 AM SGT
flyctl machines create \
  --app sg-property-bot \
  --name orchestrator-daily \
  --region sin \
  --schedule cron="0 22 * * *" \
  --env DB_HOST=sg-property-bot-db.internal \
  --env DB_PORT=5432 \
  --env DB_NAME=propertybot \
  --env DB_USER=postgres \
  --secret DB_PASSWORD \
  --secret TELEGRAM_BOT_TOKEN \
  --secret TELEGRAM_CHAT_ID \
  python orchestrator_v3.py
```

Or use Fly.io UI to create a scheduled machine.

---

## Step 9: Test Database Connection

```bash
# SSH into Fly.io machine
flyctl ssh console --app sg-property-bot

# Inside Fly machine, test database:
python -c "
from database_persistence import PropertyDatabase

db = PropertyDatabase()
if db.connect():
    count = db.execute_query('SELECT COUNT(*) FROM listings')
    print(f'✓ Database connected. Properties: {count[0][0]}')
    db.close()
else:
    print('✗ Database connection failed')
"

# Exit
exit
```

---

## Step 10: Test Full Orchestrator

```bash
# Run orchestrator on Fly app
flyctl ssh console --app sg-property-bot

# Inside Fly machine:
python orchestrator_v3.py

# Should see:
# 📊 Starting Enhanced Property Pipeline with Database Persistence...
# 1. Generating property dataset...
# 2. Running comprehensive analysis...
# 3. Persisting to database...
# 4. Saving results locally...
# 5. Sending Telegram report...
# ✅ Pipeline completed

# Exit
exit
```

---

## Step 11: Verify Daily Execution

```bash
# Check Fly machines
flyctl machines list --app sg-property-bot

# Should show orchestrator machine with schedule

# Check machine logs (after scheduled time)
flyctl machines log MACHINE_ID --app sg-property-bot

# Or check app logs for last 24 hours
flyctl logs --app sg-property-bot --since 24h
```

---

## Monitoring

### View Real-time Logs
```bash
flyctl logs --app sg-property-bot --follow
```

### Check Database Size
```bash
flyctl postgres connect --app sg-property-bot-db

# At psql prompt:
SELECT pg_size_pretty(pg_database_size(current_database()));
\q
```

### Query Stored Properties
```bash
flyctl postgres connect --app sg-property-bot-db

# At psql prompt:
SELECT COUNT(*) FROM listings;
SELECT DATE(scraped_date) as date, COUNT(*) FROM listings GROUP BY DATE(scraped_date);
\q
```

---

## Troubleshooting

### Database Connection Failed
```bash
# Verify secrets are set correctly
flyctl secrets list --app sg-property-bot

# Test connection inside Fly machine
flyctl ssh console --app sg-property-bot
python -c "import psycopg2; print('✓ psycopg2 installed')"
exit
```

### PostgreSQL Cluster Not Ready
```bash
# Check cluster status
flyctl postgres status --app sg-property-bot-db

# Wait for "Available" status
```

### Scheduled Job Not Running
```bash
# Check machine schedule
flyctl machines list --app sg-property-bot

# View machine details
flyctl machines show MACHINE_ID --app sg-property-bot

# Check logs
flyctl machines log MACHINE_ID --app sg-property-bot --since 24h
```

### App Deployment Failed
```bash
# Check deployment logs
flyctl deploy --app sg-property-bot

# Or view recent logs
flyctl logs --app sg-property-bot --since 1h
```

---

## Rollback

If something goes wrong:

```bash
# View deployment history
flyctl releases --app sg-property-bot

# Rollback to previous version
flyctl releases rollback --app sg-property-bot

# Or specify exact version
flyctl releases rollback VERSION_NUMBER --app sg-property-bot
```

---

## Environment Variables

**For Fly.io Deployment**, set these secrets:

```
DB_HOST=sg-property-bot-db.internal
DB_PORT=5432
DB_NAME=propertybot
DB_USER=postgres
DB_PASSWORD=<from PostgreSQL setup>
TELEGRAM_BOT_TOKEN=<your token>
TELEGRAM_CHAT_ID=<your chat id>
```

---

## Cost Estimation

**Monthly costs on Fly.io:**
- App machine (shared-cpu-1x): ~$5/month
- PostgreSQL cluster (shared-cpu-1x): ~$15/month
- Data transfer: ~$0.02/GB (minimal)
- **Total: ~$20-25/month**

---

## Success Checklist

- [ ] Fly.io account created and logged in
- [ ] sg-property-bot app created
- [ ] PostgreSQL cluster created and attached
- [ ] Database credentials captured
- [ ] Fly.io secrets configured
- [ ] App deployed successfully
- [ ] Database schema initialized
- [ ] Test execution successful
- [ ] Properties persisted to database
- [ ] Telegram report received
- [ ] Scheduled job configured
- [ ] Daily execution verified

---

## Quick Reference Commands

```bash
# Login
flyctl auth login

# List apps
flyctl apps list

# Deploy app
flyctl deploy --app sg-property-bot

# Set secrets
flyctl secrets set KEY=VALUE --app sg-property-bot

# View logs
flyctl logs --app sg-property-bot

# Connect to database
flyctl postgres connect --app sg-property-bot-db

# SSH into machine
flyctl ssh console --app sg-property-bot

# Create scheduled machine
flyctl machines create --app sg-property-bot --schedule cron="0 22 * * *" python orchestrator_v3.py

# Check status
flyctl status --app sg-property-bot
```

---

**Next Steps:** Follow the steps above in order. Start with authentication, then create/attach database, then deploy app, then configure scheduling.


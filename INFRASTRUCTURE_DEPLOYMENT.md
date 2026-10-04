# Phase 1 Infrastructure Deployment Guide

**Status**: Ready for Deployment  
**Target**: Production-grade on Fly.io  
**Timeline**: ~1-2 hours  
**Credentials**: Will be injected later  

---

## Prerequisites Checklist

Before starting deployment, ensure you have:

- [ ] Fly.io account created (https://fly.io)
- [ ] `flyctl` CLI installed on your machine
- [ ] Authenticated with Fly.io: `flyctl auth login`
- [ ] This repository cloned locally
- [ ] Docker installed (optional, for local testing)
- [ ] Terminal/PowerShell ready

### Install Fly.io CLI

**macOS:**
```bash
brew install flyctl
```

**Windows (PowerShell):**
```powershell
scoop install flyctl
# OR download from https://fly.io/docs/getting-started/installing-flyctl/
```

**Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Verify Installation:**
```bash
flyctl version
flyctl auth login
```

---

## Deployment Steps

### Step 1: Navigate to Project Directory

```bash
cd C:\Users\ash_f\Desktop\python\sg-property-bot
```

### Step 2: Run Deployment Script

**Windows (PowerShell):**
```powershell
.\scripts\deploy.ps1 -AppName "sg-property-bot" -Region "sin"
```

**macOS/Linux (Bash):**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

The script will:
1. ✅ Verify Fly.io authentication
2. ✅ Create Fly.io application
3. ✅ Deploy PostgreSQL database (2GB RAM, Singapore region)
4. ✅ Deploy Redis cache (256MB RAM, Singapore region)
5. ✅ Set placeholder secrets
6. ✅ Build and deploy API
7. ✅ Verify deployment status
8. ✅ Output connection strings

### Step 3: Retrieve Connection Strings

After deployment completes, you'll get connection strings for:

```
DATABASE_URL=postgresql://username:password@sg-property-db.internal:5432/sg_property_bot
REDIS_URL=redis://sg-property-cache.internal:6379
API_URL=https://sg-property-bot.fly.dev
```

### Step 4: Create Production .env File

1. Copy `.env.production` to `.env`
   ```bash
   cp .env.production .env
   ```

2. Update with connection strings from Step 3
   ```bash
   # Edit .env with your editor
   vim .env  # or use VS Code
   ```

3. **Keep placeholder values for credentials**
   - Will be injected once you provide them
   - Don't leave empty, keep `YOUR_*_HERE` placeholders

### Step 5: Deploy Database Schema

Initialize the database with the schema:

```bash
# Deploy schema to production PostgreSQL
flyctl postgres exec sg-property-db < database/schema.sql

# Or manually:
psql $DATABASE_URL < database/schema.sql
```

Verify schema was created:
```bash
psql $DATABASE_URL -c "SELECT * FROM properties LIMIT 0;"
```

### Step 6: Test API Health Check

```bash
# Test API is running
curl https://sg-property-bot.fly.dev/health

# Expected response:
# {"status":"OK","timestamp":"2026-10-04T...","uptime":123.45}
```

### Step 7: Monitor Logs

```bash
# Stream logs from production
flyctl logs --app sg-property-bot

# Or view specific lines
flyctl logs --app sg-property-bot -n 50
```

---

## Deployment Checklist

- [ ] Fly.io account created and authenticated
- [ ] `flyctl` CLI installed and verified
- [ ] Deployment script executed successfully
- [ ] PostgreSQL database created and accessible
- [ ] Redis cache created and accessible
- [ ] API deployed to Fly.io
- [ ] Database schema migrated
- [ ] API health check passing
- [ ] Connection strings saved to `.env`
- [ ] Placeholder credentials configured
- [ ] Logs streaming properly

---

## Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Fly.io (Singapore)                    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  sg-property-db (PostgreSQL 15)                 │   │
│  │  • 2GB RAM, Shared CPU                          │   │
│  │  • Automatic backups                            │   │
│  │  • Internal DNS: sg-property-db.internal        │   │
│  └─────────────────┬───────────────────────────────┘   │
│                    │                                    │
│  ┌────────────────┴──────────────────────────────────┐ │
│  │  sg-property-bot (Node.js API)                   │ │
│  │  • Health check: /health                         │ │
│  │  • Automatic scaling                             │ │
│  │  • HTTPS enabled                                 │ │
│  │  • URL: https://sg-property-bot.fly.dev          │ │
│  └────────────────┬──────────────────────────────────┘ │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐   │
│  │  sg-property-cache (Redis 7)                    │   │
│  │  • 256MB RAM                                    │   │
│  │  • Persistence enabled                          │   │
│  │  • Internal DNS: sg-property-cache.internal     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
         │
         ▼
    External APIs
    (URA, 99.co, PropertyGuru, etc.)
```

---

## Connection Testing

### Test PostgreSQL Connection

```bash
# From local machine
psql postgresql://user:password@sg-property-db.internal:5432/sg_property_bot

# Or using Fly.io proxy
flyctl postgres connect -a sg-property-db

# Test query
SELECT COUNT(*) FROM properties;
SELECT version();
```

### Test Redis Connection

```bash
# Using Fly.io Redis CLI
flyctl redis connect -a sg-property-cache

# Test commands
PING
SET test_key "hello"
GET test_key
```

### Test API Connection

```bash
# Health check
curl https://sg-property-bot.fly.dev/health

# Check logs
flyctl logs --app sg-property-bot

# SSH into app (for debugging)
flyctl ssh console --app sg-property-bot
```

---

## Scaling & Performance

### Database Sizing

Current: **Shared CPU, 2GB RAM** (suitable for Phase 1)

For production upgrade:
```bash
flyctl postgres update sg-property-db --vm-size performance-1x
```

### Redis Sizing

Current: **256MB RAM** (suitable for caching)

For production upgrade:
```bash
flyctl redis update sg-property-cache --plan pro
```

### API Scaling

Auto-scaling is configured:
- Min: 1 machine
- Max: 3 machines (configurable in `fly.toml`)

Monitor scaling:
```bash
flyctl status --app sg-property-bot
```

---

## Backup & Recovery

### Automatic Backups

PostgreSQL has automatic backups (enabled by default on Fly.io):
```bash
# List backups
flyctl postgres backups list -a sg-property-db

# Restore from backup
flyctl postgres restore sg-property-db --backup-id <id>
```

### Manual Backup

```bash
# Export database to local file
pg_dump $DATABASE_URL > backup.sql

# Restore from file
psql $DATABASE_URL < backup.sql
```

---

## Troubleshooting

### Database Connection Failed

```bash
# Check database status
flyctl status -a sg-property-db

# Check logs
flyctl logs -a sg-property-db

# Restart database
flyctl restart -a sg-property-db
```

### API Not Responding

```bash
# Check app status
flyctl status -a sg-property-bot

# Check logs
flyctl logs -a sg-property-bot

# Restart app
flyctl restart -a sg-property-bot

# Deploy latest version
flyctl deploy -a sg-property-bot
```

### Redis Connection Issues

```bash
# Check Redis status
flyctl status -a sg-property-cache

# Test connection
flyctl redis connect -a sg-property-cache

# Restart Redis
flyctl restart -a sg-property-cache
```

---

## Cost Estimation

**Monthly Costs (Production):**
- PostgreSQL (shared-cpu-1x, 2GB RAM): $15
- Redis (small, 256MB): $5
- API Server (shared-cpu-2x): ~$10
- **Total: ~$30/month**

**Year 1 Total: ~$360**

---

## Next Steps (After Deployment)

1. **Provide Credentials**
   - Share Telegram bot token
   - Share Telegram chat ID
   - Share RapidAPI key (99.co)
   - Share NewsAPI key
   - Share URA access key

2. **Inject Secrets**
   ```bash
   flyctl secrets set \
     TELEGRAM_BOT_TOKEN=... \
     TELEGRAM_CHAT_ID=... \
     RAPIDAPI_KEY=... \
     NEWSAPI_KEY=... \
     URA_ACCESS_KEY=... \
     --app sg-property-bot
   ```

3. **Begin Phase 1 Implementation**
   - Implement PropertyGuru scraper
   - Implement URA API integration
   - Implement 99.co API integration
   - Build REST API endpoints
   - Test end-to-end data flow

---

## Monitoring Dashboard

View your infrastructure at: **https://fly.io/apps/sg-property-bot**

Monitor:
- CPU usage
- Memory usage
- Network I/O
- Request rates
- Error rates
- Logs in real-time

---

## Support & Documentation

- **Fly.io Docs**: https://fly.io/docs/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Redis Docs**: https://redis.io/docs/
- **Node.js Docs**: https://nodejs.org/docs/

---

**Ready to deploy!**

Once you've completed these steps, let me know and we'll proceed with credential injection and Phase 1 implementation.

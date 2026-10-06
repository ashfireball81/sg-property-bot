# Fly.io Deployment Ready - Final Guide

**Date:** 2026-10-06  
**Status:** ✅ **READY TO DEPLOY**  
**Time to Deploy:** 10-15 minutes  

---

## 🎯 Quick Start

You have **2 deployment options**:

### Option 1: Manual (Recommended for First Time)
Open your terminal and run these 10 commands in order:

```bash
# 1. Authenticate
flyctl auth login

# 2. Verify
flyctl auth whoami

# 3. Create app
flyctl app create sg-property-bot --region sin

# 4. Create database
flyctl postgres create --app sg-property-bot --region sin

# 5. Get credentials
flyctl postgres info --app sg-property-bot-db

# 6. Set secrets (copy values from step 5)
flyctl secrets set \
  DB_HOST=sg-property-bot-db.internal \
  DB_PORT=5432 \
  DB_NAME=propertybot \
  DB_USER=postgres \
  DB_PASSWORD=<your_password> \
  TELEGRAM_BOT_TOKEN=8864201770:AAGaqUPVsnitvQAlkq1xUrAeWSKdHNFE5WU \
  TELEGRAM_CHAT_ID=6834628591 \
  --app sg-property-bot

# 7. Deploy
flyctl deploy --app sg-property-bot

# 8. Verify
flyctl status --app sg-property-bot

# 9. Check logs
flyctl logs --app sg-property-bot --follow

# 10. Configure scheduled job
# See: .github/FLYIO_DEPLOYMENT_STEPS.md (Step 8)
```

### Option 2: Automated (After Authentication)

```bash
# After you've done: flyctl auth login

python deploy_to_flyio.py
```

The script will ask for database credentials and handle everything.

---

## 📋 What Gets Deployed

### Application Code
- `orchestrator_v3.py` - Enhanced pipeline with database
- `database_persistence.py` - PostgreSQL operations
- `property_analytics.py` - Analytics queries
- `send_telegram_analysis.py` - Telegram reporting

### Infrastructure
- **App:** sg-property-bot (Docker container)
- **Database:** PostgreSQL cluster (sg-property-bot-db)
- **Region:** Singapore (sin)
- **Cost:** ~$20-25/month

### Configuration
- **Runtime:** Python 3.11
- **Memory:** 256MB (shared)
- **CPU:** Shared vCPU
- **Persistent Storage:** PostgreSQL

---

## 🔑 Secrets to Configure

From your `.env` file:
- `TELEGRAM_BOT_TOKEN` ✓ Already have: 8864201770:AAGaqUPVsnitvQAlkq1xUrAeWSKdHNFE5WU
- `TELEGRAM_CHAT_ID` ✓ Already have: 6834628591

From Fly PostgreSQL:
- `DB_HOST` → `sg-property-bot-db.internal`
- `DB_PORT` → `5432`
- `DB_NAME` → `propertybot` (or whatever you name it)
- `DB_USER` → `postgres`
- `DB_PASSWORD` → *(get from PostgreSQL cluster)*

---

## 📊 Post-Deployment

### Verify Everything Works

**Check app status:**
```bash
flyctl status --app sg-property-bot
```

**View logs:**
```bash
flyctl logs --app sg-property-bot --follow
```

**Connect to database:**
```bash
flyctl postgres connect --app sg-property-bot-db
# At psql prompt:
SELECT COUNT(*) FROM listings;
```

**Test full pipeline:**
```bash
flyctl ssh console --app sg-property-bot
python orchestrator_v3.py
```

### Configure Daily Scheduled Job

**For 06:00 AM SGT execution:**

Create a scheduled machine:
```bash
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

Or follow detailed steps in: `.github/FLYIO_DEPLOYMENT_STEPS.md` (Step 8)

---

## ⚠️ Common Issues & Fixes

### Not Authenticated
```bash
flyctl auth login
flyctl auth whoami  # Should show email
```

### Database Password Incorrect
```bash
# Get correct password:
flyctl postgres info --app sg-property-bot-db

# Update secret:
flyctl secrets set DB_PASSWORD=new_password --app sg-property-bot
```

### App Won't Start
```bash
# Check logs:
flyctl logs --app sg-property-bot --since 1h

# Redeploy:
flyctl deploy --app sg-property-bot
```

### Can't Connect to Database
```bash
# Verify app has secrets:
flyctl secrets list --app sg-property-bot

# Test connection inside app:
flyctl ssh console --app sg-property-bot
python -c "from database_persistence import PropertyDatabase; db = PropertyDatabase(); print('OK' if db.connect() else 'FAIL')"
```

---

## 📈 Expected Results

### First Run (Day 1)
```
✅ App deploys successfully
✅ Database schema auto-initializes
✅ 8-12 properties generated
✅ Analysis metrics calculated
✅ Database insertion successful
✅ Telegram report sent
✅ Results saved as JSON
```

### Daily (06:00 AM SGT)
```
✅ Automatic execution starts
✅ New properties generated
✅ Full analysis performed
✅ Data persisted to database
✅ Telegram notification sent
✅ Results accumulated
```

### After 30 Days
```
✅ 240-360 properties stored
✅ Price history tracked
✅ Cross-comparison enabled
✅ Area trends visible
✅ Investment rankings available
✅ Query capabilities active
```

---

## 🔗 Reference Files

**Deployment Guides:**
- `.github/FLYIO_DEPLOYMENT_STEPS.md` - Complete step-by-step
- `.github/DEPLOYMENT_READINESS.md` - Deployment checklist
- `DEPLOY_MANUALLY.bat` - Quick reference

**Setup & Configuration:**
- `.github/DATABASE_SETUP_GUIDE.md` - Database setup
- `.github/PHASE_4_DATABASE_INTEGRATION.md` - Architecture

**Automation:**
- `deploy_to_flyio.py` - Automated deployment script

**Summary:**
- `.github/PHASE_4_COMPLETE_SUMMARY.md` - Phase 4 overview

---

## ✅ Deployment Checklist

**Before Deployment:**
- [ ] Have Fly.io account created
- [ ] flyctl installed
- [ ] Have Telegram credentials ready
- [ ] Read this guide

**During Deployment:**
- [ ] Run `flyctl auth login`
- [ ] Run deployment commands (10 steps)
- [ ] Wait for deployment to complete
- [ ] Verify with `flyctl status`
- [ ] Check logs with `flyctl logs --follow`

**After Deployment:**
- [ ] Test database connection
- [ ] Run test orchestration
- [ ] Verify Telegram report received
- [ ] Check properties in database
- [ ] Configure scheduled daily job
- [ ] Monitor first execution

---

## 🎯 Success Indicators

When deployment is successful, you'll see:

1. **App Status:** `Running` (not Stopped or Failed)
2. **Database Connection:** Can query `SELECT 1;`
3. **Schema Created:** Tables exist in database
4. **Test Run:** Telegram receives report with 10+ messages
5. **Properties Stored:** Can query `SELECT COUNT(*) FROM listings;`
6. **Daily Job Configured:** Machine shows in `flyctl machines list`

---

## 📞 Support

**If deployment fails:**

1. Check logs: `flyctl logs --app sg-property-bot --since 1h`
2. Review guide: `.github/FLYIO_DEPLOYMENT_STEPS.md` (Troubleshooting section)
3. Verify secrets: `flyctl secrets list --app sg-property-bot`
4. Test database: `flyctl postgres connect --app sg-property-bot-db`

**Common error messages:**

| Error | Solution |
|-------|----------|
| "Unauthorized" | Run `flyctl auth login` |
| "App not found" | Run `flyctl app create sg-property-bot --region sin` |
| "Database connection failed" | Check DB_PASSWORD in secrets |
| "Telegram not sending" | Verify token and chat ID in secrets |
| "Schema not found" | Schema auto-initializes on first run |

---

## 🚀 Next Steps

1. **Authenticate:** `flyctl auth login`
2. **Deploy:** Run commands in Option 1 or Option 2
3. **Configure:** Set up scheduled daily job
4. **Monitor:** Watch logs and verify execution
5. **Enjoy:** Daily property intelligence delivered automatically!

---

## 💡 Tips

- **Keep secrets safe:** Never commit `.env` to git (already ignored)
- **Monitor costs:** Check Fly.io dashboard for usage
- **Scale later:** Database easily handles 1000+ properties
- **Backup data:** Fly.io handles daily backups automatically
- **Rollback available:** `flyctl releases rollback --app sg-property-bot`

---

**Status:** ✅ ALL READY FOR DEPLOYMENT  
**Time to Deploy:** 10-15 minutes  
**Daily Execution:** 06:00 AM SGT (automatic after configuration)  
**Next Action:** `flyctl auth login`


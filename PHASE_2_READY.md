# Phase 1 Complete - Setup Instructions for Phase 2

**Status**: Infrastructure Live ✅ | Database Schema Pending  
**Deployed**: 2026-10-04 22:50 UTC+8  
**API URL**: https://sg-property-bot.fly.dev

---

## ✅ What's Live Right Now

### 1. API Server (ACTIVE)
```
URL: https://sg-property-bot.fly.dev
Health: https://sg-property-bot.fly.dev/health
Region: sin (Singapore)
Status: Running (1/1 checks passing)
```

### 2. PostgreSQL Database (READY)
```
Cluster: sg-property-db (Managed Postgres - Basic plan)
Region: sin (Singapore)
Disk: 10GB
Status: ready
Replicas: 1
```

### 3. Environment Variables (INJECTED)
```
DATABASE_URL=**** (auto-injected by Fly.io)
TELEGRAM_BOT_TOKEN=8864201770:AAGaqUPVsnitvQAlkq1xUrAeWSKdHNFE5WU
TELEGRAM_CHAT_ID=6834628591
```

---

## 📋 Deploy Database Schema (Choose One Method)

### Method 1: Fly.io Dashboard (EASIEST) 🌐

1. Go to: https://fly.io/dashboard
2. Select: **sg-property-db** (Managed Postgres)
3. Click: **"Open Web Terminal"** (or "SQL"...)
4. Copy contents of: `database/schema.sql`
5. Paste into terminal
6. Execute (Ctrl+Enter or click Execute)

**Time**: 2-3 minutes  
**No software needed**: ✅

---

### Method 2: PostgreSQL Client (psql)

**Prerequisites**:
- Install PostgreSQL: https://www.postgresql.org/download/

**Steps**:
```bash
# 1. Get connection string from Fly.io dashboard
# (Copy from pg-proxy or direct connection)

# 2. Connect and deploy schema:
psql postgresql://user:password@host:5432/fly-db < database/schema.sql

# 3. Verify:
psql postgresql://user:password@host:5432/fly-db
\dt  # List tables
\dv  # List views
```

**Time**: 5 minutes  
**Requires**: PostgreSQL installation

---

### Method 3: Python Script (programmatic)

**Prerequisites**:
```bash
pip install psycopg2-binary
```

**Command**:
```bash
python scripts/deploy-schema-advanced.py
```

**Time**: 3-5 minutes  
**Requires**: Python + psycopg2

---

### Method 4: Fly.io Proxy (via `flyctl`)

**Prerequisites**:
- Fly.io CLI (`flyctl`) - already installed

**Command**:
```bash
# Connect and execute schema
flyctl mpg connect nlkxjo5wgmloy93v < database/schema.sql
```

**Note**: Requires `psql` CLI available on your system.

---

## 🗄️ Database Schema Summary

**Tables (13 total)**:
- `properties` - Core property records
- `listings` - Active/historical listings
- `buildings` - Building profiles & metadata
- `price_history` - Price tracking over time
- `agents` - Real estate agent info
- `transactions` - Sales/lease transactions
- `tenants` - Tenant information
- `news_articles` - Building-related news
- `scrape_logs` - Scraper audit trail
- `api_usage` - API quota tracking
- `data_sources` - Connected data sources
- `alerts` - Configured alerts
- `user_settings` - User preferences

**Views (3 total)**:
- `property_market_analysis` - Market insights
- `building_performance` - Building metrics
- `agent_statistics` - Agent performance

**Indexes & Triggers**: Auto-created for optimization

---

## 🚀 Ready for Phase 2: Data Source Implementation

Once schema is deployed, we're ready to:

1. **PropertyGuru Scraper** (Web scraping)
   - B1/B2 listings
   - Price tracking
   - Agent contact info

2. **URA API Integration** (Official data)
   - Transaction records
   - Rental data
   - Building info

3. **99.co Scraper** (Web scraping)
   - Listings
   - Agent profiles
   - Market trends

4. **EdgeProp Integration** (Web scraping)
   - News & articles
   - Development updates
   - Market analysis

5. **Additional Sources**
   - C&W, JLL, CBRE research
   - News APIs (integration)
   - Government sources

---

## 📊 Infrastructure Status

| Component | Status | Cost | Notes |
|-----------|--------|------|-------|
| API Server | 🟢 LIVE | $10/mo | shared-cpu-1x |
| PostgreSQL | 🟢 READY | $38/mo | Managed, sin region |
| Redis | ⏳ PENDING | $5/mo | Via dashboard |
| Backups | 🟢 READY | $5/mo | Automatic |
| **TOTAL** | **Ready** | **$58/mo** | 24/7 uptime |

---

## 🔑 Access Credentials

**Safe Locations**:
- ✅ Database: Stored in Fly.io secrets (secure)
- ✅ Telegram: Stored in Fly.io secrets (secure)
- ✅ APIs: To be added via `flyctl secrets set`

**Never commit secrets to Git!** 🔒

---

## 📞 Next Steps

**Today**:
- [ ] Deploy database schema (use Method 1 if unsure)
- [ ] Verify schema with `flyctl mpg connect` + `\dt`

**This Week**:
- [ ] Implement PropertyGuru scraper
- [ ] Test data ingestion

**Next Week**:
- [ ] Add URA API integration
- [ ] Set up alert system

---

## 📚 Documentation Files

- **DEPLOYMENT_PHASE_1_COMPLETE.md** - Detailed deployment report
- **database/schema.sql** - Database DDL (17 KB)
- **docs/API_DOCUMENTATION.md** - API endpoints
- **.github/action-journal.md** - Deployment audit trail

---

## ❓ Troubleshooting

**Q: PostgreSQL connection fails?**
A: Check Fly.io dashboard for connection string, verify cluster status

**Q: Schema deployment times out?**
A: Try Method 1 (dashboard) which has better error handling

**Q: Can I start data sources without schema?**
A: No, schema must be deployed first

**Q: How do I verify schema was deployed?**
A: Connect via dashboard and run: `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';`

---

**Last Updated**: 2026-10-04 22:50 UTC+8  
**API Status**: https://sg-property-bot.fly.dev/health  
**Dashboard**: https://fly.io/apps/sg-property-bot

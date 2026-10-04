# Phase 1 Infrastructure Deployment Plan

**Status**: Starting Infrastructure Setup  
**Target**: Production-ready PostgreSQL + Redis on Fly.io  
**Timeline**: ~1-2 hours for full setup  
**Credentials**: Will be added later via .env injection

---

## Deployment Roadmap

### Step 1: Fly.io Setup ✅ (You'll do this)
- [ ] Create Fly.io account (if not exists)
- [ ] Install `flyctl` CLI
- [ ] Authenticate with Fly.io
- [ ] Set up organization

### Step 2: PostgreSQL Database ✅ (Setting up now)
- [ ] Launch PostgreSQL instance on Fly.io
- [ ] Create database schema
- [ ] Verify connectivity
- [ ] Create backup snapshots

### Step 3: Redis Cache ✅ (Setting up now)
- [ ] Launch Redis instance on Fly.io
- [ ] Configure persistence
- [ ] Set up monitoring

### Step 4: API Deployment ✅ (Setting up now)
- [ ] Build Docker image
- [ ] Deploy to Fly.io
- [ ] Set up environment variables (placeholders)
- [ ] Verify health checks

### Step 5: Scraper Deployment 🟡 (Ready but not deploying yet)
- [ ] Build scraper Docker image
- [ ] Prepare deployment config
- [ ] Ready to deploy when credentials available

### Step 6: Monitoring & Logs ✅ (Setting up now)
- [ ] Configure logging
- [ ] Set up monitoring dashboard
- [ ] Create backup strategy

---

## Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Fly.io (Singapore)                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐    ┌──────────────────┐         │
│  │ PostgreSQL 15    │    │ Redis 7          │         │
│  │ sg-property-db   │    │ sg-property-cache│         │
│  │ 2GB RAM          │    │ 256MB RAM        │         │
│  └────────┬─────────┘    └────────┬─────────┘         │
│           │                       │                   │
│           └───────────┬───────────┘                   │
│                       │                               │
│              ┌────────▼────────┐                     │
│              │  Node.js API    │                     │
│              │ :3000           │                     │
│              │ Health: /health │                     │
│              └────────┬────────┘                     │
│                       │                               │
│              (Python Scraper - On-Demand)           │
│                                                     │
└─────────────────────────────────────────────────────────┘
         │
         ▼
    Internet
         │
         ▼
   Data Sources
   (PropertyGuru, URA, 99.co, etc.)
```

---

## What You Need To Do (Prerequisites)

### 1. Fly.io Setup
```bash
# Install Fly.io CLI
# macOS:
brew install flyctl

# Windows (WSL):
curl -L https://fly.io/install.sh | sh

# Login/Create Account
flyctl auth login

# Verify installation
flyctl version
```

### 2. Environment Preparation
We've already prepared:
- ✅ `fly.toml` - Deployment configuration
- ✅ `Dockerfile` - Container images (API)
- ✅ `.env.example` - Environment template
- ✅ `database/schema.sql` - Database schema
- ✅ `docker-compose.yml` - Local development setup (for testing)

---

## Deployment Steps (Automated & Manual)

### Phase A: Local Testing (Before Fly.io)
1. Verify Docker setup
2. Run docker-compose locally
3. Test database connectivity
4. Test API health checks

### Phase B: Fly.io Deployment
1. Create Fly.io PostgreSQL instance
2. Migrate schema to production
3. Deploy API to Fly.io
4. Set up monitoring and logs

### Phase C: Configuration & Secrets
1. Create placeholder .env files
2. Document credential injection points
3. Prepare for credential injection (later)

---

## Expected Timeline

| Task | Duration | Status |
|------|----------|--------|
| Fly.io setup verification | 15 min | Pending |
| PostgreSQL deployment | 10 min | Ready |
| Database schema migration | 5 min | Ready |
| Redis deployment | 5 min | Ready |
| API Docker build | 10 min | Ready |
| API deployment to Fly.io | 10 min | Ready |
| Health check verification | 5 min | Ready |
| Monitoring setup | 10 min | Ready |
| **Total** | **~70 minutes** | **Pending** |

---

## Success Criteria

- ✅ Fly.io PostgreSQL accessible from API
- ✅ Database schema successfully migrated
- ✅ Redis cache operational
- ✅ API deployed to Fly.io with health check passing
- ✅ Logs streaming to Fly.io console
- ✅ Environment variables configured (with placeholders)
- ✅ Ready for credential injection

---

## Credential Injection Points (To Add Later)

### API Environment Variables
```
DATABASE_URL=postgresql://user:pass@fly-io-db/sg_property_bot
REDIS_URL=redis://fly-io-redis:6379
API_PORT=3000
NODE_ENV=production
```

### Scraper Environment Variables
```
DATABASE_URL=postgresql://user:pass@fly-io-db/sg_property_bot
RAPIDAPI_KEY=<YOU WILL PROVIDE>
NEWSAPI_KEY=<YOU WILL PROVIDE>
URA_ACCESS_KEY=<YOU WILL PROVIDE>
TELEGRAM_BOT_TOKEN=<YOU WILL PROVIDE>
TELEGRAM_CHAT_ID=<YOU WILL PROVIDE>
LOG_LEVEL=info
```

### Alert System (When Implemented)
```
ALERT_EMAIL_FROM=bot@propertybot.sg
ALERT_TELEGRAM_TOKEN=<YOU WILL PROVIDE>
ALERT_TELEGRAM_CHAT=<YOU WILL PROVIDE>
```

---

## What's Next

1. **You**: Install Fly.io CLI and authenticate
2. **Me**: Deploy infrastructure to Fly.io
3. **Me**: Create placeholder .env files
4. **You**: Provide Telegram + API credentials
5. **Me**: Inject credentials and test
6. **Go**: Start Phase 1 implementation

---

## Rollback Plan

If anything fails:
- Fly.io has automatic backups
- Docker images preserved locally
- Schema versioned in Git
- Easy to redeploy or rollback

---

**Ready to begin Phase 1 Infrastructure Deployment!**

Generated: 2026-10-04 16:11 SGT

# SG Property Bot - Quick Start Guide

## Prerequisites

- Git
- Docker & Docker Compose (recommended)
- OR: Python 3.9+, Node.js 18+, PostgreSQL 14+

## Option 1: Quick Start with Docker (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd sg-property-bot

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
vim .env

# Start services (PostgreSQL + Redis + API)
docker-compose up

# In another terminal, run the scraper
docker-compose --profile scraper up scraper
```

Services will be available at:
- API: http://localhost:3000
- Health check: http://localhost:3000/health
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## Option 2: Local Development Setup

### Setup Python Scraper

```bash
cd scraper

# Create virtual environment
python -m venv venv

# Activate venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy .env
cp ../.env.example .env

# Run scraper
python main.py
```

### Setup Node.js API

```bash
cd api

# Install dependencies
npm install

# Generate Prisma client
npm run prisma:generate

# Copy .env to root
cp ../.env.example .env

# Start development server
npm run dev
```

### Setup PostgreSQL

```bash
# macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Linux (Ubuntu)
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
# Or use WSL + Linux instructions

# Create database
createdb sg_property_bot

# Run schema
psql sg_property_bot < database/schema.sql
```

### Setup Redis (Optional but Recommended)

```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt-get install redis-server
sudo systemctl start redis-server

# Windows (WSL or Docker)
docker run -d -p 6379:6379 redis:7-alpine
```

---

## Environment Configuration

Copy `.env.example` to `.env` and update:

```bash
# Database (Fly.io PostgreSQL)
DATABASE_URL=postgresql://user:pass@fly-io-db.internal/sg_property_bot

# Redis
REDIS_URL=redis://localhost:6379

# External APIs
RAPIDAPI_KEY=your_key_here
NEWSAPI_KEY=your_key_here
URA_ACCESS_KEY=your_key_here

# Scraper
SCRAPER_HEADLESS=true
SCRAPER_TIMEOUT=30000
```

### Getting API Keys

**RapidAPI (for 99.co):**
1. Visit https://rapidapi.com/99co-official/api/99-co-sg
2. Click "Subscribe" (free tier available)
3. Copy API key from dashboard

**NewsAPI:**
1. Visit https://newsapi.org
2. Register for free account
3. Copy API key

**URA Data Service:**
1. Visit https://www.ura.gov.sg/maps/?service=dataservice
2. Register for free account
3. Receive access key via email

---

## Verify Installation

```bash
# Check API server
curl http://localhost:3000/health

# Check database
psql sg_property_bot -c "SELECT COUNT(*) FROM properties;"

# Check Redis
redis-cli ping
```

Expected responses:
- API: `{"status":"OK",...}`
- Database: Should work without errors
- Redis: `PONG`

---

## Running the Bot

### Full System
```bash
# Terminal 1: Database + Redis + API
docker-compose up

# Terminal 2: Scraper
docker-compose --profile scraper up scraper

# Terminal 3: Monitor logs
tail -f logs/app.log
```

### Development Only
```bash
# Terminal 1: API
cd api && npm run dev

# Terminal 2: Scraper
cd scraper && python main.py

# Terminal 3: Monitor
tail -f logs/*.log
```

---

## First Run Checklist

- [ ] Database created and schema loaded
- [ ] API server running (port 3000)
- [ ] Redis running (port 6379)
- [ ] Scraper connected to database
- [ ] API responds to `/health` endpoint
- [ ] Database contains initial data

---

## Deployment to Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Create app (interactive)
flyctl launch --name sg-property-bot

# Deploy
flyctl deploy

# Monitor
flyctl logs
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 3000
lsof -i :3000

# Kill it
kill -9 <PID>
```

### Database Connection Failed
```bash
# Check connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

### Docker Issues
```bash
# Rebuild images
docker-compose down
docker-compose build --no-cache

# Start fresh
docker-compose up
```

---

## Next Steps

1. **Verify API**: Test endpoints at http://localhost:3000/api/*
2. **Check Data**: Query properties table for initial data
3. **Monitor Scraper**: Watch logs for any errors
4. **Configure Alerts**: Set up price change notifications
5. **Build Dashboard**: Start Phase 2 frontend development

---

## Documentation

- [Architecture](./DATA_SOURCES.md) - Data sources and integration strategy
- [Development Checklist](./.github/DEVELOPMENT_CHECKLIST.md) - Tasks and milestones
- [API Documentation](./api/README.md) - API endpoints and usage
- [Database Schema](./database/schema.sql) - Database structure

---

**Status**: Phase 1 - Foundation Ready  
**Last Updated**: 2026-10-04

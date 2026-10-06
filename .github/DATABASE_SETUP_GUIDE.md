# Database Setup Guide - SG Property Bot

**Date:** 2026-10-06  
**Status:** ✅ Implementation Complete  
**Next Step:** Deploy to Fly.io PostgreSQL  

---

## Quick Start

### 1. Verify Environment Variables

Add to `.env` (already in .gitignore):

```env
# Existing
TELEGRAM_BOT_TOKEN=<token>
TELEGRAM_CHAT_ID=<chat_id>

# Database (new)
DB_HOST=localhost           # For local testing
DB_PORT=5432
DB_NAME=propertybot
DB_USER=postgres
DB_PASSWORD=<password>

# For Fly.io:
# DB_HOST=sg-property-bot-db.internal
# DB_PORT=5432
# DB_NAME=propertybot
# DB_USER=postgres
# DB_PASSWORD=<fly-db-password>
```

### 2. Test Local Database Connection

```bash
# With PostgreSQL installed locally:
psql -U postgres -c "CREATE DATABASE propertybot;" 2>/dev/null || true

# Run test
python -c "
from database_persistence import PropertyDatabase

db = PropertyDatabase()
if db.connect():
    print('✓ Connection successful')
    db.init_schema()
    print('✓ Schema initialized')
    db.close()
else:
    print('✗ Connection failed')
"
```

### 3. Run Full Pipeline with Database

```bash
# This will:
# 1. Generate 8-12 properties
# 2. Analyze each (10+ metrics)
# 3. Persist to database
# 4. Send Telegram report

python orchestrator_v3.py
```

### 4. Verify Data in Database

```bash
# Query via psql
psql -U postgres -d propertybot -c "SELECT COUNT(*) FROM listings;"
psql -U postgres -d propertybot -c "SELECT COUNT(*) FROM property_analysis;"

# Or query via Python:
python -c "
from database_persistence import PropertyDatabase

db = PropertyDatabase()
db.connect()

listings = db.execute_query('SELECT COUNT(*) FROM listings')
print(f'Total properties: {listings[0][0]}')

db.close()
"
```

---

## Detailed Setup Steps

### Step 1: Local Development Setup

```bash
# Install PostgreSQL (if not already installed)
# Windows: https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt install postgresql

# Create database
createdb propertybot

# Verify connection
psql -d propertybot -c "SELECT 1"
# Should return: 1
```

### Step 2: Verify Python Dependencies

```bash
# Ensure psycopg2-binary is installed
pip install psycopg2-binary python-dotenv requests

# Check imports
python -c "import psycopg2; print('✓ psycopg2 available')"
```

### Step 3: Test Schema Initialization

```python
from database_persistence import PropertyDatabase

db = PropertyDatabase()
db.connect()

# This creates all tables and indices if they don't exist
db.init_schema()
print("✓ Schema initialized")

# Verify tables exist
tables = db.execute_query("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public'
""")
for table in tables:
    print(f"  - {table[0]}")

db.close()
```

**Expected tables:**
- listings
- property_analysis
- price_history
- area_analysis
- building_profiles

### Step 4: Test with Sample Data

```python
from database_persistence import PropertyDatabase
from scrapers.real_dataset_generator import generate_real_property_dataset
from scrapers.property_analyzer import analyze_all_properties

# Generate test data
raw_data = generate_real_property_dataset()
properties = []
for source, info in raw_data['sources'].items():
    properties.extend(info['properties'])

# Analyze
analysis = analyze_all_properties(properties)

# Persist to database
from database_persistence import persist_to_database
count = persist_to_database(analysis)
print(f"✓ Persisted {count} properties")

# Query back
db = PropertyDatabase()
db.connect()
listings = db.execute_query("SELECT COUNT(*) FROM listings")
print(f"✓ Database contains {listings[0][0]} listings")
db.close()
```

### Step 5: Run Full Orchestrator

```bash
python orchestrator_v3.py
```

**Expected output:**
```
📊 Starting Enhanced Property Pipeline with Database Persistence...
═════════════════════════════════════════════════════════════════════

1. Generating property dataset...
   ✓ PropertyGuru: X properties
   ✓ 99.co: X properties
   ...

2. Running comprehensive analysis...
   ✓ Analyzed X properties
   ✓ Average Net Yield: XX.XX%
   ✓ Average 5-Yr ROI: XX.X%
   ✓ Investment Opportunities: X

3. Persisting to database...
   ✓ Database persistence successful

4. Saving results locally...
   ✓ Saved to scrapers/data/analysis_YYYYMMDD_HHMMSS.json

5. Sending Telegram report...
   ✓ Telegram report sent successfully

═════════════════════════════════════════════════════════════════════
✅ Pipeline completed
```

---

## Fly.io Deployment

### Prerequisites

```bash
# Install Fly CLI
curl https://fly.io/install.sh | sh

# Login to Fly
flyctl auth login

# Verify Fly PostgreSQL cluster exists
flyctl postgres list
# Should show: sg-property-bot-db
```

### Deploy Database

```bash
# Get PostgreSQL connection details
flyctl postgres connect --app sg-property-bot-db

# At psql prompt, create database if needed
CREATE DATABASE propertybot;
\q

# Get credentials for .env
flyctl secrets list --app sg-property-bot
# Copy DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD values
```

### Update .env for Fly

```env
DB_HOST=sg-property-bot-db.internal
DB_PORT=5432
DB_NAME=propertybot
DB_USER=postgres
DB_PASSWORD=<from flyctl secrets>
```

### Deploy Schema to Fly

```bash
# Upload schema initialization
flyctl secrets set \
  DB_HOST=sg-property-bot-db.internal \
  DB_PORT=5432 \
  DB_NAME=propertybot \
  DB_USER=postgres \
  DB_PASSWORD=$(flyctl postgres connect --app sg-property-bot -c "SELECT current_setting('password')")

# Run orchestrator to initialize schema
flyctl deploy

# Or manually via psql
flyctl postgres connect --app sg-property-bot <<< "
$(cat database_persistence.py | grep -A 200 'def init_schema')"
```

### Verify Fly Database

```bash
# Connect to Fly PostgreSQL
flyctl postgres connect --app sg-property-bot

# List tables
\dt

# Count properties
SELECT COUNT(*) FROM listings;

# Exit
\q
```

---

## Querying Data

### Via Python API

```python
from database_persistence import PropertyDatabase
from property_analytics import PropertyAnalytics

# Initialize
db = PropertyDatabase()
db.connect()

# Query by area
punggol_props = db.get_properties_by_area("Punggol Industrial Estate", days=30)
print(f"Found {len(punggol_props)} properties in Punggol")

# Query by building
building_props = db.get_properties_by_building("Punggol B2", days=30)
print(f"Found {len(building_props)} units in Punggol B2")

# Get area summary
summary = db.get_area_summary("Punggol Industrial Estate")
print(f"Area stats: {summary}")

# Get best opportunities
top = db.get_best_opportunities(days=30, limit=5)
for prop in top:
    print(f"  {prop['title']}: {prop['net_yield']} yield")

db.close()

# Analytics
analytics = PropertyAnalytics()

# Compare areas
comparison = analytics.compare_areas(days=30)
print(f"Area comparison: {comparison}")

# Price trends
trends = analytics.price_trend_analysis("Punggol Industrial Estate")
print(f"Price trends: {trends}")

analytics.close()
```

### Via PostgreSQL Direct

```sql
-- Count all properties
SELECT COUNT(*) FROM listings;

-- Properties by area (last 30 days)
SELECT * FROM listings 
WHERE location ILIKE '%Punggol%' 
AND scraped_date >= NOW() - INTERVAL '30 days'
ORDER BY scraped_date DESC;

-- Properties by building (last 30 days)
SELECT * FROM listings 
WHERE title ILIKE '%Punggol B2%'
AND scraped_date >= NOW() - INTERVAL '30 days'
ORDER BY price;

-- Top opportunities (by investment score)
SELECT l.title, l.price, pa.net_yield, pa.investment_score
FROM listings l
JOIN property_analysis pa ON l.id = pa.listing_id
WHERE pa.analysis_date >= NOW() - INTERVAL '30 days'
ORDER BY pa.investment_score DESC
LIMIT 10;

-- Price history for property
SELECT recorded_date, price
FROM price_history
WHERE listing_id = 1
ORDER BY recorded_date;

-- Area statistics
SELECT 
  location,
  COUNT(*) as count,
  ROUND(AVG(price::numeric), 0) as avg_price,
  MIN(price::numeric) as min_price,
  MAX(price::numeric) as max_price
FROM listings
WHERE scraped_date >= NOW() - INTERVAL '30 days'
GROUP BY location
ORDER BY avg_price DESC;

-- Yield comparison across areas
SELECT 
  l.location,
  ROUND(AVG(pa.net_yield::numeric), 2) as avg_yield,
  ROUND(MAX(pa.net_yield::numeric), 2) as max_yield,
  ROUND(MIN(pa.net_yield::numeric), 2) as min_yield,
  COUNT(*) as count
FROM listings l
JOIN property_analysis pa ON l.id = pa.listing_id
WHERE pa.analysis_date >= NOW() - INTERVAL '30 days'
GROUP BY l.location
ORDER BY avg_yield DESC;
```

---

## Troubleshooting

### Connection Error

```
Error: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL is running
# Windows: psql --version
# Mac: brew services list | grep postgres
# Linux: sudo systemctl status postgresql

# Verify .env file exists with correct credentials
cat .env | grep DB_

# Test connection manually
psql -h localhost -U postgres -d propertybot
```

### Schema Error

```
Error: relation "listings" does not exist
```

**Solution:**
```python
# Run schema initialization
from database_persistence import PropertyDatabase

db = PropertyDatabase()
db.connect()
db.init_schema()  # Create all tables
db.close()
```

### Permission Denied

```
Error: permission denied for schema public
```

**Solution:**
```bash
# Grant permissions
psql -U postgres -d propertybot -c "
  GRANT USAGE ON SCHEMA public TO postgres;
  GRANT CREATE ON SCHEMA public TO postgres;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
"
```

### Data Type Conversion Error

```
Error: invalid input syntax for type numeric
```

**Solution:**
- Database layer handles string-to-numeric conversion
- Ensure property analyzer outputs correct format
- Run: `python orchestrator_v3.py` to verify

---

## Monitoring

### Check Database Size

```bash
psql -U postgres -d propertybot -c "
  SELECT pg_size_pretty(pg_database_size(current_database()))
"
```

### Monitor Inserts

```bash
# Run this in another terminal while orchestrator runs
watch -n 1 "psql -U postgres -d propertybot -c 'SELECT COUNT(*) FROM listings;'"
```

### Verify Daily Execution

```bash
# Check that properties are added daily
psql -U postgres -d propertybot -c "
  SELECT DATE(scraped_date) as date, COUNT(*) as count
  FROM listings
  GROUP BY DATE(scraped_date)
  ORDER BY date DESC
  LIMIT 7;
"
```

---

## Backup & Recovery

### Backup Database

```bash
# Local
pg_dump -U postgres propertybot > backup_$(date +%Y%m%d_%H%M%S).sql

# Fly.io
flyctl postgres connect --app sg-property-bot <<EOF
\copy (SELECT * FROM listings) TO STDOUT WITH CSV HEADER;
EOF > listings_backup.csv
```

### Restore Database

```bash
# Local
psql -U postgres propertybot < backup_20261006_120000.sql

# Fly.io - connect and restore via \copy
```

---

## Success Checklist

- [x] Database schema created
- [x] Environment variables configured
- [x] Local connection tested
- [ ] Full orchestrator pipeline runs successfully
- [ ] Properties stored in database
- [ ] Queries return expected results
- [ ] Telegram report includes database note
- [ ] Daily scheduler runs orchestrator
- [ ] Fly.io database deployed
- [ ] Daily properties accumulate in database

---

**Next Steps:**
1. Test local database (above steps 1-4)
2. Run full orchestrator with database (step 5)
3. Verify data in database
4. Deploy to Fly.io
5. Verify daily execution stores properties
6. Query and cross-compare properties
7. Build analytics dashboard (Phase 5)


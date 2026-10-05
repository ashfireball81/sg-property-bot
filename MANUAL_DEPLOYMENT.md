# 🚀 MANUAL SCHEMA DEPLOYMENT GUIDE

**Status**: Automated methods blocked due to Fly.io API authentication issues (401 Unauthorized)

**Solution**: Deploy manually via Fly.io Web Terminal (takes 2-3 minutes)

---

## ✅ QUICK START - Deploy Now!

### Step 1: Open Fly.io Dashboard
👉 **Go here**: https://fly.io/dashboard/apps/sg-property-db

### Step 2: Click "Web Terminal"
- Look for the **"Web Terminal"** tab in the top navigation
- Click to open the database terminal

### Step 3: Copy Schema File
**In your local terminal/file explorer:**
```
File: C:\Users\ash_f\Desktop\python\sg-property-bot\database\schema.sql
Size: 17.6 KB
```

**Copy the ENTIRE contents of this file**

### Step 4: Paste into Web Terminal
- Paste the SQL code into the Fly.io Web Terminal
- Press **Enter** to execute

### Step 5: Verify Deployment
After the command completes, run this verification query:

```sql
SELECT COUNT(*) as table_count FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
```

**Expected result: 13**

---

## 📊 What Gets Created

After successful deployment:
- ✅ 13 database tables
- ✅ 3 analytical views  
- ✅ 30+ performance indexes
- ✅ 2 data integrity triggers

---

## 🔧 Why Automation Failed

**Root Cause**: Fly.io API authentication returned 401 Unauthorized
- FLY_API_TOKEN environment variable: ✓ Set
- flyctl CLI: ✓ Installed (v0.4.103)
- flyctl auth whoami: ❌ Failed (401)
- DATABASE_URL retrieval: ❌ Failed (permission denied)

**Workaround**: Use Fly.io Web Terminal (browser-based, no CLI auth needed)

---

## 📁 File Locations

**Schema File:**
```
C:\Users\ash_f\Desktop\python\sg-property-bot\database\schema.sql
```

**GitHub Repositories:**
- New repo: https://github.com/ashfireball81/sg-property-bot ✅ ACTIVE
- Old repo: https://github.com/ashfireball81/GeneralBot (deprecated for this project)

---

## 🎯 After Deployment

1. ✅ Verify schema created (13 tables)
2. 🚀 Proceed to Phase 2: Implement data sources
3. 📊 Set up Telegram daily alerts
4. 💼 Begin accumulating property market data

---

## 💡 Alternative Manual Methods

### Alternative 1: Direct PostgreSQL Connection (if you have psql installed)
```powershell
# Get DATABASE_URL from Fly.io dashboard
# Then run:
psql "your-database-url-here" -f C:\Users\ash_f\Desktop\python\sg-property-bot\database\schema.sql
```

### Alternative 2: Use Python psycopg2
```python
import psycopg2

# Get DATABASE_URL from Fly.io dashboard
conn = psycopg2.connect("your-database-url")
cursor = conn.cursor()
cursor.execute(open('database/schema.sql').read())
conn.commit()
```

---

**Status**: Ready for manual deployment  
**Last Updated**: 2026-10-05 06:56:07 UTC+8  
**Estimated Time**: 2-3 minutes

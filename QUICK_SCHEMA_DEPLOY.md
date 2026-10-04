# Quick Start: Deploy Database Schema

**Goal**: Get the database schema running in 2-3 minutes  
**Difficulty**: Easy ✅

---

## 🚀 FASTEST METHOD - Fly.io Dashboard

### Step-by-Step:

**1. Open Dashboard**
   - Go to: https://fly.io/dashboard

**2. Select Database**
   - Find: "sg-property-db" in your apps
   - Click it

**3. Open Terminal**
   - Look for: "Tools" or "Web Terminal" button
   - Click: "SQL" or "Web Terminal"

**4. Copy Schema**
   - Open file: `database/schema.sql` (in this repo)
   - Select all (Ctrl+A)
   - Copy (Ctrl+C)

**5. Paste & Execute**
   - In the Fly.io terminal
   - Paste (Ctrl+V)
   - Hit: Enter or click "Execute"

**6. Wait**
   - Database creates tables
   - Should see: `CREATE TABLE`, `CREATE VIEW` messages
   - ~2-3 minutes

**7. Verify Success**
   - Run: `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';`
   - Should show: 13 tables

---

## ✅ Verification Checklist

After deployment, run these to confirm:

```sql
-- Check tables (should show 13)
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check views (should show 3)
SELECT table_name FROM information_schema.views 
WHERE table_schema = 'public';

-- Sample query
SELECT COUNT(*) as total_tables FROM information_schema.tables 
WHERE table_schema = 'public';
```

Expected output: **13 tables, 3 views**

---

## Tables That Will Be Created

| Table | Purpose |
|-------|---------|
| `properties` | Core property records |
| `listings` | Active/historical listings |
| `buildings` | Building profiles |
| `price_history` | Price tracking |
| `agents` | Real estate agents |
| `transactions` | Sales/leases |
| `tenants` | Tenant info |
| `news_articles` | Building news |
| `scrape_logs` | Audit trail |
| `api_usage` | API tracking |
| `data_sources` | Connected sources |
| `alerts` | Alert config |
| `user_settings` | User prefs |

---

## Views That Will Be Created

| View | Purpose |
|------|---------|
| `property_market_analysis` | Market insights |
| `building_performance` | Performance metrics |
| `agent_statistics` | Agent performance |

---

## 🆘 Troubleshooting

**Q: Dashboard won't load?**
- Clear cache: Ctrl+Shift+Del
- Use incognito/private window
- Try Firefox if Chrome fails

**Q: SQL commands not executing?**
- Check syntax (copy-paste should be fine)
- Schema file might have extra characters
- Try smaller chunks if it times out

**Q: "Table already exists" error?**
- Schema might have run partially
- You can safely ignore (idempotent)
- Tables are fine

**Q: Verify showed 0 tables?**
- Connection might be stale
- Refresh dashboard
- Try query again

**Q: Still having issues?**
- Try Method 2: Command line (psql)
- Contact support with error message

---

## 📊 What Happens Next

After schema is deployed:

1. **Database is ready** for data ingestion
2. **API can start** writing to tables
3. **Scrapers can run** (Phase 2)
4. **Alerts can trigger** via Telegram

---

## ⏱️ Timeline

- **Now**: Deploy schema (2-3 min)
- **Next**: Verify tables (1 min)
- **Then**: Start Phase 2 scrapers (1-2 weeks)

---

## 📝 Notes

- Schema is idempotent (safe to run multiple times)
- Indexes created automatically
- Foreign keys validated
- Triggers enabled for audit trail

---

**Stuck?** See `PHASE_2_READY.md` for alternative deployment methods.

**Ready for Phase 2?** Schema deployment is the last step before data ingestion!

# Data Sources Summary & Integration Mapping

**Research Date**: 2026-10-04  
**Status**: Complete - Ready for Implementation

---

## Overview

This document provides a quick reference guide to all 10 data sources identified for the SG Property Digital Twin Bot. Use this to quickly understand integration approach for each source.

---

## Tier 1: Phase 1 (High Priority - Weeks 1-2)

### 1️⃣ PropertyGuru - Web Scraper
**URL**: https://www.propertyguru.com.sg  
**API Type**: Web Scraping Required  
**Cost**: FREE  
**Difficulty**: Medium  
**Time Estimate**: 10-15 hours

**Coverage**: All property types (residential, commercial, industrial)  
**Key Data Points**:
- Listings (buy, rent, auction)
- Prices and price per sqft
- Agent information & contact
- Unit details, floor, size
- Property location & specifications

**Integration Approach**:
```python
# Technology: Selenium + BeautifulSoup
scraper = PropertyGuruScraper(headless=True)
listings = scraper.fetch_listings(property_type='B1')
for listing in listings:
    validate(listing)
    deduplicate(listing)
    save(listing)
```

**Considerations**:
- Implement exponential backoff (3-5s between requests)
- Rotate user agents and IP addresses
- Cache results to minimize re-requests
- Respect robots.txt

---

### 2️⃣ URA Data Service - Government API ⭐ EASIEST
**URL**: https://www.ura.gov.sg/maps/?service=dataservice  
**API Type**: REST API (Official)  
**Cost**: FREE (Government)  
**Difficulty**: Low  
**Time Estimate**: 5-8 hours

**Coverage**: Transaction history, prices, car park data  
**Key Data Points**:
- Private residential transactions (last 3 years)
- Median rental data
- Property price indices
- Tenure information
- Car park details

**Integration Approach**:
```python
# 1. Register at URA website (free)
# 2. Get access key via email
# 3. Use API to fetch data

ura = URADataService(access_key=YOUR_KEY)
token = ura.get_daily_token()
transactions = ura.fetch_transactions(token)
```

**Endpoints**:
```
GET https://www.ura.gov.sg/uraDataService/insertNewToken.action
  Headers: AccessKey

GET https://www.ura.gov.sg/uraDataService/invokeUraDS?service=ResidentialTransaction
  Headers: AccessKey, Token
```

**Advantages**:
- Official government data (high credibility)
- No scraping needed
- Structured API responses
- Regular updates

---

### 3️⃣ 99.co - Official REST API
**URL**: https://rapidapi.com/99co-official/api/99-co-sg  
**API Type**: REST API (via RapidAPI)  
**Cost**: Free tier (100 req/month) or $5-50/month  
**Difficulty**: Low  
**Time Estimate**: 3-5 hours

**Coverage**: Listings, projects, agents, transactions, price trends  
**Key Data Points**:
- All property types (commercial + residential)
- Detailed listing info
- Agent directory
- Historical transactions
- Market price trends

**Integration Approach**:
```python
import requests

headers = {
    "X-RapidAPI-Key": YOUR_KEY,
    "X-RapidAPI-Host": "99co-api.p.rapidapi.com"
}

# Get listings
response = requests.get(
    "https://99co-api.p.rapidapi.com/listings",
    headers=headers,
    params={"propertyType": "commercial", "district": "Central"}
)

listings = response.json()
```

**API Endpoints**:
- `GET /listings` - Search listings
- `GET /listings/{id}` - Get details
- `GET /projects` - Development projects
- `GET /agents` - Agent directory
- `GET /transactions` - Historical transactions
- `GET /price-trends` - Market trends

**Free Tier Limits**:
- 100 requests/month
- 10 results per request

---

### 4️⃣ data.gov.sg - Government Datasets
**URL**: https://data.gov.sg  
**API Type**: REST API (Public)  
**Cost**: FREE  
**Difficulty**: Low  
**Time Estimate**: 3-4 hours

**Coverage**: HDB properties, private transactions, demographics  
**Key Datasets**:
- Private Residential Property Transactions (1999+)
- HDB Property Information
- Property Market Indicators
- Planning & Development

**Integration Approach**:
```python
import requests

# Get transaction data
url = "https://data.gov.sg/api/action/datastore_search"
params = {
    "resource_id": "d_7c69c943d5f0d89d6a9a773d2b51f337",
    "limit": 100
}

response = requests.get(url, params=params)
records = response.json()['records']
```

**API Documentation**: https://data.gov.sg/developer

---

## Tier 2: Phase 2 (Commercial Focus - Weeks 3-4)

### 5️⃣ EdgeProp - Commercial Property Focus
**URL**: https://edgeprop.sg  
**API Type**: Web Scraper or Apify  
**Cost**: FREE (custom scraper) or $1.50/1000 listings (Apify)  
**Difficulty**: Low-Medium  
**Time Estimate**: 8-12 hours (custom) or 1 hour (Apify)

**Coverage**: Strong on commercial & industrial properties  
**Key Data Points**:
- Commercial/industrial listings
- Building specifications
- Tenant information
- Lease terms
- Agent contacts

**Two Options**:

**Option A: Apify (Easiest, Paid)**
```python
# Use ready-made Apify scraper
apify_url = "https://api.apify.com/v2/acts/rl1987/edgeprop-sg-api-scraper/run-sync"
response = requests.post(apify_url, json=payload, auth=(token, ""))
```

**Option B: Custom Selenium Scraper (Recommended)**
```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://edgeprop.sg/search?...")
listings = driver.find_elements(By.CLASS_NAME, "prop-card")
# Parse and extract data
```

---

### 6️⃣ CBRE Singapore - Premium Commercial
**URL**: https://www.cbre.com.sg/properties  
**API Type**: Web Scraper  
**Cost**: FREE  
**Difficulty**: Medium  
**Time Estimate**: 12-15 hours

**Coverage**: Office, retail, industrial, logistics  
**Key Data Points**:
- Premium commercial properties
- Lease terms & conditions
- Tenant information
- Agent details

**Integration Approach**:
```python
# Analyze XHR requests in browser dev tools
# Most data comes from JSON API calls
# Parse XHR responses instead of HTML (more efficient)

response = requests.get("https://api.cbre.com.sg/properties", params=filters)
properties = response.json()
```

---

### 7️⃣ JLL Singapore - Commercial Broker
**URL**: https://www.jll.com.sg  
**API Type**: Web Scraper  
**Cost**: FREE  
**Difficulty**: Medium  
**Time Estimate**: 10-12 hours

**Coverage**: Commercial leasing and investment sales  
**Key Websites**:
- https://property.jll.com.sg/ (leasing)
- https://invest.jll.com/ (investment sales)

---

### 8️⃣ Cushman & Wakefield Singapore - Commercial Broker
**URL**: https://www.cushmanwakefield.com/en/singapore  
**API Type**: Web Scraper  
**Cost**: FREE  
**Difficulty**: Medium  
**Time Estimate**: 10-12 hours

**Coverage**: Offices, industrial, retail, business parks  
**Key Data Points**: Similar to CBRE and JLL

---

## Tier 3: Phase 3+ (Enhancement - Weeks 5+)

### 9️⃣ News & Article APIs
**For Building-Specific Intelligence**

| API | Type | Cost | Coverage |
|-----|------|------|----------|
| NewsAPI.org | REST API | Free (500 req/day) | Global news |
| Google News | RSS/API | Free | News aggregation |
| SGBusiness Review | Web Scraper | Free | Local business |

**Use Case**: Enrich building profiles with news about:
- New developments
- Redevelopment announcements
- Market trends
- Building management changes
- Tenant updates

**Example**:
```python
# Fetch news about a building
response = requests.get("https://newsapi.org/v2/everything", params={
    "q": "Marina Bay building redevelopment",
    "sortBy": "publishedAt",
    "language": "en",
    "apiKey": NEWS_API_KEY
})
```

---

### 🔟 SRX - Alternative Listing Source
**URL**: https://www.srx.com.sg  
**API Type**: Web Scraper  
**Cost**: FREE  
**Difficulty**: Medium  
**Time Estimate**: 12-15 hours

**Coverage**: Residential (HDB, condo), some commercial  
**Status**: Phase 3+ (Lower priority for commercial focus)

---

## Implementation Roadmap

### Week 1: Foundation
```
Day 1-2: URA API + data.gov.sg (easiest)
Day 3-4: 99.co API integration
Day 5: PropertyGuru scraper prototype
Day 6-7: Testing, validation, integration
```

### Week 2: Expansion
```
Day 1-2: PropertyGuru scraper (complete)
Day 3-4: Validation pipeline & deduplication
Day 5-7: Price history tracking, API endpoints
```

### Week 3-4: Commercial Focus
```
Day 1-4: EdgeProp, CBRE, JLL, C&W scrapers
Day 5-8: Advanced features, alerts, dashboard
```

---

## Data Source Decision Matrix

| Criteria | PropertyGuru | URA API | 99.co | EdgeProp | CBRE | JLL | C&W |
|----------|--------------|---------|-------|----------|------|-----|-----|
| **Coverage** | All | Residential | All | Comm/Ind | Comm | Comm | Comm |
| **Cost** | Free | Free | $5/mo | Free | Free | Free | Free |
| **Effort** | Medium | Low | Low | Medium | Med | Med | Med |
| **Freshness** | Real-time | Monthly | Daily | Daily | Daily | Daily | Daily |
| **Quality** | High | Excellent | High | High | High | High | High |
| **Integration** | Scraper | API | API | Scraper | Scraper | Scraper | Scraper |
| **Reliability** | Medium | High | High | Medium | Medium | Medium | Medium |
| **Value Score** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## Getting Started Checklist

### Before Starting Integration

- [ ] Review DATA_SOURCES.md thoroughly
- [ ] Follow QUICKSTART.md for local setup
- [ ] Set up development environment (Docker or local)
- [ ] Create .env file with placeholders
- [ ] Register for API keys:
  - [ ] URA Data Service account
  - [ ] RapidAPI key (for 99.co)
  - [ ] NewsAPI key (optional)

### Integration Order (Recommended)

1. **Start here**: URA API (easiest, official data)
2. **Quick win**: data.gov.sg (static datasets)
3. **Core source**: 99.co API (comprehensive data)
4. **Main source**: PropertyGuru scraper (largest inventory)
5. **Enhance**: EdgeProp, CBRE, JLL (commercial focus)
6. **Polish**: News APIs, advanced analytics

---

## Legal & Ethical Guidelines

✅ **DO**:
- Check robots.txt before scraping
- Implement respectful rate limiting (3-5s delays)
- Use rotating user agents
- Add exponential backoff for 429/503 errors
- Cache results to minimize requests
- Review Terms of Service for each source
- Consider partnerships with brokers

❌ **DON'T**:
- Bypass IP blocking mechanisms
- Scrape at excessive rates
- Redistribute scraped data commercially
- Use for spam or harmful purposes
- Violate Terms of Service

---

## Support & Resources

**Official Documentation**:
- URA API: https://www.ura.gov.sg/maps/?service=dataservice
- 99.co API: https://rapidapi.com/99co-official/api/99-co-sg
- data.gov.sg: https://data.gov.sg/developer
- NewsAPI: https://newsapi.org/docs

**Tools & Libraries**:
- Selenium: https://www.selenium.dev
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup
- APScheduler: https://apscheduler.readthedocs.io
- Prisma: https://www.prisma.io/docs

**Community**:
- Stack Overflow: Tag with `singapore-property` or `web-scraping`
- GitHub: Fork examples from other SG property bots
- Reddit: r/singapore for local insights

---

**Research Completed**: 2026-10-04  
**Status**: Ready for Implementation  
**Next**: Begin Phase 1 integration

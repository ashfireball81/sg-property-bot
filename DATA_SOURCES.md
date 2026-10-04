# SG Property Digital Twin Bot - Data Sources & Integration Plan

**Last Updated**: 2026-10-04  
**Research Status**: ✅ Complete  
**Implementation Status**: Phase 1 Kickoff

---

## Executive Summary

This document catalogs all viable data sources for Singapore commercial/industrial property intelligence, with integration priority, technical approach, and estimated effort.

**Key Finding**: 10 high-value sources identified across APIs, scrapers, and government data.

---

## Data Sources by Category

### 🔴 TIER 1: Highest Priority (Phase 1)

#### 1. **PropertyGuru** ⭐ PRIMARY
| Aspect | Details |
|--------|---------|
| **Type** | Web Scraper |
| **Coverage** | All property types (residential, commercial, industrial, retail) |
| **Data Points** | Listings, prices, agent contact, unit details, location |
| **Update Frequency** | Real-time (hourly scrape) |
| **Tech Stack** | Selenium + BeautifulSoup |
| **Legality** | ✅ No official API; scraping acceptable if respectful |
| **Rate Limiting** | Need exponential backoff, user-agent rotation |
| **Cost** | Free |
| **Effort** | Medium (10-15 hours) |
| **Integration** | Priority 1 |
| **Link** | https://www.propertyguru.com.sg |

**Implementation Notes**:
- Start with commercial listings filter
- Key selectors: `.prop-card`, `.price`, `.agent-name`
- Store: listing_id, title, price, address, agent_id, listing_date
- Deduplication: hash(title + price + address)

---

#### 2. **URA Data Service API** ⭐ GOVERNMENT (FREE)
| Aspect | Details |
|--------|---------|
| **Type** | Official REST API |
| **Coverage** | Transaction history, private residential, car parks, planning |
| **Data Points** | Sales/rentals, median prices, transaction dates, tenure info |
| **Update Frequency** | Quarterly (official), daily sync recommended |
| **Authentication** | Free access key registration |
| **Tech Stack** | REST API calls (Python requests) |
| **Cost** | Free (government) |
| **Effort** | Low (5-8 hours) |
| **Integration** | Priority 1 |
| **Link** | https://www.ura.gov.sg/maps/?service=dataservice |

**Registration Process**:
```bash
1. Visit https://www.ura.gov.sg/maps/?service=dataservice
2. Register for free account
3. Receive access key via email
4. Generate daily token using access key
5. Use token for API calls
```

**Sample API Endpoints**:
```python
# Get token
GET https://www.ura.gov.sg/uraDataService/insertNewToken.action
Headers: AccessKey: YOUR_KEY

# Get residential transactions
GET https://www.ura.gov.sg/uraDataService/invokeUraDS?service=ResidentialTransaction
Headers: AccessKey, Token

# Car park data
GET https://www.ura.gov.sg/uraDataService/invokeUraDS?service=CarParkAvailability
```

**Data Schema**:
- property_id, address, transaction_date, price, transaction_type, tenure_remaining

---

#### 3. **99.co REST API (via RapidAPI)** ⭐ OFFICIAL API
| Aspect | Details |
|--------|---------|
| **Type** | Official REST API |
| **Coverage** | Listings, projects, agents, transaction history, price trends |
| **Data Points** | All property details, agent contacts, historical transactions |
| **Authentication** | RapidAPI key (free tier available) |
| **Rate Limit** | Free: 100 req/month; Paid: $5-50/month |
| **Tech Stack** | REST API (Python requests, Node.js axios) |
| **Cost** | Free tier or $5/month |
| **Effort** | Low (3-5 hours) |
| **Integration** | Priority 1 |
| **Link** | https://rapidapi.com/99co-official/api/99-co-sg |

**Endpoints Available**:
```
GET /listings           # Search all listings
GET /listings/{id}      # Get listing details
GET /projects           # Get development projects
GET /agents             # Agent directory
GET /transactions       # Historical transactions
GET /price-trends       # Market price trends
```

**Example Call**:
```python
import requests

headers = {
    "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
    "X-RapidAPI-Host": "99co-api.p.rapidapi.com"
}

url = "https://99co-api.p.rapidapi.com/listings"
params = {
    "propertyType": "commercial",
    "listing_type": "sale",
    "district": "Central"
}

response = requests.get(url, headers=headers, params=params)
listings = response.json()
```

---

#### 4. **data.gov.sg API** ⭐ GOVERNMENT DATA
| Aspect | Details |
|--------|---------|
| **Type** | REST API with Datasets |
| **Coverage** | HDB property info, private transactions, demographics |
| **Data Points** | Transaction history (1999+), prices, project status, tenure |
| **Update Frequency** | Quarterly |
| **Authentication** | No key required (public) |
| **Tech Stack** | REST API |
| **Cost** | Free |
| **Effort** | Low (3-4 hours) |
| **Integration** | Phase 1 (Secondary) |
| **Link** | https://data.gov.sg/datasets |

**Key Datasets**:
- Private Residential Property Transactions (whole of Singapore)
- HDB Property Information
- Property Market Indicators
- Planning & Development Data

**Sample Query**:
```python
import requests

# Get residential transaction data
url = "https://data.gov.sg/api/action/datastore_search"
params = {
    "resource_id": "d_7c69c943d5f0d89d6a9a773d2b51f337",  # Transactions dataset
    "limit": 100
}

response = requests.get(url, params=params)
transactions = response.json()['records']
```

---

### 🟠 TIER 2: High Priority (Phase 2)

#### 5. **EdgeProp** 🏢 COMMERCIAL FOCUS
| Aspect | Details |
|--------|---------|
| **Type** | Web Scraper / Apify Integration |
| **Coverage** | Strong on commercial & industrial properties |
| **Data Points** | Listings, prices, agents, building specs, tenure |
| **Apify API** | Ready-made scraper available |
| **Cost** | ~$1.50/1000 listings via Apify OR free if self-built |
| **Effort** | Low-Medium (8-12 hours for custom scraper) |
| **Integration** | Phase 2 Priority 1 |
| **Link** | https://edgeprop.sg |

**Two Approaches**:

**Option A: Apify Integration (Easiest, Paid)**
```python
import requests

# Use Apify's EdgeProp scraper
apify_url = "https://api.apify.com/v2/acts/rl1987/edgeprop-sg-api-scraper/run-sync"
payload = {
    "pageUrl": "https://edgeprop.sg/...",
    "searchQuery": "B1 industrial"
}
response = requests.post(apify_url, json=payload, auth=(token, ""))
```

**Option B: Custom Selenium Scraper (Recommended)**
- Cost: Free
- Time: 10-15 hours
- Benefits: Full control, no dependencies

---

#### 6. **CBRE Singapore** 🏢 PREMIUM COMMERCIAL
| Aspect | Details |
|--------|---------|
| **Type** | Web Scraper |
| **Coverage** | Office, retail, industrial, logistics |
| **Data Points** | High-end properties, tenant info, lease terms |
| **Website** | https://www.cbre.com.sg/properties |
| **Tech Stack** | Selenium + BeautifulSoup |
| **Cost** | Free |
| **Effort** | Medium (12-15 hours) |
| **Integration** | Phase 2 |
| **Legal** | ✅ Check ToS; brokers often appreciate data sharing partnerships |

**Scraping Strategy**:
- Target: `.property-listing`, `.property-price`, `.property-agent`
- Parse XHR requests for JSON data (more efficient than HTML)
- Deduplication on property_id or (address + price combination)

---

#### 7. **JLL Singapore** 🏢 COMMERCIAL BROKER
| Aspect | Details |
|--------|---------|
| **Type** | Web Scraper |
| **Coverage** | Commercial leasing and investment sales |
| **Website** | https://www.jll.com.sg / https://property.jll.com.sg |
| **Cost** | Free |
| **Effort** | Medium (10-12 hours) |
| **Integration** | Phase 2 |

**Integration Pattern**: Similar to CBRE - parse XHR network requests for JSON

---

#### 8. **Cushman & Wakefield Singapore** 🏢 COMMERCIAL BROKER
| Aspect | Details |
|--------|---------|
| **Type** | Web Scraper |
| **Coverage** | Offices, industrial, retail, business parks |
| **Website** | https://www.cushmanwakefield.com/en/singapore |
| **Cost** | Free |
| **Effort** | Medium (10-12 hours) |
| **Integration** | Phase 2 |

---

### 🟡 TIER 3: Nice-to-Have (Phase 3+)

#### 9. **News APIs for Building-Specific Intelligence**
| Source | Type | Coverage | Cost |
|--------|------|----------|------|
| **NewsAPI.org** | REST API | Global news articles | Free (500 req/day) |
| **Google News API** | RSS/API | News aggregation | Free |
| **SGBusiness Review** | Web Scraper | Local business news | Free |
| **PropertyShark Newsletter** | Email scraping | SG property updates | Free |

**Use Case**: Enrich building profiles with recent news, development updates

**Example**:
```python
# Fetch news about a specific property/building
news_url = "https://newsapi.org/v2/everything"
params = {
    "q": "Marina Bay building redevelopment",
    "sortBy": "publishedAt",
    "language": "en",
    "apiKey": NEWS_API_KEY
}
response = requests.get(news_url, params=params)
```

---

#### 10. **SRX (Singapore Real Estate Exchange)**
| Aspect | Details |
|--------|---------|
| **Type** | Web Scraper |
| **Coverage** | Residential listings (HDB, condo), some commercial |
| **Website** | https://www.srx.com.sg |
| **Note** | No public API; scraping required |
| **Cost** | Free |
| **Effort** | Medium (12-15 hours) |
| **Status** | Phase 3+ (Lower priority for commercial focus) |

---

## Integration Roadmap

### Phase 1: Foundation (Weeks 1-2) ⏳ CURRENT

**Must-Have**:
- ✅ PropertyGuru scraper (basic)
- ✅ URA API integration
- ✅ 99.co API integration
- ✅ data.gov.sg import
- ✅ Database schema & Fly.io PostgreSQL
- ✅ Basic REST API endpoints

**Effort**: ~40-50 hours  
**Data Volume**: ~10,000 active listings, historical transactions

---

### Phase 2: Commercial Focus (Weeks 3-4) ⏳ NEXT

**Additions**:
- [ ] EdgeProp scraper
- [ ] CBRE scraper
- [ ] JLL scraper
- [ ] Cushman & Wakefield scraper
- [ ] Data validation & deduplication pipeline
- [ ] Price history tracking

**Effort**: ~60-80 hours  
**Data Volume**: ~20,000+ active listings, 5+ years history

---

### Phase 3: Intelligence & Scale (Weeks 5-6+) 🎯 FUTURE

**Additions**:
- [ ] News/article aggregation
- [ ] Building profile enrichment
- [ ] Alert system
- [ ] Investment scoring algorithm
- [ ] Dashboard visualization
- [ ] Real-time notifications

---

## Technical Implementation Matrix

| Source | Scraper Type | Frequency | Dedup Strategy | Storage | Alerts |
|--------|--------------|-----------|----------------|---------|--------|
| PropertyGuru | Selenium | Hourly | Hash + ML | PostgreSQL | New listings |
| EdgeProp | Selenium | Daily | Hash | PostgreSQL | Price changes |
| URA API | Direct API | Daily | API ID | PostgreSQL | N/A (official) |
| 99.co API | REST API | Daily | API ID | PostgreSQL | New projects |
| CBRE | Selenium | Daily | Hash | PostgreSQL | New properties |
| JLL | Selenium | Daily | Hash | PostgreSQL | New properties |
| Cushman & Wakefield | Selenium | Daily | Hash | PostgreSQL | New properties |
| News APIs | REST API | Hourly | Content hash | PostgreSQL | Relevant news |
| data.gov.sg | REST API | Weekly | Timestamp | PostgreSQL | N/A |
| SRX | Selenium | Daily | Hash | PostgreSQL | Phase 3+ |

---

## Data Quality & Deduplication Strategy

### Hashing Approach
```python
import hashlib
import json

def generate_listing_hash(listing: dict) -> str:
    """
    Generate unique hash for deduplication
    Uses normalized address + price + property type
    """
    key_fields = {
        'address': normalize_address(listing['address']),
        'price': int(listing['price'] / 1000) * 1000,  # Round to nearest 1K
        'property_type': listing['property_type'],
        'size': int(listing['size'] / 100) * 100  # Round to nearest 100 sqft
    }
    hash_input = json.dumps(key_fields, sort_keys=True)
    return hashlib.sha256(hash_input.encode()).hexdigest()
```

### Validation Rules
1. **Price validation**: Within 20% of median for location/type
2. **Address validation**: Must match known Singapore postcodes
3. **Contact validation**: Agent phone must be valid SG format
4. **Temporal validation**: Listing date cannot be in future

---

## Cost Estimation

| Source | Setup Cost | Monthly Cost | Data Cost | Total Year 1 |
|--------|-----------|--------------|-----------|-------------|
| PropertyGuru | 0 | 0 | 0 | $0 |
| EdgeProp | 0 | 0 | 0 | $0 |
| URA | 0 | 0 | 0 | $0 |
| 99.co (free tier) | 0 | 0 | 0 | $0 |
| data.gov.sg | 0 | 0 | 0 | $0 |
| CBRE | 0 | 0 | 0 | $0 |
| JLL | 0 | 0 | 0 | $0 |
| Cushman & Wakefield | 0 | 0 | 0 | $0 |
| NewsAPI | 0 | 0 | 0 | $0 |
| SRX | 0 | 0 | 0 | $0 |
| **Infrastructure** | $50 | $20 | 0 | $290 |
| **TOTAL** | **$50** | **$20** | **$0** | **$290** |

*Note: Fly.io PostgreSQL ~$20/month (starter plan). All data sources are free!*

---

## Legal & Ethical Checklist

- [ ] Check robots.txt for each domain
- [ ] Implement respectful rate limiting (3-5 sec between requests)
- [ ] Use rotating user agents
- [ ] Add exponential backoff for 429/503 responses
- [ ] Cache results to minimize re-requests
- [ ] Review Terms of Service for each source
- [ ] Consider reaching out to brokers (CBRE, JLL, C&W) for partnerships
- [ ] Implement data retention policies (auto-archive after 2 years)
- [ ] Get legal review for data usage (not for redistribution)

---

## Performance Targets

| Metric | Target | Method |
|--------|--------|--------|
| Daily scrape time | <2 hours | Parallel jobs (3-5 concurrent) |
| Data freshness | <24 hours | Hourly new listings check |
| Deduplication accuracy | >98% | ML-enhanced hashing |
| Data quality score | >95% | Validation pipeline |
| API uptime | >99.5% | Health checks + monitoring |
| Query response time | <500ms | Redis caching + indexing |

---

## Next Steps

1. **Immediate** (This week):
   - [ ] Set up Fly.io PostgreSQL
   - [ ] Create database schema
   - [ ] Implement PropertyGuru scraper
   - [ ] Integrate URA API
   - [ ] Integrate 99.co API

2. **Short-term** (Week 2):
   - [ ] Complete Phase 1 data sources
   - [ ] Implement validation pipeline
   - [ ] Set up Redis caching
   - [ ] Build basic REST API

3. **Medium-term** (Weeks 3-4):
   - [ ] Add EdgeProp, CBRE, JLL scrapers
   - [ ] Implement price history tracking
   - [ ] Set up alert system
   - [ ] Build analytics dashboard

---

## Research Sources

1. **PropertyGuru**: https://www.propertyguru.com.sg
2. **EdgeProp**: https://edgeprop.sg
3. **99.co API**: https://rapidapi.com/99co-official/api/99-co-sg
4. **URA Data Service**: https://www.ura.gov.sg/maps/?service=dataservice
5. **data.gov.sg**: https://data.gov.sg
6. **CBRE**: https://www.cbre.com.sg
7. **JLL**: https://www.jll.com.sg
8. **Cushman & Wakefield**: https://www.cushmanwakefield.com/en/singapore
9. **NewsAPI**: https://newsapi.org
10. **SRX**: https://www.srx.com.sg

---

**Status**: ✅ Research Complete | Phase 1 Ready to Start  
**Last Updated**: 2026-10-04 @ 15:58 SGT

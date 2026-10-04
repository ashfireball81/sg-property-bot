# SG Property Digital Twin Bot

Real-time commercial & industrial property intelligence system for Singapore (B1/B2 units). Tracks listings, prices, market trends, and building profiles across multiple sources.

## Features

- **Multi-Source Data Aggregation**: PropertyGuru, EdgeProp, 99.co, URA, CBRE, JLL, Cushman & Wakefield
- **Real-Time Monitoring**: Automated daily/hourly scraping and updates
- **Intelligent Alerts**: Price changes, new listings, market opportunities
- **Historical Analytics**: 2+ years of price tracking and trend analysis
- **Building Profiles**: Tenure, age, nearby infrastructure, tenant mix
- **Investment Scoring**: AI-powered opportunity ranking

## Tech Stack

- **Scraper**: Python (Selenium, BeautifulSoup, APScheduler)
- **API**: Node.js + Express + TypeScript
- **Database**: PostgreSQL on Fly.io
- **Cache**: Redis
- **Frontend**: React (Phase 2)

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Git

### Installation

```bash
# Clone and setup
git clone <repository>
cd sg-property-bot

# Setup Python scraper
cd scraper
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt

# Setup Node.js API
cd ../api
npm install

# Setup database
cd ../database
# Configure .env and run migrations
```

### Configuration

1. Copy `.env.example` to `.env`
2. Configure API keys and database URLs
3. Set up URA Data Service access (free registration)
4. Configure 99.co API key (via RapidAPI)

### Running

```bash
# Terminal 1: Start scraper
cd scraper
python main.py

# Terminal 2: Start API server
cd api
npm run dev

# Terminal 3: Monitor logs
tail -f logs/app.log
```

## Data Sources

| Source | Type | Coverage | Status |
|--------|------|----------|--------|
| PropertyGuru | Scraper | All property types | ✅ Priority |
| EdgeProp | Scraper | Commercial/Industrial focus | ✅ Phase 1 |
| 99.co | API (RapidAPI) | Commercial + residential | ✅ Phase 1 |
| URA | Free API | Transactions, official data | ✅ Phase 1 |
| CBRE | Scraper | Premium commercial | 🟡 Phase 2 |
| JLL | Scraper | Commercial brokers | 🟡 Phase 2 |
| Cushman & Wakefield | Scraper | Commercial brokers | 🟡 Phase 2 |
| data.gov.sg | API | Government datasets | ✅ Phase 1 |
| News APIs | API | Building-specific news | 🟡 Phase 2 |

## Project Structure

```
sg-property-bot/
├── scraper/              # Python data collection
│   ├── scrapers/         # Individual scrapers (PropertyGuru, EdgeProp, etc)
│   ├── validators/       # Data validation & deduplication
│   ├── utils/            # Helper functions
│   └── main.py           # ETL orchestrator
├── api/                  # Node.js REST API
│   ├── src/
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── models/       # Database models
│   │   └── middleware/   # Auth, validation, etc
│   └── server.ts         # Express app
├── database/             # Schema & migrations
│   ├── migrations/       # Flyway/Knex migrations
│   └── seeds/            # Sample data
├── config/               # Configuration files
├── tests/                # Test suites
└── .github/              # GitHub workflows & docs
```

## Development Roadmap

### Phase 1: Core Infrastructure (Weeks 1-2)
- [x] Project setup and scaffolding
- [x] Data source research & mapping
- [ ] Database schema & Fly.io setup
- [ ] URA API integration
- [ ] 99.co API integration
- [ ] PropertyGuru scraper (basic)
- [ ] Basic REST API endpoints

### Phase 2: Data Accumulation (Weeks 3-4)
- [ ] EdgeProp scraper
- [ ] Data validation & deduplication pipeline
- [ ] Price history tracking
- [ ] Agent database building
- [ ] Historical data backfill

### Phase 3: Intelligence & Alerts (Weeks 5-6)
- [ ] Alert system (price changes, new listings)
- [ ] Building profile enrichment
- [ ] News/article aggregation
- [ ] Investment opportunity scoring
- [ ] Trend analysis dashboard

### Phase 4: Scale & Optimize (Weeks 7+)
- [ ] React dashboard
- [ ] Real-time notifications (Email/SMS)
- [ ] Performance optimization
- [ ] Multi-market expansion
- [ ] Machine learning predictions

## API Endpoints (Phase 1)

```
GET    /api/properties              # List all tracked properties
GET    /api/properties/:id          # Get property details
GET    /api/listings                # Active listings
GET    /api/listings/new            # New listings (last 24h)
GET    /api/prices/trends/:id       # Price history
GET    /api/agents                  # Agent directory
GET    /api/alerts                  # Active alerts
POST   /api/alerts                  # Create alert
```

## Data Models

### Properties Table
- UUID, name, address, postcode, property_type
- land_area, plot_size, age_built, tenure, remaining_years
- latest_price, created_at, updated_at

### Listings Table
- property_id, listing_source, listing_type, price, price_per_sqft
- unit_count, agent_id, listing_date, status, scraped_at

### Price History (Time-Series)
- property_id, date, avg_price, min_price, max_price, active_listings_count

### Building Profiles
- property_id, description, amenities, nearby_mrt, tenant_mix, owner_info

## Testing

```bash
# Run all tests
npm run test

# Run with coverage
npm run test:coverage

# Run scraper tests
cd scraper && pytest tests/
```

## Deployment

```bash
# Deploy to Fly.io
flyctl deploy

# Monitor logs
flyctl logs

# Scale resources
flyctl scale vm=shared-cpu-2x
```

## Legal & Ethical Guidelines

- ✅ Respect robots.txt and rate limits
- ✅ Use official APIs when available
- ✅ Check Terms of Service for each data source
- ✅ Consider reaching out to sources for partnerships
- ✅ Implement exponential backoff for retries
- ✅ Rotate user agents and add delays

## Contributing

1. Create feature branch (`git checkout -b feature/xyz`)
2. Commit changes (`git commit -am 'Add xyz'`)
3. Push to branch (`git push origin feature/xyz`)
4. Create Pull Request

## License

MIT License - See LICENSE file

## Support & Contact

For issues, questions, or partnership inquiries:
- GitHub Issues: [Create an issue]
- Email: [Your email]

---

**Last Updated**: 2026-10-04  
**Status**: 🟡 In Development (Phase 1)

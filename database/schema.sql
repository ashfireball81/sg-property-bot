-- SG Property Digital Twin Bot - Database Schema
-- PostgreSQL Schema for Property Intelligence

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- ============================================================
-- PROPERTIES TABLE - Core property records
-- ============================================================
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Basic Information
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500) NOT NULL UNIQUE,
    postcode VARCHAR(10) NOT NULL,
    region VARCHAR(100),
    
    -- Property Classification
    property_type VARCHAR(50) NOT NULL,  -- B1, B2, Office, Retail, Industrial, etc
    sub_type VARCHAR(100),
    
    -- Physical Details
    land_area DECIMAL(12, 2),  -- in sqft
    building_area DECIMAL(12, 2),  -- in sqft
    plot_size DECIMAL(12, 2),  -- in sqft
    floor_count INT,
    unit_count INT,
    year_built INT,
    
    -- Tenure Information
    tenure_type VARCHAR(50),  -- Freehold, Leasehold_99yr, etc
    tenure_end_date DATE,
    remaining_years INT GENERATED ALWAYS AS (
        EXTRACT(YEAR FROM tenure_end_date) - EXTRACT(YEAR FROM CURRENT_DATE)
    ) STORED,
    
    -- Market Information
    latest_price DECIMAL(15, 2),
    price_per_sqft DECIMAL(10, 2),
    latest_rental DECIMAL(15, 2),
    rental_per_sqft DECIMAL(10, 2),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scraped_at TIMESTAMP,
    scraped_source VARCHAR(100),  -- PropertyGuru, EdgeProp, etc
    
    -- Indexing
    CONSTRAINT valid_tenure_type CHECK (tenure_type IN ('Freehold', 'Leasehold_99yr', 'Leasehold_60yr', 'Others')),
    CONSTRAINT valid_property_type CHECK (property_type IN ('B1', 'B2', 'Office', 'Retail', 'Industrial', 'Logistics', 'Conservation', 'Mixed'))
);

CREATE INDEX idx_properties_address ON properties(address);
CREATE INDEX idx_properties_postcode ON properties(postcode);
CREATE INDEX idx_properties_property_type ON properties(property_type);
CREATE INDEX idx_properties_latest_price ON properties(latest_price);
CREATE INDEX idx_properties_created_at ON properties(created_at);
CREATE INDEX idx_properties_address_gin ON properties USING GIN(address gin_trgm_ops);  -- Text search

-- ============================================================
-- LISTINGS TABLE - Active and historical listings
-- ============================================================
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- References
    property_id UUID NOT NULL,
    agent_id UUID,
    
    -- Listing Information
    listing_source VARCHAR(100) NOT NULL,  -- PropertyGuru, EdgeProp, 99.co, etc
    listing_url TEXT,
    listing_external_id VARCHAR(200),  -- ID from source
    
    -- Listing Details
    listing_type VARCHAR(50) NOT NULL,  -- Sale, Rental, Auction, Lease
    listing_sub_type VARCHAR(100),
    price DECIMAL(15, 2),
    price_per_sqft DECIMAL(10, 2),
    rental_price DECIMAL(15, 2),
    unit_size DECIMAL(10, 2),
    unit_count INT,
    
    -- Status & Dates
    status VARCHAR(50) DEFAULT 'active',  -- active, sold, withdrawn, expired, leased
    listing_date DATE NOT NULL,
    last_updated DATE,
    sold_date DATE,
    
    -- Description
    description TEXT,
    features TEXT,  -- JSON array
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scraped_at TIMESTAMP,
    data_hash VARCHAR(64),  -- SHA256 for deduplication
    
    FOREIGN KEY(property_id) REFERENCES properties(id) ON DELETE CASCADE,
    FOREIGN KEY(agent_id) REFERENCES agents(id) ON DELETE SET NULL,
    CONSTRAINT valid_listing_type CHECK (listing_type IN ('Sale', 'Rental', 'Auction', 'Lease')),
    CONSTRAINT valid_listing_status CHECK (status IN ('active', 'sold', 'withdrawn', 'expired', 'leased'))
);

CREATE INDEX idx_listings_property_id ON listings(property_id);
CREATE INDEX idx_listings_agent_id ON listings(agent_id);
CREATE INDEX idx_listings_source ON listings(listing_source);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_listing_date ON listings(listing_date DESC);
CREATE INDEX idx_listings_price ON listings(price);
CREATE INDEX idx_listings_data_hash ON listings(data_hash);

-- ============================================================
-- AGENTS TABLE - Real estate agents directory
-- ============================================================
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Contact Information
    name VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    license_number VARCHAR(100),
    
    -- Profile
    url TEXT,
    profile_image_url TEXT,
    bio TEXT,
    
    -- Statistics
    listings_count INT DEFAULT 0,
    sold_count INT DEFAULT 0,
    rating DECIMAL(3, 2),  -- Out of 5
    reviews_count INT DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    external_id VARCHAR(200),
    external_source VARCHAR(100),
    
    CONSTRAINT valid_rating CHECK (rating >= 0 AND rating <= 5)
);

CREATE INDEX idx_agents_name ON agents(name);
CREATE INDEX idx_agents_company ON agents(company);
CREATE INDEX idx_agents_email ON agents(email);
CREATE INDEX idx_agents_phone ON agents(phone);

-- ============================================================
-- PRICE_HISTORY TABLE - Time-series price tracking
-- ============================================================
CREATE TABLE price_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- References
    property_id UUID NOT NULL,
    
    -- Price Data
    record_date DATE NOT NULL,
    avg_price DECIMAL(15, 2),
    min_price DECIMAL(15, 2),
    max_price DECIMAL(15, 2),
    median_price DECIMAL(15, 2),
    price_per_sqft DECIMAL(10, 2),
    
    -- Listing Stats
    active_listings_count INT,
    new_listings_count INT,
    sold_count INT,
    
    -- Rental Data
    avg_rental DECIMAL(15, 2),
    rental_per_sqft DECIMAL(10, 2),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100),  -- Aggregated from which sources
    
    FOREIGN KEY(property_id) REFERENCES properties(id) ON DELETE CASCADE,
    UNIQUE(property_id, record_date)
);

CREATE INDEX idx_price_history_property_id ON price_history(property_id);
CREATE INDEX idx_price_history_record_date ON price_history(record_date DESC);
CREATE INDEX idx_price_history_property_date ON price_history(property_id, record_date DESC);

-- ============================================================
-- BUILDING_PROFILES TABLE - Detailed building information
-- ============================================================
CREATE TABLE building_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- References
    property_id UUID NOT NULL UNIQUE,
    
    -- Building Details
    description TEXT,
    building_use_class VARCHAR(100),
    age_category VARCHAR(50),
    architectural_style VARCHAR(100),
    
    -- Amenities & Features
    amenities TEXT,  -- JSON array
    security_features TEXT,
    parking_spaces INT,
    loading_bay INT,
    
    -- Location Features
    nearby_mrt VARCHAR(255),
    nearby_bus_stops INT,
    nearby_schools INT,
    nearby_hospitals INT,
    nearby_shopping INT,
    walkability_score INT,  -- 0-100
    
    -- Tenant Information
    tenant_mix TEXT,  -- JSON
    major_tenants TEXT,  -- JSON array
    occupancy_rate DECIMAL(5, 2),  -- percentage
    tenant_diversity VARCHAR(100),
    
    -- Building Management
    management_company VARCHAR(255),
    management_contact VARCHAR(100),
    sinking_fund DECIMAL(15, 2),
    maintenance_cost_per_sqft DECIMAL(10, 2),
    
    -- Environmental & Sustainability
    green_building_cert VARCHAR(100),  -- BCA, LEED, etc
    energy_efficiency_rating VARCHAR(10),
    renewable_energy BOOLEAN,
    
    -- Photos & Media
    photos_urls TEXT,  -- JSON array
    video_url TEXT,
    virtual_tour_url TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified_at TIMESTAMP,
    
    FOREIGN KEY(property_id) REFERENCES properties(id) ON DELETE CASCADE
);

CREATE INDEX idx_building_profiles_property_id ON building_profiles(property_id);

-- ============================================================
-- TRANSACTIONS TABLE - Historical sales and rentals
-- ============================================================
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- References
    property_id UUID NOT NULL,
    agent_id UUID,
    
    -- Transaction Details
    transaction_type VARCHAR(50) NOT NULL,  -- Sale, Rental, Lease
    transaction_date DATE NOT NULL,
    
    -- Pricing
    transaction_price DECIMAL(15, 2),
    price_per_sqft DECIMAL(10, 2),
    
    -- Details
    unit_size DECIMAL(10, 2),
    unit_floor INT,
    unit_number VARCHAR(50),
    buyer_profile VARCHAR(100),  -- Individual, Developer, Institution
    tenure_at_transaction VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(100),
    external_id VARCHAR(200),
    
    FOREIGN KEY(property_id) REFERENCES properties(id) ON DELETE CASCADE,
    FOREIGN KEY(agent_id) REFERENCES agents(id) ON DELETE SET NULL,
    CONSTRAINT valid_transaction_type CHECK (transaction_type IN ('Sale', 'Rental', 'Lease'))
);

CREATE INDEX idx_transactions_property_id ON transactions(property_id);
CREATE INDEX idx_transactions_transaction_date ON transactions(transaction_date DESC);
CREATE INDEX idx_transactions_agent_id ON transactions(agent_id);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);

-- ============================================================
-- ARTICLES TABLE - News and articles about properties
-- ============================================================
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- References
    property_id UUID,  -- NULL if general market article
    
    -- Article Content
    title VARCHAR(500) NOT NULL,
    content TEXT,
    summary TEXT,
    url TEXT NOT NULL,
    source VARCHAR(100),
    source_name VARCHAR(255),
    
    -- Categorization
    category VARCHAR(100),  -- News, Development, Market, Redevelopment
    sentiment VARCHAR(50),  -- Positive, Neutral, Negative
    keywords TEXT,  -- JSON array
    
    -- Dates
    published_date TIMESTAMP,
    fetched_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Images
    image_url TEXT,
    
    FOREIGN KEY(property_id) REFERENCES properties(id) ON DELETE SET NULL
);

CREATE INDEX idx_articles_property_id ON articles(property_id);
CREATE INDEX idx_articles_published_date ON articles(published_date DESC);
CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_articles_category ON articles(category);

-- ============================================================
-- ALERTS TABLE - User alerts and monitoring
-- ============================================================
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Alert Trigger
    alert_type VARCHAR(100),  -- PriceChange, NewListing, PriceThreshold, SoldAlert
    property_id UUID,
    
    -- Conditions
    trigger_value DECIMAL(15, 2),  -- Price threshold, change percentage, etc
    condition_met BOOLEAN DEFAULT FALSE,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active',  -- active, triggered, acknowledged, inactive
    is_triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(property_id) REFERENCES properties(id) ON DELETE CASCADE,
    CONSTRAINT valid_alert_type CHECK (alert_type IN ('PriceChange', 'NewListing', 'PriceThreshold', 'SoldAlert')),
    CONSTRAINT valid_alert_status CHECK (status IN ('active', 'triggered', 'acknowledged', 'inactive'))
);

CREATE INDEX idx_alerts_property_id ON alerts(property_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);

-- ============================================================
-- DATA_SYNC_LOG TABLE - Track scraping/import operations
-- ============================================================
CREATE TABLE data_sync_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Sync Details
    sync_source VARCHAR(100) NOT NULL,  -- PropertyGuru, EdgeProp, URA, etc
    sync_type VARCHAR(50),  -- Full, Incremental
    
    -- Results
    records_processed INT,
    records_inserted INT,
    records_updated INT,
    records_failed INT,
    
    -- Status
    status VARCHAR(50),  -- Success, Partial, Failed
    error_message TEXT,
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_data_sync_log_source ON data_sync_log(sync_source);
CREATE INDEX idx_data_sync_log_started_at ON data_sync_log(started_at DESC);

-- ============================================================
-- VIEWS - Useful aggregations
-- ============================================================

-- Active Listings View
CREATE VIEW active_listings_view AS
SELECT 
    p.id,
    p.name,
    p.address,
    p.postcode,
    p.property_type,
    COUNT(l.id) as listing_count,
    AVG(l.price) as avg_price,
    MIN(l.price) as min_price,
    MAX(l.price) as max_price,
    p.updated_at
FROM properties p
LEFT JOIN listings l ON p.id = l.property_id AND l.status = 'active'
GROUP BY p.id, p.name, p.address, p.postcode, p.property_type, p.updated_at;

-- Price Trend View (last 12 months)
CREATE VIEW price_trends_12m AS
SELECT
    property_id,
    record_date,
    avg_price,
    price_per_sqft,
    LAG(avg_price) OVER (PARTITION BY property_id ORDER BY record_date) as prev_price,
    (avg_price - LAG(avg_price) OVER (PARTITION BY property_id ORDER BY record_date)) / 
    LAG(avg_price) OVER (PARTITION BY property_id ORDER BY record_date) * 100 as price_change_pct
FROM price_history
WHERE record_date >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY property_id, record_date DESC;

-- Agent Performance View
CREATE VIEW agent_performance_view AS
SELECT
    a.id,
    a.name,
    a.company,
    COUNT(l.id) as total_listings,
    COUNT(CASE WHEN l.status = 'sold' THEN 1 END) as sold_count,
    AVG(l.price) as avg_listing_price,
    a.rating,
    a.reviews_count
FROM agents a
LEFT JOIN listings l ON a.id = l.agent_id
GROUP BY a.id, a.name, a.company, a.rating, a.reviews_count;

-- ============================================================
-- TRIGGERS - Automatic updates
-- ============================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER properties_update_timestamp
BEFORE UPDATE ON properties
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER listings_update_timestamp
BEFORE UPDATE ON listings
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER agents_update_timestamp
BEFORE UPDATE ON agents
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER alerts_update_timestamp
BEFORE UPDATE ON alerts
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- ============================================================
-- Seed data (Optional - for testing)
-- ============================================================
-- INSERT INTO properties (name, address, postcode, property_type, land_area, year_built, tenure_type, latest_price)
-- VALUES (
--     'Marina Bay Financial Centre',
--     '8 Marina Boulevard, Singapore 018981',
--     '018981',
--     'Office',
--     NULL,
--     2011,
--     'Freehold',
--     500000000
-- );

-- ============================================================
-- Performance Optimization Settings
-- ============================================================

-- Analyze tables for query planner
ANALYZE properties;
ANALYZE listings;
ANALYZE price_history;
ANALYZE agents;
ANALYZE transactions;
ANALYZE articles;
ANALYZE alerts;

-- Set statistics target for better query plans
ALTER TABLE properties ALTER COLUMN price_per_sqft SET STATISTICS 100;
ALTER TABLE listings ALTER COLUMN price SET STATISTICS 100;
ALTER TABLE price_history ALTER COLUMN record_date SET STATISTICS 100;

-- ============================================================
-- Schema Version
-- ============================================================
-- Version: 1.0.0
-- Created: 2026-10-04
-- Last Modified: 2026-10-04

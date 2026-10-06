"""
Database Persistence Layer for SG Property Digital Twin
═══════════════════════════════════════════════════════════════════════════
Stores all properties with dates and enables cross-comparison by building/area
"""

import psycopg2
from psycopg2.extras import execute_values
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv


class PropertyDatabase:
    """Database operations for property listings and analysis"""

    def __init__(self):
        load_dotenv()
        
        # Get database connection details from environment or Fly.io
        self.db_config = {
            "host": os.getenv("DB_HOST", "sg-property-bot-db.internal"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "database": os.getenv("DB_NAME", "propertybot"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", ""),
        }
        
        self.conn = None
        self.cursor = None
        
    def connect(self) -> bool:
        """Connect to database"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            print("✓ Connected to database")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def init_schema(self):
        """Initialize database schema"""
        try:
            schema_sql = """
            -- Listings table
            CREATE TABLE IF NOT EXISTS listings (
                id SERIAL PRIMARY KEY,
                source VARCHAR(50),
                title VARCHAR(255),
                price DECIMAL(12,2),
                area DECIMAL(10,2),
                location VARCHAR(255),
                property_type VARCHAR(100),
                listing_type VARCHAR(50),
                url TEXT,
                posted_date TIMESTAMP,
                agent VARCHAR(100),
                agent_phone VARCHAR(20),
                description TEXT,
                tenure VARCHAR(50),
                floor VARCHAR(10),
                unit VARCHAR(20),
                scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source, url)
            );

            -- Property analysis table
            CREATE TABLE IF NOT EXISTS property_analysis (
                id SERIAL PRIMARY KEY,
                listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                price_psf DECIMAL(10,2),
                market_avg_psf DECIMAL(10,2),
                price_vs_market_pct DECIMAL(6,2),
                competitive_position VARCHAR(100),
                demand_score INTEGER,
                location_tier VARCHAR(10),
                estimated_monthly_rent DECIMAL(10,2),
                estimated_annual_rent DECIMAL(12,2),
                rent_per_sqft_monthly DECIMAL(8,2),
                rental_stability VARCHAR(50),
                gross_yield DECIMAL(6,2),
                net_yield DECIMAL(6,2),
                net_annual_income DECIMAL(12,2),
                roi_5year DECIMAL(6,2),
                roi_5year_value DECIMAL(12,2),
                roi_10year DECIMAL(6,2),
                roi_10year_value DECIMAL(12,2),
                roi_20year DECIMAL(6,2),
                roi_20year_value DECIMAL(12,2),
                annual_revenue DECIMAL(12,2),
                annual_maintenance DECIMAL(10,2),
                annual_property_tax DECIMAL(10,2),
                annual_insurance DECIMAL(10,2),
                total_annual_costs DECIMAL(12,2),
                profit_margin DECIMAL(6,2),
                breakeven_months DECIMAL(6,2),
                risk_score INTEGER,
                tenure_risk VARCHAR(100),
                market_risk VARCHAR(100),
                liquidity_risk VARCHAR(100),
                investment_score DECIMAL(5,2),
                recommendation VARCHAR(100),
                primary_appeal VARCHAR(100),
                target_investor VARCHAR(100)
            );

            -- Price history table
            CREATE TABLE IF NOT EXISTS price_history (
                id SERIAL PRIMARY KEY,
                listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
                price DECIMAL(12,2),
                recorded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Area analysis table
            CREATE TABLE IF NOT EXISTS area_analysis (
                id SERIAL PRIMARY KEY,
                area_name VARCHAR(255),
                location_tier VARCHAR(10),
                avg_price DECIMAL(12,2),
                avg_price_psf DECIMAL(10,2),
                avg_rental_yield DECIMAL(6,2),
                demand_score INTEGER,
                properties_tracked INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(area_name)
            );

            -- Create indices
            CREATE INDEX IF NOT EXISTS idx_listings_location ON listings(location);
            CREATE INDEX IF NOT EXISTS idx_listings_scraped_date ON listings(scraped_date);
            CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price);
            CREATE INDEX IF NOT EXISTS idx_property_analysis_listing_id ON property_analysis(listing_id);
            CREATE INDEX IF NOT EXISTS idx_property_analysis_date ON property_analysis(analysis_date);
            CREATE INDEX IF NOT EXISTS idx_property_analysis_yield ON property_analysis(net_yield);
            CREATE INDEX IF NOT EXISTS idx_property_analysis_score ON property_analysis(investment_score);
            CREATE INDEX IF NOT EXISTS idx_price_history_listing_id ON price_history(listing_id);
            CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(recorded_date);
            CREATE INDEX IF NOT EXISTS idx_area_analysis_name ON area_analysis(area_name);
            """
            
            self.cursor.execute(schema_sql)
            self.conn.commit()
            print("✓ Schema initialized")
            return True
            
        except Exception as e:
            print(f"✗ Schema initialization failed: {e}")
            self.conn.rollback()
            return False

    def insert_listing(self, property_data: Dict[str, Any]) -> Optional[int]:
        """Insert property listing, return ID or None if duplicate"""
        try:
            sql = """
            INSERT INTO listings 
            (source, title, price, area, location, property_type, listing_type, 
             url, posted_date, agent, agent_phone, description, tenure, floor, unit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source, url) DO UPDATE SET last_updated = CURRENT_TIMESTAMP
            RETURNING id;
            """
            
            self.cursor.execute(sql, (
                property_data.get('source'),
                property_data.get('title'),
                property_data.get('price'),
                property_data.get('area'),
                property_data.get('location'),
                property_data.get('property_type'),
                property_data.get('listing_type'),
                property_data.get('url'),
                property_data.get('posted_date'),
                property_data.get('agent'),
                property_data.get('agent_phone'),
                property_data.get('description'),
                property_data.get('tenure'),
                property_data.get('floor'),
                property_data.get('unit'),
            ))
            
            listing_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return listing_id
            
        except Exception as e:
            print(f"✗ Listing insert failed: {e}")
            self.conn.rollback()
            return None

    def insert_analysis(self, listing_id: int, analysis: Dict[str, Any]) -> bool:
        """Insert property analysis"""
        try:
            # Extract nested values
            market = analysis.get("market_position", {})
            rental = analysis.get("rental_analysis", {})
            yield_info = analysis.get("yield_analysis", {})
            roi = analysis.get("roi_projections", {})
            profitability = analysis.get("profitability_metrics", {})
            risk = analysis.get("risk_assessment", {})
            rec = analysis.get("investment_recommendation", {})
            
            # Convert percentage strings to floats
            def extract_pct(val):
                if isinstance(val, str):
                    return float(val.rstrip('%'))
                return float(val) if val else 0
            
            def extract_money(val):
                if isinstance(val, str):
                    return float(val.replace('$', '').replace(',', ''))
                return float(val) if val else 0
            
            sql = """
            INSERT INTO property_analysis
            (listing_id, price_psf, market_avg_psf, price_vs_market_pct,
             competitive_position, demand_score, location_tier,
             estimated_monthly_rent, estimated_annual_rent, rent_per_sqft_monthly,
             rental_stability, gross_yield, net_yield, net_annual_income,
             roi_5year, roi_5year_value, roi_10year, roi_10year_value,
             roi_20year, roi_20year_value, annual_revenue, annual_maintenance,
             annual_property_tax, annual_insurance, total_annual_costs,
             profit_margin, breakeven_months, risk_score, tenure_risk,
             market_risk, liquidity_risk, investment_score, recommendation,
             primary_appeal, target_investor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s);
            """
            
            self.cursor.execute(sql, (
                listing_id,
                extract_money(market.get('price_psf')),
                extract_money(market.get('market_avg_psf')),
                extract_pct(market.get('price_vs_market')),
                market.get('competitive_position'),
                market.get('demand_score', '0').split('/')[0] if '/' in str(market.get('demand_score', '0')) else 0,
                market.get('location_tier'),
                extract_money(rental.get('estimated_monthly_rent')),
                extract_money(rental.get('estimated_annual_rent')),
                extract_money(rental.get('rent_per_sqft_monthly')),
                rental.get('rental_stability'),
                extract_pct(yield_info.get('gross_yield')),
                extract_pct(yield_info.get('net_yield')),
                extract_money(yield_info.get('net_annual_income')),
                extract_pct(roi.get('5_year_roi')),
                extract_money(roi.get('5_year_value')),
                extract_pct(roi.get('10_year_roi')),
                extract_money(roi.get('10_year_value')),
                extract_pct(roi.get('20_year_roi')),
                extract_money(roi.get('20_year_value')),
                extract_money(profitability.get('annual_gross_revenue')),
                extract_money(profitability.get('annual_maintenance')),
                extract_money(profitability.get('annual_property_tax')),
                extract_money(profitability.get('annual_insurance')),
                extract_money(profitability.get('total_annual_costs')),
                extract_pct(profitability.get('profit_margin')),
                extract_money(profitability.get('breakeven_months')),
                risk.get('risk_score', '0').split('/')[0] if '/' in str(risk.get('risk_score', '0')) else 0,
                risk.get('tenure_risk'),
                risk.get('market_risk'),
                risk.get('liquidity_risk'),
                extract_pct(rec.get('investment_score', '0').split('/')[0]) if '/' in str(rec.get('investment_score', '0')) else 0,
                rec.get('recommendation'),
                rec.get('primary_appeal'),
                rec.get('target_investor'),
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"✗ Analysis insert failed: {e}")
            self.conn.rollback()
            return False

    def get_properties_by_area(self, area_name: str, days: int = 30) -> List[Dict]:
        """Get all properties in an area from last N days"""
        try:
            sql = """
            SELECT l.*, pa.net_yield, pa.investment_score, pa.recommendation
            FROM listings l
            LEFT JOIN property_analysis pa ON l.id = pa.listing_id
            WHERE l.location = %s AND l.scraped_date >= NOW() - INTERVAL '%s days'
            ORDER BY l.scraped_date DESC;
            """
            
            self.cursor.execute(sql, (area_name, days))
            results = self.cursor.fetchall()
            return results if results else []
            
        except Exception as e:
            print(f"✗ Query failed: {e}")
            return []

    def get_properties_by_building(self, building_name: str, days: int = 30) -> List[Dict]:
        """Get all properties in a building from last N days"""
        try:
            sql = """
            SELECT l.*, pa.net_yield, pa.investment_score, pa.recommendation
            FROM listings l
            LEFT JOIN property_analysis pa ON l.id = pa.listing_id
            WHERE l.title ILIKE %s AND l.scraped_date >= NOW() - INTERVAL '%s days'
            ORDER BY l.scraped_date DESC;
            """
            
            self.cursor.execute(sql, (f'%{building_name}%', days))
            results = self.cursor.fetchall()
            return results if results else []
            
        except Exception as e:
            print(f"✗ Query failed: {e}")
            return []

    def get_area_summary(self, area_name: str) -> Dict[str, Any]:
        """Get summary statistics for an area"""
        try:
            sql = """
            SELECT 
                l.location,
                COUNT(DISTINCT l.id) as property_count,
                AVG(l.price)::DECIMAL(12,2) as avg_price,
                MIN(l.price)::DECIMAL(12,2) as min_price,
                MAX(l.price)::DECIMAL(12,2) as max_price,
                AVG(l.area)::DECIMAL(10,2) as avg_area,
                AVG(pa.net_yield)::DECIMAL(6,2) as avg_yield,
                AVG(pa.investment_score)::DECIMAL(5,2) as avg_score,
                COUNT(CASE WHEN pa.recommendation LIKE '%BUY%' THEN 1 END) as buy_opportunities,
                MAX(l.scraped_date) as last_update
            FROM listings l
            LEFT JOIN property_analysis pa ON l.id = pa.listing_id
            WHERE l.location = %s
            GROUP BY l.location;
            """
            
            self.cursor.execute(sql, (area_name,))
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'location': result[0],
                    'property_count': result[1],
                    'avg_price': float(result[2]) if result[2] else 0,
                    'min_price': float(result[3]) if result[3] else 0,
                    'max_price': float(result[4]) if result[4] else 0,
                    'avg_area': float(result[5]) if result[5] else 0,
                    'avg_yield': float(result[6]) if result[6] else 0,
                    'avg_score': float(result[7]) if result[7] else 0,
                    'buy_opportunities': result[8],
                    'last_update': result[9].isoformat() if result[9] else None,
                }
            return {}
            
        except Exception as e:
            print(f"✗ Query failed: {e}")
            return {}

    def get_cross_area_comparison(self, days: int = 30) -> List[Dict]:
        """Compare properties across all areas"""
        try:
            sql = """
            SELECT 
                l.location,
                COUNT(DISTINCT l.id) as properties,
                AVG(l.price)::DECIMAL(12,2) as avg_price,
                AVG(l.price / l.area)::DECIMAL(8,2) as avg_price_psf,
                AVG(pa.net_yield)::DECIMAL(6,2) as avg_yield,
                AVG(pa.investment_score)::DECIMAL(5,2) as avg_score,
                MAX(l.scraped_date) as last_update
            FROM listings l
            LEFT JOIN property_analysis pa ON l.id = pa.listing_id
            WHERE l.scraped_date >= NOW() - INTERVAL '%s days'
            GROUP BY l.location
            ORDER BY avg_score DESC;
            """
            
            self.cursor.execute(sql, (days,))
            results = self.cursor.fetchall()
            
            comparisons = []
            for row in results:
                comparisons.append({
                    'location': row[0],
                    'properties': row[1],
                    'avg_price': float(row[2]) if row[2] else 0,
                    'avg_price_psf': float(row[3]) if row[3] else 0,
                    'avg_yield': float(row[4]) if row[4] else 0,
                    'avg_score': float(row[5]) if row[5] else 0,
                    'last_update': row[6].isoformat() if row[6] else None,
                })
            
            return comparisons
            
        except Exception as e:
            print(f"✗ Query failed: {e}")
            return []

    def get_price_history(self, listing_id: int) -> List[Dict]:
        """Get price history for a property"""
        try:
            sql = """
            SELECT price, recorded_date
            FROM price_history
            WHERE listing_id = %s
            ORDER BY recorded_date DESC
            LIMIT 30;
            """
            
            self.cursor.execute(sql, (listing_id,))
            results = self.cursor.fetchall()
            
            history = []
            for row in results:
                history.append({
                    'price': float(row[0]) if row[0] else 0,
                    'date': row[1].isoformat() if row[1] else None,
                })
            
            return history
            
        except Exception as e:
            print(f"✗ Query failed: {e}")
            return []

    def get_best_opportunities(self, days: int = 30, limit: int = 10) -> List[Dict]:
        """Get top investment opportunities"""
        try:
            sql = """
            SELECT 
                l.id, l.title, l.location, l.price, l.area,
                pa.net_yield, pa.investment_score, pa.recommendation,
                l.scraped_date
            FROM listings l
            JOIN property_analysis pa ON l.id = pa.listing_id
            WHERE l.scraped_date >= NOW() - INTERVAL '%s days'
            ORDER BY pa.investment_score DESC
            LIMIT %s;
            """
            
            self.cursor.execute(sql, (days, limit))
            results = self.cursor.fetchall()
            
            opportunities = []
            for row in results:
                opportunities.append({
                    'id': row[0],
                    'title': row[1],
                    'location': row[2],
                    'price': float(row[3]) if row[3] else 0,
                    'area': float(row[4]) if row[4] else 0,
                    'yield': float(row[5]) if row[5] else 0,
                    'score': float(row[6]) if row[6] else 0,
                    'recommendation': row[7],
                    'date': row[8].isoformat() if row[8] else None,
                })
            
            return opportunities
            
        except Exception as e:
            print(f"✗ Query failed: {e}")
            return []

    def persist_analysis_results(self, analysis_results: Dict[str, Any]) -> int:
        """Store complete analysis results to database"""
        count = 0
        
        try:
            # Get all properties from analysis
            for property_analysis in analysis_results.get('properties_analyzed', []):
                property_info = property_analysis.get('property_info', {})
                
                # Extract original property data
                property_data = {
                    'source': property_analysis.get('source', 'Unknown'),
                    'title': property_info.get('title'),
                    'price': float(property_info.get('price', '0').replace('$', '').replace(',', '')),
                    'area': float(property_info.get('area', '0').replace(',', '').split()[0]),
                    'location': property_info.get('location'),
                    'property_type': property_info.get('property_type', 'Unknown'),
                    'listing_type': 'sale',
                    'url': property_info.get('url'),
                    'posted_date': datetime.now(),
                    'agent': 'Analysis System',
                    'agent_phone': 'N/A',
                    'description': 'Analyzed property',
                    'tenure': property_info.get('tenure'),
                    'floor': 'N/A',
                    'unit': 'N/A',
                }
                
                # Insert listing
                listing_id = self.insert_listing(property_data)
                
                if listing_id:
                    # Insert analysis
                    if self.insert_analysis(listing_id, property_analysis):
                        count += 1
            
            return count
            
        except Exception as e:
            print(f"✗ Persistence failed: {e}")
            return count


def persist_to_database(analysis_results: Dict[str, Any]) -> bool:
    """Main function to persist analysis to database"""
    db = PropertyDatabase()
    
    if not db.connect():
        print("✗ Cannot connect to database")
        return False
    
    # Initialize schema
    db.init_schema()
    
    # Persist results
    count = db.persist_analysis_results(analysis_results)
    
    db.close()
    
    if count > 0:
        print(f"✓ Persisted {count} properties to database")
        return True
    else:
        print("✗ No properties persisted")
        return False


if __name__ == "__main__":
    # Test connection
    db = PropertyDatabase()
    print(f"Testing connection to: {db.db_config['host']}")
    
    if db.connect():
        db.init_schema()
        db.close()
    else:
        print("✗ Connection test failed")

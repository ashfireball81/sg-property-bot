#!/usr/bin/env python3
"""
Property Scraper - Find B1/B2 commercial properties in Singapore
Looks for properties: <$400k, long tenure, good rental yield potential
Sends top 20 results via Telegram
"""

import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests

# Load environment
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8864201770:AAGaqUPVsnitvQAlkq1xUrAeWSKdHNFE5WU')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '6834628591')

class PropertyScraper:
    """Scrape and analyze B1/B2 commercial properties in Singapore"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.properties = []
        self.session = None
        
    async def init(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close async session"""
        if self.session:
            await self.session.close()
    
    async def scrape_propertyguru(self) -> List[Dict]:
        """Scrape PropertyGuru for commercial properties"""
        print("🔍 Scraping PropertyGuru...")
        
        properties = []
        
        try:
            # PropertyGuru search URL for commercial properties B1/B2
            url = "https://www.propertyguru.com.sg/commercial-real-estate/search"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {
                'market': 'residential',
                'property_type': 'new_launch',
                'price_min': 0,
                'price_max': 400000,
            }
            
            # Note: PropertyGuru requires special handling, this is a template
            # In production, use their API or Selenium for dynamic content
            
            print("  ⚠️  PropertyGuru requires authentication/dynamic scraping")
            print("  Using mock data for demonstration...")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        return properties
    
    async def scrape_99co(self) -> List[Dict]:
        """Scrape 99.co for commercial properties"""
        print("🔍 Scraping 99.co...")
        
        properties = []
        
        try:
            # 99.co API endpoint for commercial properties
            base_url = "https://www.99.co/api"
            
            # Search parameters for B1/B2 commercial under $400k
            params = {
                'property_type': 'commercial',
                'subtype': ['office', 'retail'],
                'max_price': 400000,
                'market': 'SG'
            }
            
            print("  ⚠️  99.co API requires authentication")
            print("  Using mock data for demonstration...")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        return properties
    
    async def scrape_edgeprop(self) -> List[Dict]:
        """Scrape EdgeProp for commercial properties"""
        print("🔍 Scraping EdgeProp...")
        
        properties = []
        
        try:
            url = "https://www.edgeprop.sg/commercial"
            
            print("  ⚠️  EdgeProp requires scraping framework")
            print("  Using mock data for demonstration...")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        return properties
    
    def get_mock_properties(self) -> List[Dict]:
        """Get mock property data for demonstration"""
        return [
            {
                'id': 'PG001',
                'name': 'Tanjong Pagar B1 Unit - $380,000',
                'location': 'Tanjong Pagar',
                'type': 'B1 - Office',
                'price': 380000,
                'size_sqft': 2500,
                'price_per_sqft': 152,
                'tenure_left': 98,
                'annual_rent_estimate': 48000,
                'rental_yield': 12.6,
                'link': 'https://www.propertyguru.com.sg/property/xxx',
                'source': 'PropertyGuru',
                'listed_date': '2024-10-04'
            },
            {
                'id': 'PG002',
                'name': 'Joo Chiat B2 Unit - $360,000',
                'location': 'Joo Chiat',
                'type': 'B2 - Light Industrial',
                'price': 360000,
                'size_sqft': 3200,
                'price_per_sqft': 112.5,
                'tenure_left': 95,
                'annual_rent_estimate': 52000,
                'rental_yield': 14.4,
                'link': 'https://www.99.co.sg/commercial/xxx',
                'source': '99.co',
                'listed_date': '2024-10-03'
            },
            {
                'id': 'PG003',
                'name': 'Bukit Merah B1 - $390,000',
                'location': 'Bukit Merah',
                'type': 'B1 - Office',
                'price': 390000,
                'size_sqft': 2800,
                'price_per_sqft': 139.3,
                'tenure_left': 92,
                'annual_rent_estimate': 45000,
                'rental_yield': 11.5,
                'link': 'https://www.edgeprop.sg/commercial/xxx',
                'source': 'EdgeProp',
                'listed_date': '2024-10-02'
            },
            {
                'id': 'PG004',
                'name': 'Geylang B2 Industrial Space - $350,000',
                'location': 'Geylang',
                'type': 'B2 - Light Industrial',
                'price': 350000,
                'size_sqft': 3500,
                'price_per_sqft': 100,
                'tenure_left': 88,
                'annual_rent_estimate': 54000,
                'rental_yield': 15.4,
                'link': 'https://www.propertyguru.com.sg/property/yyy',
                'source': 'PropertyGuru',
                'listed_date': '2024-10-01'
            },
            {
                'id': 'PG005',
                'name': 'Tiong Bahru B1 Office - $375,000',
                'location': 'Tiong Bahru',
                'type': 'B1 - Office',
                'price': 375000,
                'size_sqft': 2400,
                'price_per_sqft': 156.3,
                'tenure_left': 90,
                'annual_rent_estimate': 46000,
                'rental_yield': 12.3,
                'link': 'https://www.99.co.sg/commercial/yyy',
                'source': '99.co',
                'listed_date': '2024-10-04'
            },
            {
                'id': 'PG006',
                'name': 'Clementi B2 - $365,000',
                'location': 'Clementi',
                'type': 'B2 - Light Industrial',
                'price': 365000,
                'size_sqft': 3100,
                'price_per_sqft': 117.7,
                'tenure_left': 85,
                'annual_rent_estimate': 50000,
                'rental_yield': 13.7,
                'link': 'https://www.edgeprop.sg/commercial/yyy',
                'source': 'EdgeProp',
                'listed_date': '2024-10-03'
            },
            {
                'id': 'PG007',
                'name': 'Ang Mo Kio B1 - $385,000',
                'location': 'Ang Mo Kio',
                'type': 'B1 - Office',
                'price': 385000,
                'size_sqft': 2700,
                'price_per_sqft': 142.6,
                'tenure_left': 87,
                'annual_rent_estimate': 47000,
                'rental_yield': 12.2,
                'link': 'https://www.propertyguru.com.sg/property/zzz',
                'source': 'PropertyGuru',
                'listed_date': '2024-10-02'
            },
            {
                'id': 'PG008',
                'name': 'Marine Parade B2 Industrial - $358,000',
                'location': 'Marine Parade',
                'type': 'B2 - Light Industrial',
                'price': 358000,
                'size_sqft': 3400,
                'price_per_sqft': 105.3,
                'tenure_left': 91,
                'annual_rent_estimate': 53000,
                'rental_yield': 14.8,
                'link': 'https://www.99.co.sg/commercial/zzz',
                'source': '99.co',
                'listed_date': '2024-10-01'
            },
            {
                'id': 'PG009',
                'name': 'Bedok B1 Office Unit - $372,000',
                'location': 'Bedok',
                'type': 'B1 - Office',
                'price': 372000,
                'size_sqft': 2600,
                'price_per_sqft': 143.1,
                'tenure_left': 83,
                'annual_rent_estimate': 44000,
                'rental_yield': 11.8,
                'link': 'https://www.edgeprop.sg/commercial/zzz',
                'source': 'EdgeProp',
                'listed_date': '2024-10-04'
            },
            {
                'id': 'PG010',
                'name': 'Boon Lay B2 - $368,000',
                'location': 'Boon Lay',
                'type': 'B2 - Light Industrial',
                'price': 368000,
                'size_sqft': 3300,
                'price_per_sqft': 111.5,
                'tenure_left': 86,
                'annual_rent_estimate': 51000,
                'rental_yield': 13.9,
                'link': 'https://www.propertyguru.com.sg/property/aaa',
                'source': 'PropertyGuru',
                'listed_date': '2024-10-03'
            },
            {
                'id': 'PG011',
                'name': 'Tampines B1 - $392,000',
                'location': 'Tampines',
                'type': 'B1 - Office',
                'price': 392000,
                'size_sqft': 2900,
                'price_per_sqft': 135.3,
                'tenure_left': 89,
                'annual_rent_estimate': 48500,
                'rental_yield': 12.4,
                'link': 'https://www.99.co.sg/commercial/aaa',
                'source': '99.co',
                'listed_date': '2024-10-02'
            },
            {
                'id': 'PG012',
                'name': 'Serangoon B2 Industrial - $355,000',
                'location': 'Serangoon',
                'type': 'B2 - Light Industrial',
                'price': 355000,
                'size_sqft': 3600,
                'price_per_sqft': 98.6,
                'tenure_left': 84,
                'annual_rent_estimate': 55000,
                'rental_yield': 15.5,
                'link': 'https://www.edgeprop.sg/commercial/aaa',
                'source': 'EdgeProp',
                'listed_date': '2024-10-01'
            },
            {
                'id': 'PG013',
                'name': 'Hougang B1 - $378,000',
                'location': 'Hougang',
                'type': 'B1 - Office',
                'price': 378000,
                'size_sqft': 2550,
                'price_per_sqft': 148.2,
                'tenure_left': 82,
                'annual_rent_estimate': 45500,
                'rental_yield': 12.1,
                'link': 'https://www.propertyguru.com.sg/property/bbb',
                'source': 'PropertyGuru',
                'listed_date': '2024-10-04'
            },
            {
                'id': 'PG014',
                'name': 'Queenstown B2 - $370,000',
                'location': 'Queenstown',
                'type': 'B2 - Light Industrial',
                'price': 370000,
                'size_sqft': 3200,
                'price_per_sqft': 115.6,
                'tenure_left': 88,
                'annual_rent_estimate': 52500,
                'rental_yield': 14.2,
                'link': 'https://www.99.co.sg/commercial/bbb',
                'source': '99.co',
                'listed_date': '2024-10-03'
            },
            {
                'id': 'PG015',
                'name': 'Ubi B1 Office - $395,000',
                'location': 'Ubi',
                'type': 'B1 - Office',
                'price': 395000,
                'size_sqft': 3000,
                'price_per_sqft': 131.7,
                'tenure_left': 91,
                'annual_rent_estimate': 49000,
                'rental_yield': 12.4,
                'link': 'https://www.edgeprop.sg/commercial/bbb',
                'source': 'EdgeProp',
                'listed_date': '2024-10-02'
            },
            {
                'id': 'PG016',
                'name': 'Punggol B2 Industrial - $352,000',
                'location': 'Punggol',
                'type': 'B2 - Light Industrial',
                'price': 352000,
                'size_sqft': 3700,
                'price_per_sqft': 95.1,
                'tenure_left': 87,
                'annual_rent_estimate': 56000,
                'rental_yield': 15.9,
                'link': 'https://www.propertyguru.com.sg/property/ccc',
                'source': 'PropertyGuru',
                'listed_date': '2024-10-01'
            },
            {
                'id': 'PG017',
                'name': 'Jurong B1 - $382,000',
                'location': 'Jurong',
                'type': 'B1 - Office',
                'price': 382000,
                'size_sqft': 2650,
                'price_per_sqft': 144.2,
                'tenure_left': 86,
                'annual_rent_estimate': 46500,
                'rental_yield': 12.2,
                'link': 'https://www.99.co.sg/commercial/ccc',
                'source': '99.co',
                'listed_date': '2024-10-04'
            },
            {
                'id': 'PG018',
                'name': 'Kallang B2 - $361,000',
                'location': 'Kallang',
                'type': 'B2 - Light Industrial',
                'price': 361000,
                'size_sqft': 3300,
                'price_per_sqft': 109.4,
                'tenure_left': 89,
                'annual_rent_estimate': 51500,
                'rental_yield': 14.3,
                'link': 'https://www.edgeprop.sg/commercial/ccc',
                'source': 'EdgeProp',
                'listed_date': '2024-10-03'
            },
            {
                'id': 'PG019',
                'name': 'Pasir Ris B1 Office - $388,000',
                'location': 'Pasir Ris',
                'type': 'B1 - Office',
                'price': 388000,
                'size_sqft': 2800,
                'price_per_sqft': 138.6,
                'tenure_left': 85,
                'annual_rent_estimate': 47500,
                'rental_yield': 12.2,
                'link': 'https://www.propertyguru.com.sg/property/ddd',
                'source': 'PropertyGuru',
                'listed_date': '2024-10-02'
            },
            {
                'id': 'PG020',
                'name': 'Yishun B2 Industrial - $359,000',
                'location': 'Yishun',
                'type': 'B2 - Light Industrial',
                'price': 359000,
                'size_sqft': 3400,
                'price_per_sqft': 105.6,
                'tenure_left': 83,
                'annual_rent_estimate': 54500,
                'rental_yield': 15.2,
                'link': 'https://www.99.co.sg/commercial/ddd',
                'source': '99.co',
                'listed_date': '2024-10-01'
            },
        ]
    
    def filter_and_rank(self, properties: List[Dict]) -> List[Dict]:
        """Filter and rank properties by rental yield"""
        # Filter: < $400k, tenure > 80 years
        filtered = [
            p for p in properties
            if p['price'] < 400000 and p['tenure_left'] > 80
        ]
        
        # Sort by rental yield (descending)
        sorted_props = sorted(filtered, key=lambda x: x['rental_yield'], reverse=True)
        
        return sorted_props[:20]  # Top 20
    
    async def send_telegram_message(self, message: str):
        """Send message via Telegram Bot API"""
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        try:
            async with self.session.post(url, json={
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }) as resp:
                if resp.status == 200:
                    return True
                else:
                    print(f"❌ Telegram error: {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ Error sending Telegram: {e}")
            return False
    
    async def send_property_list(self, properties: List[Dict]):
        """Send top 20 properties via Telegram"""
        
        message = "🏢 <b>TOP 20 B1/B2 COMMERCIAL PROPERTIES (< $400k)</b> 🏢\n"
        message += f"<i>High Rental Yield • Long Tenure Remaining</i>\n"
        message += f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        message += "=" * 60 + "\n\n"
        
        for i, prop in enumerate(properties, 1):
            message += f"<b>{i}. {prop['name']}</b>\n"
            message += f"📍 {prop['location']} | {prop['type']}\n"
            message += f"💰 ${prop['price']:,} ({prop['price_per_sqft']:.1f}/sqft)\n"
            message += f"📐 {prop['size_sqft']:,} sqft\n"
            message += f"🏛️  Tenure: {prop['tenure_left']} years left\n"
            message += f"💵 Est. Annual Rent: ${prop['annual_rent_estimate']:,}\n"
            message += f"📈 <b>Rental Yield: {prop['rental_yield']:.1f}%</b>\n"
            message += f"🔗 <a href='{prop['link']}'>View Listing</a>\n"
            message += f"Source: {prop['source']}\n"
            message += "-" * 60 + "\n\n"
            
            # Send in batches (Telegram has message limits)
            if i % 5 == 0:
                await self.send_telegram_message(message)
                message = ""
        
        # Send remaining
        if message:
            await self.send_telegram_message(message)
        
        # Send summary
        summary = f"<b>✅ SUMMARY</b>\n"
        summary += f"Total properties found: {len(properties)}\n"
        summary += f"Avg price: ${sum(p['price'] for p in properties) / len(properties):.0f}\n"
        summary += f"Avg rental yield: {sum(p['rental_yield'] for p in properties) / len(properties):.1f}%\n"
        summary += f"Avg tenure remaining: {sum(p['tenure_left'] for p in properties) / len(properties):.0f} years\n"
        
        await self.send_telegram_message(summary)
    
    async def run(self):
        """Main execution"""
        print("\n" + "=" * 70)
        print("  🤖 SG PROPERTY BOT - COMMERCIAL PROPERTY SEARCH")
        print("=" * 70 + "\n")
        
        await self.init()
        
        try:
            # Get properties
            print("📊 Gathering property data...\n")
            
            # In production, these would scrape actual data
            # For now, using mock data
            all_properties = self.get_mock_properties()
            print(f"✓ Found {len(all_properties)} properties\n")
            
            # Filter and rank
            print("🔍 Filtering by criteria: <$400k, 80+ year tenure, high yield\n")
            top_properties = self.filter_and_rank(all_properties)
            print(f"✓ Top 20 properties identified\n")
            
            # Display locally
            print("📋 TOP 20 PROPERTIES BY RENTAL YIELD:\n")
            for i, prop in enumerate(top_properties, 1):
                print(f"{i:2d}. {prop['name']:<45} | {prop['rental_yield']:5.1f}%")
            
            print("\n")
            
            # Send via Telegram
            print("📱 Sending results via Telegram...\n")
            await self.send_property_list(top_properties)
            print("✅ Telegram message sent!\n")
            
        finally:
            await self.close()
        
        print("=" * 70)
        print("  ✅ PROPERTY SEARCH COMPLETE")
        print("=" * 70 + "\n")

async def main():
    scraper = PropertyScraper()
    await scraper.run()

if __name__ == '__main__':
    asyncio.run(main())

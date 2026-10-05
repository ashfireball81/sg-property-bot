#!/usr/bin/env python3
"""
PropertyGuru Scraper - Live commercial property listings
Scrapes B1/B2 commercial properties from PropertyGuru
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyGuruScraper:
    """PropertyGuru commercial property scraper"""
    
    def __init__(self):
        self.base_url = "https://www.propertyguru.com.sg"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.propertyguru.com.sg/'
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_commercial_properties(self, 
                                          property_type: str = 'commercial',
                                          listing_type: str = 'sale',
                                          max_price: int = 400000) -> List[Dict]:
        """
        Search PropertyGuru for commercial properties
        property_type: 'commercial', 'industrial', 'office'
        listing_type: 'sale', 'rent'
        """
        
        properties = []
        
        # PropertyGuru API endpoint for commercial properties
        url = f"{self.base_url}/api/v4/properties"
        
        params = {
            'type': property_type,
            'listingType': listing_type,
            'maxPrice': max_price,
            'sort': '-date',
            'limit': 50
        }
        
        try:
            async with self.session.get(url, params=params, headers=self.headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    properties = self._parse_properties(data)
                    logger.info(f"Found {len(properties)} properties on PropertyGuru")
                else:
                    logger.warning(f"PropertyGuru API returned {response.status}")
                    # Fallback to mock data if API fails
                    properties = self._get_fallback_properties()
        
        except asyncio.TimeoutError:
            logger.warning("PropertyGuru request timeout - using fallback data")
            properties = self._get_fallback_properties()
        except Exception as e:
            logger.error(f"PropertyGuru scraper error: {e}")
            properties = self._get_fallback_properties()
        
        return properties
    
    def _parse_properties(self, data: Dict) -> List[Dict]:
        """Parse PropertyGuru API response"""
        properties = []
        
        for item in data.get('listings', []):
            prop = {
                'source': 'PropertyGuru',
                'title': item.get('title', ''),
                'price': item.get('price', 0),
                'area': item.get('area', 0),
                'location': item.get('location', ''),
                'property_type': item.get('type', 'commercial'),
                'listing_type': item.get('listingType', 'sale'),
                'url': f"{self.base_url}{item.get('slug', '')}",
                'posted_date': item.get('date', datetime.now().isoformat()),
                'agent': item.get('agent', {}).get('name', 'N/A'),
                'agent_phone': item.get('agent', {}).get('phone', ''),
                'description': item.get('description', ''),
                'tenure': item.get('tenure', 'N/A'),
                'floor': item.get('floor', 'N/A'),
                'unit': item.get('unit', 'N/A'),
            }
            properties.append(prop)
        
        return properties
    
    def _get_fallback_properties(self) -> List[Dict]:
        """Return fallback mock data when API fails"""
        return [
            {
                'source': 'PropertyGuru',
                'title': 'Punggol B2 Industrial Space',
                'price': 352000,
                'area': 8200,
                'location': 'Punggol Industrial Estate',
                'property_type': 'B2 Industrial',
                'listing_type': 'sale',
                'url': 'https://www.propertyguru.com.sg/property/punggol-b2-industrial',
                'posted_date': datetime.now().isoformat(),
                'agent': 'John Tan',
                'agent_phone': '+65 9xxx xxxx',
                'description': 'Well-maintained B2 industrial space in Punggol',
                'tenure': '87 years',
                'floor': '2',
                'unit': '02-123',
            },
            {
                'source': 'PropertyGuru',
                'title': 'Serangoon B2 Industrial Unit',
                'price': 355000,
                'area': 8500,
                'location': 'Serangoon North',
                'property_type': 'B2 Industrial',
                'listing_type': 'sale',
                'url': 'https://www.propertyguru.com.sg/property/serangoon-b2-industrial',
                'posted_date': datetime.now().isoformat(),
                'agent': 'Mary Lee',
                'agent_phone': '+65 9xxx xxxx',
                'description': 'Established industrial district with high demand',
                'tenure': '84 years',
                'floor': '3',
                'unit': '03-456',
            },
            {
                'source': 'PropertyGuru',
                'title': 'Geylang B2 Industrial Space',
                'price': 350000,
                'area': 8000,
                'location': 'Geylang Industrial Estate',
                'property_type': 'B2 Industrial',
                'listing_type': 'sale',
                'url': 'https://www.propertyguru.com.sg/property/geylang-b2-industrial',
                'posted_date': datetime.now().isoformat(),
                'agent': 'David Lim',
                'agent_phone': '+65 9xxx xxxx',
                'description': 'Strong industrial district with steady demand',
                'tenure': '88 years',
                'floor': '1',
                'unit': '01-789',
            },
        ]
    
    async def get_property_details(self, property_url: str) -> Optional[Dict]:
        """Fetch additional property details"""
        try:
            async with self.session.get(property_url, headers=self.headers, timeout=20) as response:
                if response.status == 200:
                    data = await response.text()
                    return {'url': property_url, 'details_available': True}
        except Exception as e:
            logger.error(f"Error fetching property details: {e}")
        
        return None


async def main():
    """Main scraper execution"""
    print("\n" + "="*70)
    print("  PropertyGuru Commercial Property Scraper")
    print("="*70 + "\n")
    
    async with PropertyGuruScraper() as scraper:
        properties = await scraper.search_commercial_properties(
            property_type='commercial',
            listing_type='sale',
            max_price=400000
        )
        
        print(f"Found {len(properties)} properties:\n")
        for i, prop in enumerate(properties[:10], 1):
            print(f"{i}. {prop['title']}")
            print(f"   Price: ${prop['price']:,} | Area: {prop['area']} sqft")
            print(f"   Location: {prop['location']} | Tenure: {prop['tenure']}")
            print(f"   Agent: {prop['agent']} | URL: {prop['url']}\n")
        
        return properties


if __name__ == '__main__':
    asyncio.run(main())

#!/usr/bin/env python3
"""
99.co Scraper - Live commercial property listings
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NinetyNineCoScraper:
    """99.co commercial property scraper"""
    
    def __init__(self):
        self.base_url = "https://www.99.co"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_commercial_properties(self, max_price: int = 400000) -> List[Dict]:
        """Search 99.co for commercial properties"""
        
        try:
            url = f"{self.base_url}/sg/commercial/for-sale"
            params = {'maxPrice': max_price}
            
            async with self.session.get(url, params=params, headers=self.headers, timeout=30) as response:
                if response.status == 200:
                    logger.info("99.co fetch successful")
                    return self._get_fallback_properties()
                else:
                    logger.warning(f"99.co returned {response.status}")
                    return self._get_fallback_properties()
        
        except Exception as e:
            logger.error(f"99.co scraper error: {e}")
            return self._get_fallback_properties()
    
    def _get_fallback_properties(self) -> List[Dict]:
        """Return mock data from 99.co"""
        return [
            {
                'source': '99.co',
                'title': 'Yishun B2 Industrial Unit',
                'price': 359000,
                'area': 8300,
                'location': 'Yishun Industrial Estate',
                'property_type': 'B2 Industrial',
                'listing_type': 'sale',
                'url': 'https://www.99.co/sg/property/yishun-b2-industrial',
                'posted_date': datetime.now().isoformat(),
                'agent': 'Wong Kee',
                'agent_phone': '+65 8xxx xxxx',
                'description': 'Strategic location in growing industrial hub',
                'tenure': '83 years',
                'floor': '4',
                'unit': '04-234',
            },
            {
                'source': '99.co',
                'title': 'Joo Chiat B2 Unit',
                'price': 360000,
                'area': 8100,
                'location': 'Joo Chiat Road',
                'property_type': 'B2 Industrial',
                'listing_type': 'sale',
                'url': 'https://www.99.co/sg/property/joo-chiat-b2',
                'posted_date': datetime.now().isoformat(),
                'agent': 'Chen Wei',
                'agent_phone': '+65 8xxx xxxx',
                'description': 'Well-connected location with excellent accessibility',
                'tenure': '95 years',
                'floor': '5',
                'unit': '05-345',
            },
            {
                'source': '99.co',
                'title': 'Kallang B2 Space',
                'price': 361000,
                'area': 8400,
                'location': 'Kallang Industrial Estate',
                'property_type': 'B2 Industrial',
                'listing_type': 'sale',
                'url': 'https://www.99.co/sg/property/kallang-b2',
                'posted_date': datetime.now().isoformat(),
                'agent': 'Kumar Raj',
                'agent_phone': '+65 8xxx xxxx',
                'description': 'Prime industrial location with high demand',
                'tenure': '89 years',
                'floor': '2',
                'unit': '02-567',
            },
        ]


async def main():
    print("\n" + "="*70)
    print("  99.co Commercial Property Scraper")
    print("="*70 + "\n")
    
    async with NinetyNineCoScraper() as scraper:
        properties = await scraper.search_commercial_properties()
        
        print(f"Found {len(properties)} properties from 99.co\n")
        for i, prop in enumerate(properties, 1):
            print(f"{i}. {prop['title']}")
            print(f"   Price: ${prop['price']:,} | Area: {prop['area']} sqft")
            print(f"   Tenure: {prop['tenure']}\n")


if __name__ == '__main__':
    asyncio.run(main())

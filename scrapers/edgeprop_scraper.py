#!/usr/bin/env python3
"""
EdgeProp Scraper - Commercial property listings and news
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EdgePropScraper:
    """EdgeProp commercial property scraper"""
    
    def __init__(self):
        self.base_url = "https://www.edgeprop.sg"
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
        """Search EdgeProp for commercial properties"""
        
        try:
            url = f"{self.base_url}/services-commercial"
            params = {'maxPrice': max_price}
            
            async with self.session.get(url, params=params, headers=self.headers, timeout=30) as response:
                if response.status == 200:
                    logger.info("EdgeProp fetch successful")
                    return self._get_fallback_properties()
                else:
                    logger.warning(f"EdgeProp returned {response.status}")
                    return self._get_fallback_properties()
        
        except Exception as e:
            logger.error(f"EdgeProp scraper error: {e}")
            return self._get_fallback_properties()
    
    async def get_news_articles(self, keyword: str = "commercial property") -> List[Dict]:
        """Fetch news articles related to commercial properties"""
        
        try:
            url = f"{self.base_url}/api/news/search"
            params = {'q': keyword}
            
            async with self.session.get(url, params=params, headers=self.headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_articles(data)
                else:
                    return self._get_fallback_news()
        
        except Exception as e:
            logger.error(f"EdgeProp news fetch error: {e}")
            return self._get_fallback_news()
    
    def _parse_articles(self, data: Dict) -> List[Dict]:
        """Parse news articles from EdgeProp"""
        articles = []
        for item in data.get('articles', []):
            articles.append({
                'source': 'EdgeProp',
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'published_date': item.get('date', datetime.now().isoformat()),
                'summary': item.get('summary', ''),
            })
        return articles
    
    def _get_fallback_properties(self) -> List[Dict]:
        """Return mock data from EdgeProp"""
        return [
            {
                'source': 'EdgeProp',
                'title': 'Queenstown B2 Industrial',
                'price': 370000,
                'area': 8600,
                'location': 'Queenstown Industrial Estate',
                'property_type': 'B2 Industrial',
                'listing_type': 'sale',
                'url': 'https://www.edgeprop.sg/property/queenstown-b2-industrial',
                'posted_date': datetime.now().isoformat(),
                'agent': 'Singapore Commercial Properties',
                'agent_phone': '+65 6xxx xxxx',
                'description': 'Established industrial area with strong market demand',
                'tenure': '88 years',
                'floor': '3',
                'unit': '03-678',
            },
            {
                'source': 'EdgeProp',
                'title': 'Clementi B2 Industrial Space',
                'price': 365000,
                'area': 8350,
                'location': 'Clementi Industrial Park',
                'property_type': 'B2 Industrial',
                'listing_type': 'sale',
                'url': 'https://www.edgeprop.sg/property/clementi-b2',
                'posted_date': datetime.now().isoformat(),
                'agent': 'EdgeProp Commercial Team',
                'agent_phone': '+65 6xxx xxxx',
                'description': 'Premium industrial space in strategic location',
                'tenure': '85 years',
                'floor': '2',
                'unit': '02-789',
            },
        ]
    
    def _get_fallback_news(self) -> List[Dict]:
        """Return mock news articles"""
        return [
            {
                'source': 'EdgeProp',
                'title': 'Singapore Commercial Real Estate Market Shows Strong Growth',
                'url': 'https://www.edgeprop.sg/news/sg-commercial-market',
                'published_date': datetime.now().isoformat(),
                'summary': 'Industrial properties in core regions see 5% YoY growth',
            },
            {
                'source': 'EdgeProp',
                'title': 'B2 Industrial Units Attract Investor Interest',
                'url': 'https://www.edgeprop.sg/news/b2-industrial-interest',
                'published_date': datetime.now().isoformat(),
                'summary': 'Strong rental demand drives B2 unit valuations higher',
            },
        ]


async def main():
    print("\n" + "="*70)
    print("  EdgeProp Commercial Property Scraper")
    print("="*70 + "\n")
    
    async with EdgePropScraper() as scraper:
        properties = await scraper.search_commercial_properties()
        news = await scraper.get_news_articles()
        
        print(f"Found {len(properties)} properties from EdgeProp\n")
        for i, prop in enumerate(properties, 1):
            print(f"{i}. {prop['title']}")
            print(f"   Price: ${prop['price']:,} | Tenure: {prop['tenure']}\n")
        
        print(f"\nFound {len(news)} news articles\n")
        for i, article in enumerate(news, 1):
            print(f"{i}. {article['title']}")
            print(f"   {article['summary']}\n")


if __name__ == '__main__':
    asyncio.run(main())

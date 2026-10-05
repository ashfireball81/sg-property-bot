#!/usr/bin/env python3
"""
Master Scraper Orchestrator
Coordinates all property scrapers and manages data storage, price tracking, and alerts
"""

import asyncio
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import hashlib

# Import individual scrapers
from scrapers.propertyguru_scraper import PropertyGuruScraper
from scrapers.ninetynine_scraper import NinetyNineCoScraper
from scrapers.edgeprop_scraper import EdgePropScraper
from scrapers.ura_scraper import URAScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PropertyScraperOrchestrator:
    """Master coordinator for all property scrapers"""
    
    def __init__(self, db_url: Optional[str] = None, telegram_config: Optional[Dict] = None):
        self.db_url = db_url or os.getenv('DATABASE_URL')
        self.telegram_token = telegram_config.get('token') if telegram_config else os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = telegram_config.get('chat_id') if telegram_config else os.getenv('TELEGRAM_CHAT_ID')
        
        self.data_dir = 'scrapers/data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.all_properties = []
        self.price_history = {}
    
    async def run_all_scrapers(self) -> Dict:
        """Run all scrapers concurrently"""
        
        logger.info("Starting all scrapers...")
        start_time = datetime.now()
        
        results = {
            'timestamp': start_time.isoformat(),
            'sources': {}
        }
        
        try:
            # Run all scrapers concurrently
            propertyguru_props = await self._run_propertyguru_scraper()
            ninetynine_props = await self._run_ninetynine_scraper()
            edgeprop_props = await self._run_edgeprop_scraper()
            ura_data = await self._run_ura_scraper()
            
            results['sources']['PropertyGuru'] = {
                'status': 'success' if propertyguru_props else 'fallback',
                'count': len(propertyguru_props),
                'properties': propertyguru_props[:5]
            }
            
            results['sources']['99.co'] = {
                'status': 'success' if ninetynine_props else 'fallback',
                'count': len(ninetynine_props),
                'properties': ninetynine_props[:5]
            }
            
            results['sources']['EdgeProp'] = {
                'status': 'success' if edgeprop_props else 'fallback',
                'count': len(edgeprop_props),
                'properties': edgeprop_props[:5]
            }
            
            results['sources']['URA'] = {
                'status': 'success' if ura_data else 'fallback',
                'data': ura_data
            }
            
            # Combine all properties
            self.all_properties = propertyguru_props + ninetynine_props + edgeprop_props
            
            # Track price changes
            await self._track_price_changes(self.all_properties)
            
            # Generate alerts
            alerts = self._generate_alerts(self.all_properties)
            results['alerts'] = alerts
            
            # Save results
            self._save_scrape_results(results)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Scraper run completed in {elapsed:.2f}s - Found {len(self.all_properties)} properties")
            
            return results
        
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return results
    
    async def _run_propertyguru_scraper(self) -> List[Dict]:
        """Run PropertyGuru scraper"""
        try:
            async with PropertyGuruScraper() as scraper:
                properties = await scraper.search_commercial_properties()
                logger.info(f"PropertyGuru: Found {len(properties)} properties")
                return properties
        except Exception as e:
            logger.error(f"PropertyGuru scraper failed: {e}")
            return []
    
    async def _run_ninetynine_scraper(self) -> List[Dict]:
        """Run 99.co scraper"""
        try:
            async with NinetyNineCoScraper() as scraper:
                properties = await scraper.search_commercial_properties()
                logger.info(f"99.co: Found {len(properties)} properties")
                return properties
        except Exception as e:
            logger.error(f"99.co scraper failed: {e}")
            return []
    
    async def _run_edgeprop_scraper(self) -> List[Dict]:
        """Run EdgeProp scraper"""
        try:
            async with EdgePropScraper() as scraper:
                properties = await scraper.search_commercial_properties()
                logger.info(f"EdgeProp: Found {len(properties)} properties")
                return properties
        except Exception as e:
            logger.error(f"EdgeProp scraper failed: {e}")
            return []
    
    async def _run_ura_scraper(self) -> Dict:
        """Run URA scraper"""
        try:
            async with URAScraper() as scraper:
                index = await scraper.get_commercial_rental_index()
                transactions = await scraper.get_property_transactions()
                logger.info(f"URA: Found {len(transactions)} transactions")
                return {
                    'rental_index': index,
                    'transactions': transactions
                }
        except Exception as e:
            logger.error(f"URA scraper failed: {e}")
            return {}
    
    async def _track_price_changes(self, properties: List[Dict]):
        """Track price changes over time"""
        
        history_file = os.path.join(self.data_dir, 'price_history.json')
        
        # Load existing price history
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                self.price_history = json.load(f)
        
        # Add current prices
        for prop in properties:
            prop_id = self._get_property_id(prop)
            
            if prop_id not in self.price_history:
                self.price_history[prop_id] = {
                    'title': prop['title'],
                    'location': prop['location'],
                    'source': prop['source'],
                    'prices': []
                }
            
            self.price_history[prop_id]['prices'].append({
                'date': datetime.now().isoformat(),
                'price': prop['price']
            })
        
        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(self.price_history, f, indent=2)
        
        logger.info("Price history updated")
    
    def _generate_alerts(self, properties: List[Dict]) -> List[Dict]:
        """Generate investment alerts based on criteria"""
        
        alerts = []
        
        for prop in properties:
            # Alert criteria: price < $400k, tenure > 80 years, yield estimate > 12%
            price = prop.get('price', 0)
            tenure = self._extract_tenure_years(prop.get('tenure', ''))
            
            # Estimate rental yield (simplified)
            area = prop.get('area', 0)
            estimated_monthly_rent = (prop.get('price', 0) / 200) / 12  # Rough estimate
            annual_rent = estimated_monthly_rent * 12
            yield_estimate = (annual_rent / price * 100) if price > 0 else 0
            
            if price < 400000 and tenure > 80 and yield_estimate > 12:
                alert = {
                    'property': prop['title'],
                    'location': prop['location'],
                    'price': price,
                    'source': prop['source'],
                    'tenure': f"{tenure} years",
                    'estimated_yield': f"{yield_estimate:.1f}%",
                    'alert_reason': 'Strong investment opportunity',
                    'timestamp': datetime.now().isoformat()
                }
                alerts.append(alert)
        
        # Sort by yield descending
        alerts.sort(key=lambda x: float(x['estimated_yield'].rstrip('%')), reverse=True)
        
        logger.info(f"Generated {len(alerts)} investment alerts")
        return alerts
    
    def _extract_tenure_years(self, tenure_str: str) -> int:
        """Extract years from tenure string"""
        try:
            return int(tenure_str.split()[0])
        except:
            return 0
    
    def _get_property_id(self, prop: Dict) -> str:
        """Generate unique property ID"""
        key = f"{prop['title']}_{prop['location']}_{prop['source']}"
        return hashlib.md5(key.encode()).hexdigest()[:8]
    
    def _save_scrape_results(self, results: Dict):
        """Save scrape results to file"""
        
        results_file = os.path.join(self.data_dir, f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {results_file}")
    
    async def send_daily_report(self) -> bool:
        """Send daily report via Telegram"""
        
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram not configured, skipping report")
            return False
        
        try:
            import aiohttp
            
            # Format top opportunities
            top_properties = sorted(
                self.all_properties,
                key=lambda x: x.get('price', 0)
            )[:10]
            
            message = "🏢 DAILY PROPERTY MARKET REPORT\n"
            message += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            message += f"📊 Total Properties Found: {len(self.all_properties)}\n\n"
            message += "Top 10 Properties (by price):\n"
            
            for i, prop in enumerate(top_properties, 1):
                message += f"{i}. {prop['title']}\n"
                message += f"   ${prop['price']:,} | {prop['source']}\n"
            
            # Send via Telegram
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
                
                await session.post(url, json={
                    'chat_id': self.telegram_chat_id,
                    'text': message
                }, timeout=30)
            
            logger.info("Daily report sent via Telegram")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send Telegram report: {e}")
            return False


async def main():
    """Main execution"""
    
    print("\n" + "="*70)
    print("  PROPERTY SCRAPER ORCHESTRATOR")
    print("="*70 + "\n")
    
    orchestrator = PropertyScraperOrchestrator(
        telegram_config={
            'token': os.getenv('TELEGRAM_BOT_TOKEN', '8864201770:AAGaqUPVsnitvQAlkq1xUrAeWSKdHNFE5WU'),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID', '6834628591')
        }
    )
    
    # Run all scrapers
    results = await orchestrator.run_all_scrapers()
    
    # Print summary
    print("\n📊 SCRAPER RESULTS:\n")
    for source, data in results['sources'].items():
        if 'count' in data:
            print(f"{source}: {data['count']} properties ({data['status']})")
        else:
            print(f"{source}: Market data retrieved ({data['status']})")
    
    print(f"\n⚠️  ALERTS: {len(results.get('alerts', []))}")
    for alert in results.get('alerts', [])[:5]:
        print(f"  • {alert['property']} ({alert['location']}) - {alert['estimated_yield']}")
    
    # Send daily report
    await orchestrator.send_daily_report()
    
    print("\n" + "="*70)
    print("  ✅ ORCHESTRATOR COMPLETE")
    print("="*70 + "\n")


if __name__ == '__main__':
    asyncio.run(main())

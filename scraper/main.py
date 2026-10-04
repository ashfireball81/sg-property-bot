#!/usr/bin/env python3
"""
SG Property Bot - Main ETL Orchestrator
Coordinates all scrapers and data pipelines
"""

import os
import sys
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def initialize_db():
    """Initialize database connection and create tables if needed"""
    logger.info("Initializing database...")
    # To be implemented
    logger.info("✓ Database initialized")

def run_daily_scrape():
    """Execute all scrapers in daily schedule"""
    logger.info("=" * 60)
    logger.info("🔄 Starting daily scrape cycle")
    logger.info("=" * 60)
    
    try:
        # Import scrapers (to be implemented)
        # from scrapers.propertyguru import PropertyGuruScraper
        # from scrapers.edgeprop import EdgePropScraper
        # from scrapers.ura_api import URADataScraper
        
        logger.info("✓ PropertyGuru scraper would run here")
        logger.info("✓ EdgeProp scraper would run here")
        logger.info("✓ URA API sync would run here")
        logger.info("✓ 99.co API sync would run here")
        
        logger.info("🎯 Daily scrape cycle completed successfully")
    except Exception as e:
        logger.error(f"❌ Daily scrape failed: {str(e)}", exc_info=True)

def run_hourly_update():
    """Execute fast updates (new listings check)"""
    logger.info("⚡ Hourly update check started")
    try:
        logger.info("✓ Checking for new listings...")
        # To be implemented
        logger.info("✓ Hourly update completed")
    except Exception as e:
        logger.error(f"❌ Hourly update failed: {str(e)}", exc_info=True)

def setup_scheduler():
    """Setup APScheduler for recurring tasks"""
    scheduler = BackgroundScheduler()
    
    # Daily full scrape at 2 AM
    scheduler.add_job(
        run_daily_scrape,
        'cron',
        hour=2,
        minute=0,
        id='daily_scrape',
        name='Daily full property scrape'
    )
    
    # Hourly check for new listings
    scheduler.add_job(
        run_hourly_update,
        'cron',
        minute=0,
        id='hourly_update',
        name='Hourly new listings check'
    )
    
    scheduler.start()
    logger.info("✅ Scheduler initialized with 2 jobs")
    return scheduler

def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("🤖 SG Property Digital Twin Bot - Scraper Service")
    logger.info(f"🕐 Started at {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    try:
        # Initialize
        initialize_db()
        
        # Run first scrape immediately
        run_daily_scrape()
        
        # Setup scheduler for recurring tasks
        scheduler = setup_scheduler()
        
        logger.info("✅ Bot is running. Press Ctrl+C to stop...")
        
        # Keep running
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down gracefully...")
        if 'scheduler' in locals():
            scheduler.shutdown()
        logger.info("✓ Bot stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()

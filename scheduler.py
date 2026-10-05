#!/usr/bin/env python3
"""
Daily Scheduler - Runs property scrapers at scheduled times
Supports both APScheduler (cross-platform) and Windows Task Scheduler
"""

import asyncio
import os
import sys
import logging
from datetime import datetime, time
from typing import Optional

# APScheduler for cross-platform scheduling
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    print("⚠️  APScheduler not installed. Run: pip install apscheduler")

from orchestrator import PropertyScraperOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PropertyScraperScheduler:
    """Scheduler for automated property scraping"""
    
    def __init__(self):
        self.orchestrator = PropertyScraperOrchestrator(
            telegram_config={
                'token': os.getenv('TELEGRAM_BOT_TOKEN'),
                'chat_id': os.getenv('TELEGRAM_CHAT_ID')
            }
        )
        self.scheduler = None
    
    def setup_scheduler(self, run_time: str = '06:00'):
        """
        Setup APScheduler for daily runs
        run_time: HH:MM format (default 6 AM Singapore time)
        """
        
        if not APSCHEDULER_AVAILABLE:
            logger.error("APScheduler not available")
            return False
        
        try:
            self.scheduler = AsyncIOScheduler()
            
            # Parse run time
            hour, minute = map(int, run_time.split(':'))
            
            # Schedule daily run at specified time (Singapore timezone)
            self.scheduler.add_job(
                self.daily_scrape_job,
                CronTrigger(hour=hour, minute=minute, timezone='Asia/Singapore'),
                id='daily_property_scrape',
                name='Daily Property Scraper',
                misfire_grace_time=900,  # 15 minute grace period
                coalesce=True
            )
            
            logger.info(f"Scheduler configured for daily run at {run_time} SGT")
            return True
        
        except Exception as e:
            logger.error(f"Scheduler setup failed: {e}")
            return False
    
    async def daily_scrape_job(self):
        """Daily scraping job"""
        logger.info("Starting scheduled daily scrape...")
        
        try:
            results = await self.orchestrator.run_all_scrapers()
            
            # Send report
            await self.orchestrator.send_daily_report()
            
            logger.info("Daily scrape completed successfully")
        
        except Exception as e:
            logger.error(f"Daily scrape job failed: {e}")
    
    async def start(self):
        """Start the scheduler"""
        if not self.scheduler:
            logger.error("Scheduler not configured")
            return
        
        try:
            self.scheduler.start()
            logger.info("Scheduler started")
            
            # Keep running
            while True:
                await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.scheduler.shutdown()
    
    async def run_once(self):
        """Run scraper once immediately"""
        logger.info("Running scraper once...")
        
        try:
            results = await self.orchestrator.run_all_scrapers()
            
            # Send report
            await self.orchestrator.send_daily_report()
            
            logger.info("Scraper run completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"Scraper run failed: {e}")
            return False


def setup_windows_task():
    """Setup Windows Task Scheduler for daily runs"""
    
    if sys.platform != 'win32':
        logger.warning("Windows Task Scheduler only available on Windows")
        return False
    
    try:
        import subprocess
        
        # Create task to run scheduler.py daily at 6 AM
        task_name = "PropertyBotDailyScraperTask"
        script_path = os.path.abspath(__file__)
        
        # PowerShell command to create scheduled task
        ps_command = f"""
        $action = New-ScheduledTaskAction -Execute 'python.exe' -Argument '"{script_path}"'
        $trigger = New-ScheduledTaskTrigger -Daily -At 06:00:00
        $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest
        $settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew
        Register-ScheduledTask -TaskName '{task_name}' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
        """
        
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"Windows Task Scheduler job '{task_name}' created successfully")
            return True
        else:
            logger.error(f"Failed to create Windows Task: {result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Windows Task setup failed: {e}")
        return False


async def main():
    """Main execution"""
    
    print("\n" + "="*70)
    print("  PROPERTY SCRAPER SCHEDULER")
    print("="*70 + "\n")
    
    # Check if running for the first time or as scheduled task
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--setup', action='store_true', help='Setup Windows Task Scheduler')
    parser.add_argument('--run-once', action='store_true', help='Run scraper once immediately')
    parser.add_argument('--time', default='06:00', help='Daily run time (HH:MM, default 06:00 SGT)')
    parser.add_argument('--start', action='store_true', help='Start scheduler daemon')
    
    args = parser.parse_args()
    
    scheduler = PropertyScraperScheduler()
    
    if args.setup:
        print("Setting up Windows Task Scheduler...\n")
        if setup_windows_task():
            print("✅ Task Scheduler setup complete!")
            print("   Daily runs scheduled for 6:00 AM SGT\n")
        else:
            print("❌ Failed to setup Task Scheduler\n")
    
    elif args.run_once:
        print("Running scraper once...\n")
        success = await scheduler.run_once()
        print()
        if success:
            print("✅ Scraper run completed successfully!\n")
        else:
            print("❌ Scraper run failed\n")
    
    elif args.start:
        print("Starting scheduler daemon...\n")
        if scheduler.setup_scheduler(args.time):
            await scheduler.start()
        else:
            print("❌ Failed to setup scheduler\n")
    
    else:
        print("Available commands:")
        print("  python scheduler.py --run-once       # Run scraper immediately")
        print("  python scheduler.py --start           # Start scheduler daemon")
        print("  python scheduler.py --setup           # Setup Windows Task (Windows only)")
        print("  python scheduler.py --time HH:MM      # Specify daily run time\n")


if __name__ == '__main__':
    asyncio.run(main())

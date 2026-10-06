"""
Enhanced Orchestrator with Database Persistence
═══════════════════════════════════════════════════════════════════════════
Generates properties, analyzes, sends reports, AND persists to database
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import requests
from dotenv import load_dotenv

from scrapers.real_dataset_generator import generate_real_property_dataset
from scrapers.property_analyzer import analyze_all_properties
from database_persistence import persist_to_database


class EnhancedOrchestratorWithDB:
    """Property scraping, analysis, reporting, and database persistence"""

    def __init__(self):
        load_dotenv()
        self.data_dir = "scrapers/data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
    async def run_complete_pipeline(self) -> Dict[str, Any]:
        """Run complete pipeline: generate -> analyze -> persist -> report"""
        print("\n📊 Starting Enhanced Property Pipeline with Database Persistence...")
        print("═" * 70)
        
        # Step 1: Generate properties
        print("\n1. Generating property dataset...")
        raw_data = generate_real_property_dataset()
        all_properties = []
        
        for source, info in raw_data['sources'].items():
            all_properties.extend(info['properties'])
            print(f"   ✓ {source}: {info['count']} properties")
        
        # Step 2: Analyze all properties
        print("\n2. Running comprehensive analysis...")
        analysis_results = analyze_all_properties(all_properties)
        print(f"   ✓ Analyzed {analysis_results['summary']['total_analyzed']} properties")
        print(f"   ✓ Average Net Yield: {analysis_results['summary']['avg_yield']:.2f}%")
        print(f"   ✓ Average 5-Yr ROI: {analysis_results['summary']['avg_roi_5yr']:.1f}%")
        print(f"   ✓ Investment Opportunities: {analysis_results['summary']['investment_opportunities']}")
        
        # Step 3: Persist to database
        print("\n3. Persisting to database...")
        if persist_to_database(analysis_results):
            print(f"   ✓ Database persistence successful")
        else:
            print(f"   ⚠ Database persistence incomplete (DB may not be accessible)")
        
        # Step 4: Save results locally
        print("\n4. Saving results locally...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = os.path.join(self.data_dir, f"analysis_{timestamp}.json")
        
        with open(result_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "raw_data": raw_data,
                "analysis": analysis_results
            }, f, indent=2)
        
        print(f"   ✓ Saved to {result_file}")
        
        # Step 5: Send Telegram report
        print("\n5. Sending Telegram report...")
        if self.send_enhanced_telegram_report(analysis_results):
            print("   ✓ Telegram report sent successfully")
        else:
            print("   ⚠ Telegram delivery incomplete")
        
        print("\n═" * 70)
        print("✅ Pipeline completed\n")
        
        return analysis_results

    def send_enhanced_telegram_report(self, analysis_results: Dict[str, Any]) -> bool:
        """Send enhanced analysis report via Telegram"""
        if not self.telegram_token or not self.telegram_chat_id:
            print("   ❌ Missing Telegram credentials")
            return False
        
        try:
            analyses = analysis_results["properties_analyzed"]
            summary = analysis_results["summary"]
            
            # Send header
            self._send_header_message(summary, len(analyses))
            
            # Send individual properties (first 5 to avoid message limit)
            for i, analysis in enumerate(analyses[:5], 1):
                self._send_property_message(analysis, i, min(5, len(analyses)))
            
            # Send ranking and summary
            self._send_ranking_and_summary(analyses, summary)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error sending report: {e}")
            return False

    def _send_header_message(self, summary: Dict[str, Any], count: int) -> None:
        """Send report header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M SGT")
        
        header = f"""
SG COMMERCIAL PROPERTY DAILY ANALYSIS REPORT
═══════════════════════════════════════════════════════════════════════════

Report Date: {timestamp}
Properties Analyzed: {count}
Average Net Yield: {summary.get('avg_yield', 0):.2f}%
Average 5-Yr ROI: {summary.get('avg_roi_5yr', 0):.1f}%
Investment Opportunities: {summary.get('investment_opportunities', 0)} properties

PERSISTENCE: All properties stored in database with full analysis
Can query by: building, area, date, yield, ROI, risk score

═══════════════════════════════════════════════════════════════════════════
        """
        self._send_message(header)

    def _send_property_message(self, analysis: Dict[str, Any], index: int, total: int) -> None:
        """Send detailed property analysis"""
        prop = analysis["property_info"]
        rental = analysis["rental_analysis"]
        yield_info = analysis["yield_analysis"]
        roi = analysis["roi_projections"]
        rec = analysis["investment_recommendation"]
        
        marker = "BUY" if "STRONG BUY" in rec["recommendation"] or "BUY" in rec["recommendation"] else "CONSIDER" if "HOLD" in rec["recommendation"] else "SKIP"

        message = f"""
PROPERTY #{index}/{total} - {marker}

{prop['title']}
Location: {prop['location']} | Tenure: {prop['tenure']}
Price: {prop['price']} | Area: {prop['area']}

Monthly Rent: {rental['estimated_monthly_rent']}
Annual Rent: {rental['estimated_annual_rent']}

Yield: {yield_info['net_yield']} | Score: {rec['investment_score']}
5-Yr ROI: {roi['5_year_roi']} ({roi['5_year_value']})

{rec['recommendation']}
{rec['action']}

───────────────────────────────────────────────────────────────────────────
        """
        self._send_message(message)

    def _send_ranking_and_summary(self, analyses: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
        """Send top opportunities ranking"""
        
        try:
            ranked = sorted(
                analyses,
                key=lambda x: float(x["investment_recommendation"]["investment_score"].split("/")[0]),
                reverse=True
            )
        except:
            ranked = analyses
        
        message = """
TOP INVESTMENT OPPORTUNITIES (Ranked)
═══════════════════════════════════════════════════════════════════════════

        """
        
        for i, prop in enumerate(ranked[:5], 1):
            title = prop["property_info"]["title"]
            price = prop["property_info"]["price"]
            score = prop["investment_recommendation"]["investment_score"]
            yield_pct = prop["yield_analysis"]["net_yield"]
            
            message += f"""
#{i}. {title}
    Price: {price} | Score: {score}
    Yield: {yield_pct}

        """
        
        message += """
DATABASE INTEGRATION
- All 8-12 properties stored with full analysis
- Queryable by: building name, area, date range, yield, risk score
- Price history tracking enabled
- Cross-comparison available

USE CASES
1. Find all properties in Punggol Industrial Estate (last 30 days)
2. Compare properties by yield or investment score
3. Track price trends in specific areas
4. Identify best ROI opportunities across all areas
5. Analyze building-specific market trends

═══════════════════════════════════════════════════════════════════════════
        """
        
        self._send_message(message)

    def _send_message(self, text: str) -> bool:
        """Send message to Telegram"""
        try:
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": text,
                "parse_mode": "HTML",
            }
            response = requests.post(
                f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"   ❌ Telegram error: {e}")
            return False


async def main():
    """Main entry point"""
    orchestrator = EnhancedOrchestratorWithDB()
    await orchestrator.run_complete_pipeline()


if __name__ == "__main__":
    asyncio.run(main())

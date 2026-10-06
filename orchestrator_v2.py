"""
Enhanced Orchestrator - Integrated Analysis & Telegram Reporting
═══════════════════════════════════════════════════════════════════════════
Replaces the basic orchestrator with comprehensive analysis and detailed
Telegram reporting for investment decisions.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import aiohttp
import requests
from dotenv import load_dotenv

from scrapers.real_dataset_generator import generate_real_property_dataset
from scrapers.property_analyzer import analyze_all_properties


class EnhancedOrchestrator:
    """Enhanced property scraping and analysis orchestrator"""

    def __init__(self):
        load_dotenv()
        self.data_dir = "scrapers/data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
    async def run_complete_analysis(self) -> Dict[str, Any]:
        """Run complete scraping and analysis pipeline"""
        print("\n📊 Starting Enhanced Property Analysis Pipeline...")
        print("═" * 70)
        
        # Step 1: Generate or scrape properties
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
        
        # Step 3: Save results
        print("\n3. Saving results...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = os.path.join(self.data_dir, f"analysis_{timestamp}.json")
        
        with open(result_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "raw_data": raw_data,
                "analysis": analysis_results
            }, f, indent=2)
        
        print(f"   ✓ Saved to {result_file}")
        
        # Step 4: Send Telegram report
        print("\n4. Sending Telegram report...")
        if self.send_enhanced_telegram_report(analysis_results):
            print("   ✓ Telegram report sent successfully")
        else:
            print("   ⚠ Telegram delivery incomplete")
        
        print("\n═" * 70)
        print("✅ Analysis pipeline completed\n")
        
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
            
            # Send individual properties
            for i, analysis in enumerate(analyses, 1):
                self._send_property_message(analysis, i, len(analyses))
            
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

Market Snapshot: Properties under $400k with 80+ year tenure
Target: B1/B2 industrial units with positive cash flow

═══════════════════════════════════════════════════════════════════════════
        """
        self._send_message(header)

    def _send_property_message(self, analysis: Dict[str, Any], index: int, total: int) -> None:
        """Send detailed property analysis"""
        prop = analysis["property_info"]
        market = analysis["market_position"]
        rental = analysis["rental_analysis"]
        yield_info = analysis["yield_analysis"]
        roi = analysis["roi_projections"]
        profitability = analysis["profitability_metrics"]
        risk = analysis["risk_assessment"]
        rec = analysis["investment_recommendation"]
        
        # Recommendation marker
        marker = "BUY" if "STRONG BUY" in rec["recommendation"] or "BUY" in rec["recommendation"] else "CONSIDER" if "HOLD" in rec["recommendation"] else "SKIP"

        message = f"""
PROPERTY #{index}/{total} - {marker}

Location & Pricing
{prop['title']}
{prop['location']}
Price: {prop['price']} | Area: {prop['area']}
Tenure: {prop['tenure']}

Market Position
Price/SqFt: {market['price_psf']} (vs {market['market_avg_psf']})
Position: {market['price_vs_market']} vs market
Demand: {market['demand_score']} | Tier: {market['location_tier']}

Rental Analysis
Monthly Rent: {rental['estimated_monthly_rent']}
Annual Rent: {rental['estimated_annual_rent']}
Rent/SqFt: {rental['rent_per_sqft_monthly']}/month
Stability: {rental['rental_stability']}

Yield Analysis
Gross Yield: {yield_info['gross_yield']}
Net Yield: {yield_info['net_yield']}
Annual Income: {yield_info['net_annual_income']}

ROI Projections
5-Year: {roi['5_year_roi']} (Value: {roi['5_year_value']})
10-Year: {roi['10_year_roi']} (Value: {roi['10_year_value']})
20-Year: {roi['20_year_roi']} (Value: {roi['20_year_value']})

Profitability
Revenue: {profitability['annual_gross_revenue']}
Costs: {profitability['total_annual_costs']}
Net Income: {profitability['net_annual_income']}
Profit Margin: {profitability['profit_margin']}

Risk Assessment
Risk Score: {risk['risk_score']}
Tenure: {risk['tenure_risk']}
Market: {risk['market_risk']}

Investment Score: {rec['investment_score']}
Recommendation: {rec['recommendation']}
Appeal: {rec['primary_appeal']}
Target: {rec['target_investor']}
Action: {rec['action']}

URL: {prop['url']}

───────────────────────────────────────────────────────────────────────────
        """
        self._send_message(message)

    def _send_ranking_and_summary(self, analyses: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
        """Send top opportunities ranking"""
        
        # Rank by investment score
        try:
            ranked = sorted(
                analyses,
                key=lambda x: float(x["investment_recommendation"]["investment_score"].split("/")[0]),
                reverse=True
            )
        except:
            ranked = analyses
        
        message = """
TOP INVESTMENT OPPORTUNITIES (Ranked by Score)
═══════════════════════════════════════════════════════════════════════════

        """
        
        for i, prop in enumerate(ranked[:5], 1):
            title = prop["property_info"]["title"]
            location = prop["property_info"]["location"]
            price = prop["property_info"]["price"]
            score = prop["investment_recommendation"]["investment_score"]
            yield_pct = prop["yield_analysis"]["net_yield"]
            roi_5yr = prop["roi_projections"]["5_year_roi"]
            rec = prop["investment_recommendation"]["recommendation"]
            
            message += f"""
#{i}. {title}
    Location: {location}
    Price: {price}
    Score: {score}
    Yield: {yield_pct} | 5-Yr ROI: {roi_5yr}
    {rec}

        """
        
        message += """
ANALYSIS METHODOLOGY
- Valuations based on 2026 SG market data
- Conservative 2.5% annual property appreciation
- 20% expense ratio for operating costs
- Demand scores reflect market dynamics
- ROI includes property appreciation + rental income

DISCLAIMER
This analysis is for informational purposes only. Conduct thorough due 
diligence and consult with legal/financial advisors before investing.

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
    orchestrator = EnhancedOrchestrator()
    await orchestrator.run_complete_analysis()


if __name__ == "__main__":
    asyncio.run(main())

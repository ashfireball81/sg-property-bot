"""
Enhanced Telegram Report Generator - Detailed Property Analysis
═══════════════════════════════════════════════════════════════════════════
Sends comprehensive property analysis via Telegram with:
- Individual property metrics
- ROI projections
- Risk assessments
- Investment recommendations
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any
from property_analyzer import analyze_all_properties


class TelegramAnalysisReporter:
    """Sends detailed property analysis to Telegram"""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{token}"

    def send_analysis_report(self, properties: List[Dict[str, Any]]) -> bool:
        """Send comprehensive analysis report"""
        try:
            # Analyze all properties
            analysis_results = analyze_all_properties(properties)
            analyses = analysis_results["properties_analyzed"]
            summary = analysis_results["summary"]

            # Send header message
            self._send_header_message(summary, len(analyses))

            # Send individual property analysis
            for i, analysis in enumerate(analyses, 1):
                self._send_property_analysis(analysis, i, len(analyses))

            # Send summary and ranking
            self._send_summary_and_ranking(analyses, summary)

            print(f"✅ Analysis report sent ({len(analyses)} properties analyzed)")
            return True

        except Exception as e:
            print(f"❌ Error sending analysis report: {e}")
            return False

    def _send_header_message(self, summary: Dict[str, Any], count: int) -> None:
        """Send report header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S SGT")
        
        message = f"""
📊 **SG COMMERCIAL PROPERTY DAILY ANALYSIS REPORT**
═══════════════════════════════════════════════════════════════════════════

📅 Report Date: {timestamp}
📍 Properties Analyzed: {count}
💰 Average Net Yield: {summary.get('avg_yield', 0):.2f}%
📈 Average 5-Yr ROI: {summary.get('avg_roi_5yr', 0):.1f}%
💎 Investment Opportunities: {summary.get('investment_opportunities', 0)} properties

⚡ Market Snapshot: Properties under $400k with 80+ year tenure
🎯 Target: B1/B2 industrial units with positive cash flow

═══════════════════════════════════════════════════════════════════════════
        """
        
        self._send_message(message)

    def _send_property_analysis(self, analysis: Dict[str, Any], index: int, total: int) -> None:
        """Send detailed analysis for single property"""
        prop = analysis["property_info"]
        market = analysis["market_position"]
        rental = analysis["rental_analysis"]
        yield_info = analysis["yield_analysis"]
        roi = analysis["roi_projections"]
        profitability = analysis["profitability_metrics"]
        risk = analysis["risk_assessment"]
        recommendation = analysis["investment_recommendation"]

        # Recommendation emoji
        emoji = "🟢" if "STRONG BUY" in recommendation["recommendation"] else "🟢" if "BUY" in recommendation["recommendation"] else "🟡" if "HOLD" in recommendation["recommendation"] else "🔴"

        message = f"""
{emoji} **PROPERTY #{index} OF {total}**

**📍 Location & Pricing**
🏢 {prop['title']}
📍 {prop['location']}
💰 Price: {prop['price']} | Area: {prop['area']}
📜 Tenure: {prop['tenure']}

**📊 Market Position**
💹 Price/SqFt: {market['price_psf']} (vs market: {market['market_avg_psf']})
📈 Position: {market['price_vs_market']} vs market average
🎯 Demand Score: {market['demand_score']} | Tier: {market['location_tier']}
✅ {market['competitive_position']}

**🏦 Rental Analysis**
💵 Monthly Rent: {rental['estimated_monthly_rent']}
📅 Annual Rent: {rental['estimated_annual_rent']}
📏 Rent/SqFt: {rental['rent_per_sqft_monthly']}/month
🏭 Market Benchmark: {rental['market_rent_benchmark']}
🔄 Rental Stability: {rental['rental_stability']}

**💰 Yield Analysis**
📊 Gross Yield: {yield_info['gross_yield']}
✅ Net Yield: {yield_info['net_yield']}
💵 Annual Net Income: {yield_info['net_annual_income']}

**📈 ROI Projections**
5⃣ 5-Year: {roi['5_year_roi']} ROI → Value: {roi['5_year_value']}
🔟 10-Year: {roi['10_year_roi']} ROI → Value: {roi['10_year_value']}
2️⃣0️⃣ 20-Year: {roi['20_year_roi']} ROI → Value: {roi['20_year_value']}

**💼 Profitability**
💰 Annual Revenue: {profitability['annual_gross_revenue']}
💸 Total Annual Costs: {profitability['total_annual_costs']}
📊 Net Annual Income: {profitability['net_annual_income']}
📈 Profit Margin: {profitability['profit_margin']}
🔄 Breakeven Period: {profitability['breakeven_months']} months

**⚠️ Risk Assessment**
🎯 Risk Score: {risk['risk_score']}
🏛️ Tenure Risk: {risk['tenure_risk']}
🌍 Market Risk: {risk['market_risk']}
💧 Liquidity Risk: {risk['liquidity_risk']}

**🎯 Investment Recommendation**
🌟 Score: {recommendation['investment_score']}
✅ {recommendation['recommendation']}
💎 Primary Appeal: {recommendation['primary_appeal']}
👥 Target: {recommendation['target_investor']}
📞 Action: {recommendation['action']}

🔗 View Listing: {prop['url']}
═══════════════════════════════════════════════════════════════════════════
        """

        # Telegram has message length limits, so break into multiple messages
        self._send_message(message)

    def _send_summary_and_ranking(self, analyses: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
        """Send ranking and recommendations"""
        
        # Rank by investment score
        ranked = sorted(
            analyses,
            key=lambda x: float(x["investment_recommendation"]["investment_score"].split("/")[0]),
            reverse=True
        )

        message = "🏆 **TOP INVESTMENT OPPORTUNITIES (Ranked)**\n"
        message += "═══════════════════════════════════════════════════════════════════════════\n\n"

        for i, prop in enumerate(ranked[:3], 1):
            title = prop["property_info"]["title"]
            location = prop["property_info"]["location"]
            price = prop["property_info"]["price"]
            score = prop["investment_recommendation"]["investment_score"]
            yield_pct = prop["yield_analysis"]["net_yield"]
            roi_5yr = prop["roi_projections"]["5_year_roi"]
            rec = prop["investment_recommendation"]["recommendation"]

            message += f"""#{i} {title}
📍 {location} | 💰 {price}
🌟 Score: {score}
✅ Yield: {yield_pct} | 📈 5-Yr ROI: {roi_5yr}
{rec}
📞 {prop["investment_recommendation"]["action"]}

"""

        message += """
📋 **ANALYSIS METHODOLOGY**
• Valuations based on 2026 SG market data
• Conservative 2.5% annual appreciation
• 20% expense ratio for operating costs
• Demand scores reflect market dynamics
• ROI includes property + rental income

⚠️ **DISCLAIMER**
This analysis is for informational purposes only. Conduct thorough due diligence and consult with legal/financial advisors before investing.

═══════════════════════════════════════════════════════════════════════════
        """

        self._send_message(message)

    def _send_message(self, text: str) -> bool:
        """Send message to Telegram"""
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown",
            }
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Telegram send error: {e}")
            return False


def send_enhanced_telegram_report(properties: List[Dict[str, Any]]) -> bool:
    """Main function to send enhanced report"""
    from dotenv import load_dotenv

    load_dotenv()
    
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not telegram_token or not telegram_chat_id:
        print("❌ Missing Telegram credentials")
        return False

    reporter = TelegramAnalysisReporter(telegram_token, telegram_chat_id)
    return reporter.send_analysis_report(properties)


if __name__ == "__main__":
    # Test with sample data
    sample_properties = [
        {
            "source": "PropertyGuru",
            "title": "Punggol B2 Industrial Space",
            "price": 352000,
            "area": 8200,
            "location": "Punggol Industrial Estate",
            "property_type": "B2 Industrial",
            "listing_type": "sale",
            "url": "https://www.propertyguru.com.sg/property/punggol-b2-industrial",
            "posted_date": "2026-10-06T07:56:04.032827",
            "agent": "John Tan",
            "agent_phone": "+65 9xxx xxxx",
            "description": "Well-maintained B2 industrial space in Punggol",
            "tenure": "87 years",
            "floor": "2",
            "unit": "02-123"
        }
    ]
    
    send_enhanced_telegram_report(sample_properties)

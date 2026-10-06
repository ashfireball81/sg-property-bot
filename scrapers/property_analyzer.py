"""
SG Property Digital Twin - Advanced Property Analysis Engine
═══════════════════════════════════════════════════════════════════════════
Provides comprehensive independent analysis for each property listing:
- Detailed rent profitability calculations
- Market comparables & benchmarking
- ROI projections (5/10/20 year timelines)
- Price per sqft analysis
- Tenant demand & risk scoring
- Building condition & tenure analysis
- Investment recommendation ranking
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
import math


class PropertyAnalyzer:
    """Advanced analysis engine for property investment decisions"""

    # SG Market Data (2026 estimates)
    MARKET_DATA = {
        "Punggol Industrial Estate": {
            "avg_price_psf": 42,
            "avg_rent_psf_monthly": 0.50,
            "demand_score": 85,
            "location_tier": "A",
            "industrial_type": "B2 Heavy Industrial",
        },
        "Serangoon North": {
            "avg_price_psf": 45,
            "avg_rent_psf_monthly": 0.55,
            "demand_score": 82,
            "location_tier": "A",
            "industrial_type": "B2 General Industrial",
        },
        "Geylang Industrial Estate": {
            "avg_price_psf": 38,
            "avg_rent_psf_monthly": 0.45,
            "demand_score": 78,
            "location_tier": "B",
            "industrial_type": "B2 Light Industrial",
        },
        "Tampines Industrial Park": {
            "avg_price_psf": 40,
            "avg_rent_psf_monthly": 0.52,
            "demand_score": 80,
            "location_tier": "A",
            "industrial_type": "B1/B2 Mixed",
        },
        "Kranji Avenue": {
            "avg_price_psf": 35,
            "avg_rent_psf_monthly": 0.42,
            "demand_score": 72,
            "location_tier": "C",
            "industrial_type": "B2 Warehouse",
        },
    }

    def __init__(self):
        self.analysis_timestamp = datetime.now().isoformat()

    def analyze_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a single property listing
        
        Args:
            property_data: Property listing dictionary
            
        Returns:
            Dictionary with detailed analysis metrics
        """
        location = property_data.get("location", "Unknown")
        price = float(property_data.get("price", 0))
        area = float(property_data.get("area", 0))
        tenure = property_data.get("tenure", "Unknown")
        title = property_data.get("title", "Unknown")

        # Get market comparables
        market_comp = self._get_market_comparables(location)
        
        # Override with specific market data if available
        if "market_data" in property_data:
            market_comp["demand_score"] = property_data["market_data"].get("demand_score", market_comp["demand_score"])
            market_comp["avg_rent_psf_monthly"] = property_data["market_data"].get("avg_monthly_rent_psf", market_comp["avg_rent_psf_monthly"])

        # Calculate metrics
        price_psf = self._calculate_price_psf(price, area)
        monthly_rent_estimate = self._estimate_monthly_rent(
            area, market_comp["avg_rent_psf_monthly"]
        )
        annual_rent = monthly_rent_estimate * 12

        # Calculate yields
        gross_yield = self._calculate_gross_yield(annual_rent, price)
        net_yield = self._calculate_net_yield(gross_yield)

        # ROI projections
        roi_5yr, roi_10yr, roi_20yr = self._calculate_roi_projections(
            price, annual_rent, market_comp["avg_price_psf"]
        )

        # Risk and demand scoring
        risk_score = self._calculate_risk_score(
            price_psf, market_comp["avg_price_psf"], tenure, market_comp["demand_score"]
        )
        demand_score = market_comp["demand_score"]

        # Investment ranking
        investment_score = self._calculate_investment_score(
            net_yield, roi_5yr, risk_score, demand_score, price
        )

        # Profitability analysis
        profitability = self._analyze_profitability(
            monthly_rent_estimate, area, price, annual_rent
        )

        # Building analysis
        building_analysis = self._analyze_building(property_data, market_comp)

        return {
            "property_info": {
                "title": title,
                "location": location,
                "price": f"${price:,.0f}",
                "area": f"{area:,.0f} sqft",
                "tenure": tenure,
                "url": property_data.get("url", "N/A"),
            },
            "market_position": {
                "price_psf": f"${price_psf:.2f}",
                "market_avg_psf": f"${market_comp['avg_price_psf']:.2f}",
                "price_vs_market": f"{((price_psf / market_comp['avg_price_psf'] - 1) * 100):+.1f}%",
                "location_tier": market_comp["location_tier"],
                "demand_score": f"{demand_score}/100",
                "competitive_position": self._get_competitive_position(
                    price_psf, market_comp["avg_price_psf"]
                ),
            },
            "rental_analysis": {
                "estimated_monthly_rent": f"${monthly_rent_estimate:,.0f}",
                "estimated_annual_rent": f"${annual_rent:,.0f}",
                "rent_per_sqft_monthly": f"${monthly_rent_estimate / area:.2f}",
                "market_rent_benchmark": f"${area * market_comp['avg_rent_psf_monthly']:,.0f}/month",
                "rental_stability": "HIGH"
                if demand_score > 80
                else "MEDIUM"
                if demand_score > 70
                else "LOW",
            },
            "yield_analysis": {
                "gross_yield": f"{gross_yield:.2f}%",
                "net_yield": f"{net_yield:.2f}%",
                "net_annual_income": f"${annual_rent * (net_yield / 100):,.0f}",
                "yield_vs_target": f"{(net_yield - 12):+.2f}%" if net_yield >= 12 else "BELOW TARGET",
            },
            "roi_projections": {
                "5_year_roi": f"{roi_5yr:.1f}%",
                "5_year_value": f"${price * (1 + roi_5yr / 100):,.0f}",
                "10_year_roi": f"{roi_10yr:.1f}%",
                "10_year_value": f"${price * (1 + roi_10yr / 100):,.0f}",
                "20_year_roi": f"{roi_20yr:.1f}%",
                "20_year_value": f"${price * (1 + roi_20yr / 100):,.0f}",
                "projection_method": "Conservative market growth + cumulative rental returns",
            },
            "profitability_metrics": profitability,
            "risk_assessment": {
                "risk_score": f"{risk_score}/100 ({'LOW' if risk_score < 40 else 'MEDIUM' if risk_score < 70 else 'HIGH'})",
                "tenure_risk": self._assess_tenure_risk(tenure),
                "market_risk": self._assess_market_risk(demand_score),
                "liquidity_risk": "LOW"
                if demand_score > 80
                else "MEDIUM"
                if demand_score > 70
                else "HIGH",
                "key_risks": self._identify_risks(tenure, price_psf, market_comp["avg_price_psf"]),
            },
            "building_analysis": building_analysis,
            "investment_recommendation": {
                "investment_score": f"{investment_score}/100",
                "recommendation": self._get_recommendation(investment_score),
                "primary_appeal": self._get_primary_appeal(
                    net_yield, roi_5yr, risk_score, investment_score
                ),
                "target_investor": self._get_target_investor(
                    net_yield, risk_score, price, roi_5yr
                ),
                "action": self._get_action_recommendation(
                    investment_score, net_yield, price
                ),
            },
            "analysis_metadata": {
                "analyzed_at": self.analysis_timestamp,
                "market_data_source": "SG 2026 Market Research",
                "methodology": "Conservative valuation with local market benchmarks",
            },
        }

    def _get_market_comparables(self, location: str) -> Dict[str, Any]:
        """Get market data for location"""
        return self.MARKET_DATA.get(
            location,
            {
                "avg_price_psf": 40,
                "avg_rent_psf_monthly": 6.0,
                "demand_score": 75,
                "location_tier": "B",
                "industrial_type": "B2 General Industrial",
            },
        )

    def _calculate_price_psf(self, price: float, area: float) -> float:
        """Calculate price per square foot"""
        return price / area if area > 0 else 0

    def _estimate_monthly_rent(self, area: float, avg_rent_psf: float) -> float:
        """Estimate monthly rent based on area and market rates"""
        return area * avg_rent_psf

    def _calculate_gross_yield(self, annual_rent: float, price: float) -> float:
        """Calculate gross rental yield"""
        return (annual_rent / price * 100) if price > 0 else 0

    def _calculate_net_yield(self, gross_yield: float) -> float:
        """Calculate net yield (accounting for expenses)"""
        # Assume 20% maintenance, tax, insurance costs
        return gross_yield * 0.8

    def _calculate_roi_projections(
        self, price: float, annual_rent: float, avg_price_psf: float
    ) -> Tuple[float, float, float]:
        """Calculate 5, 10, 20 year ROI projections"""
        # Conservative 2.5% annual property appreciation
        appreciation_rate = 0.025
        property_appreciation_5yr = (price * ((1 + appreciation_rate) ** 5 - 1)) / price * 100
        property_appreciation_10yr = (price * ((1 + appreciation_rate) ** 10 - 1)) / price * 100
        property_appreciation_20yr = (price * ((1 + appreciation_rate) ** 20 - 1)) / price * 100

        # Add cumulative rental income
        roi_5yr = property_appreciation_5yr + (annual_rent / price * 100 * 5)
        roi_10yr = property_appreciation_10yr + (annual_rent / price * 100 * 10)
        roi_20yr = property_appreciation_20yr + (annual_rent / price * 100 * 20)

        return roi_5yr, roi_10yr, roi_20yr

    def _calculate_risk_score(
        self, price_psf: float, market_avg_psf: float, tenure: str, demand: int
    ) -> float:
        """Calculate overall risk score (0-100, lower is better)"""
        risk = 50

        # Price deviation risk
        price_ratio = price_psf / market_avg_psf if market_avg_psf > 0 else 1
        if price_ratio < 0.85:
            risk -= 15  # Undervalued (low risk)
        elif price_ratio > 1.15:
            risk += 15  # Overvalued (high risk)

        # Tenure risk
        try:
            tenure_years = int(tenure.split()[0])
            if tenure_years < 50:
                risk += 20
            elif tenure_years < 70:
                risk += 10
        except:
            risk += 10

        # Demand risk
        if demand < 60:
            risk += 15
        elif demand < 75:
            risk += 5

        return min(100, max(0, risk))

    def _get_competitive_position(self, price_psf: float, market_avg: float) -> str:
        """Determine competitive position vs market"""
        ratio = price_psf / market_avg if market_avg > 0 else 1
        if ratio < 0.90:
            return "STRONG BUY - Well below market"
        elif ratio < 0.98:
            return "GOOD VALUE - Below market average"
        elif ratio <= 1.02:
            return "FAIR VALUE - At market average"
        elif ratio < 1.10:
            return "SLIGHTLY ABOVE - Minor premium"
        else:
            return "OVERVALUED - Above market"

    def _analyze_profitability(
        self, monthly_rent: float, area: float, price: float, annual_rent: float
    ) -> Dict[str, str]:
        """Detailed profitability analysis"""
        # Assume typical costs
        annual_maintenance = price * 0.02  # 2% of price
        annual_tax = price * 0.012  # 1.2% property tax
        annual_insurance = price * 0.003  # 0.3% insurance
        annual_overhead = 800  # Miscellaneous

        total_annual_costs = (
            annual_maintenance + annual_tax + annual_insurance + annual_overhead
        )
        net_annual_income = annual_rent - total_annual_costs
        annual_roi = (net_annual_income / price * 100) if price > 0 else 0

        return {
            "annual_gross_revenue": f"${annual_rent:,.0f}",
            "annual_maintenance": f"${annual_maintenance:,.0f}",
            "annual_property_tax": f"${annual_tax:,.0f}",
            "annual_insurance": f"${annual_insurance:,.0f}",
            "total_annual_costs": f"${total_annual_costs:,.0f}",
            "net_annual_income": f"${net_annual_income:,.0f}",
            "profit_margin": f"{(net_annual_income / annual_rent * 100) if annual_rent > 0 else 0:.1f}%",
            "breakeven_months": f"{(price / (monthly_rent - total_annual_costs / 12)):.1f}" if (monthly_rent - total_annual_costs / 12) > 0 else "N/A",
        }

    def _analyze_building(
        self, property_data: Dict[str, Any], market_comp: Dict[str, Any]
    ) -> Dict[str, str]:
        """Analyze building characteristics"""
        tenure = property_data.get("tenure", "Unknown")
        property_type = property_data.get("property_type", "Unknown")

        return {
            "property_type": property_type,
            "building_category": market_comp.get("industrial_type", "B2 Industrial"),
            "tenure": tenure,
            "tenure_status": self._assess_tenure_risk(tenure),
            "floor": f"Floor {property_data.get('floor', 'N/A')}",
            "unit": property_data.get("unit", "N/A"),
            "size_category": "Large"
            if float(property_data.get("area", 0)) > 8000
            else "Medium"
            if float(property_data.get("area", 0)) > 5000
            else "Small",
            "location_logistics": "Excellent access" if market_comp["demand_score"] > 80 else "Good access" if market_comp["demand_score"] > 70 else "Moderate access",
        }

    def _assess_tenure_risk(self, tenure: str) -> str:
        """Assess tenure risk level"""
        try:
            years = int(tenure.split()[0])
            if years >= 90:
                return "VERY LOW - Lease security excellent"
            elif years >= 80:
                return "LOW - Lease secure"
            elif years >= 70:
                return "MEDIUM - Monitor renewal timeline"
            elif years >= 60:
                return "MEDIUM-HIGH - Approaching renewal window"
            else:
                return "HIGH - Renewal recommended within 5 years"
        except:
            return "UNKNOWN - Verify lease terms"

    def _assess_market_risk(self, demand: int) -> str:
        """Assess market demand risk"""
        if demand >= 85:
            return "LOW - High demand, strong market"
        elif demand >= 75:
            return "MEDIUM - Stable demand"
        elif demand >= 60:
            return "MEDIUM-HIGH - Softer demand"
        else:
            return "HIGH - Weak market conditions"

    def _identify_risks(self, tenure: str, price_psf: float, market_avg: float) -> List[str]:
        """Identify key investment risks"""
        risks = []

        try:
            years = int(tenure.split()[0])
            if years < 70:
                risks.append("Lease approaching renewal - refinancing may be needed")
        except:
            pass

        ratio = price_psf / market_avg if market_avg > 0 else 1
        if ratio > 1.15:
            risks.append("Premium valuation - less margin of safety")

        if not risks:
            risks.append("Low-risk profile - good fundamentals")

        return risks

    def _calculate_investment_score(
        self, net_yield: float, roi_5yr: float, risk_score: float, demand_score: int, price: float
    ) -> float:
        """Calculate overall investment score (0-100)"""
        score = 50

        # Yield factor (max +30)
        if net_yield >= 12:
            score += min(30, 15 + (net_yield - 12) * 2)
        elif net_yield >= 10:
            score += 20
        elif net_yield >= 8:
            score += 10

        # ROI factor (max +20)
        if roi_5yr >= 60:
            score += 20
        elif roi_5yr >= 40:
            score += 15
        elif roi_5yr >= 20:
            score += 10

        # Risk factor (max -20)
        if risk_score > 70:
            score -= 15
        elif risk_score > 50:
            score -= 8

        # Demand factor (max +10)
        if demand_score >= 85:
            score += 10
        elif demand_score >= 75:
            score += 5

        # Price factor (max +10)
        if price < 400000:
            score += min(10, (400000 - price) / 40000)

        return min(100, max(0, score))

    def _get_recommendation(self, score: float) -> str:
        """Get investment recommendation"""
        if score >= 80:
            return "🟢 STRONG BUY - Excellent opportunity"
        elif score >= 70:
            return "🟢 BUY - Good value, worth pursuing"
        elif score >= 60:
            return "🟡 HOLD - Monitor for improvement"
        elif score >= 50:
            return "🟡 WEAK - Below target criteria"
        else:
            return "🔴 AVOID - Does not meet criteria"

    def _get_primary_appeal(self, yield_pct: float, roi_5yr: float, risk: float, score: float) -> str:
        """Identify primary investment appeal"""
        if yield_pct >= 14:
            return "INCOME GENERATION - High rental yields"
        elif roi_5yr >= 50:
            return "CAPITAL APPRECIATION - Strong growth potential"
        elif risk < 40 and score > 65:
            return "BALANCED APPROACH - Moderate risk/return"
        else:
            return "SPECULATIVE - Requires careful due diligence"

    def _get_target_investor(self, yield_pct: float, risk: float, price: float, roi_5yr: float) -> str:
        """Identify target investor profile"""
        if yield_pct >= 12 and risk < 50:
            return "INCOME-FOCUSED INVESTORS - Seeking stable cash flow"
        elif roi_5yr >= 50 and risk < 60:
            return "GROWTH INVESTORS - Capital appreciation focus"
        elif price < 400000 and roi_5yr > 30:
            return "FIRST-TIME BUYERS - Affordable entry point with upside"
        else:
            return "EXPERIENCED INVESTORS - Can manage complexity"

    def _get_action_recommendation(self, score: float, yield_pct: float, price: float) -> str:
        """Get specific action recommendation"""
        if score >= 75 and yield_pct >= 12:
            return "📞 CONTACT AGENT - Schedule viewing immediately"
        elif score >= 65 and price < 400000:
            return "📋 SHORTLIST - Add to watchlist for monitoring"
        elif score >= 55:
            return "🔍 INVESTIGATE - Do deep due diligence on building"
        else:
            return "⏭️ SKIP - Continue searching for better opportunities"


def analyze_all_properties(properties: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze all properties in a batch"""
    analyzer = PropertyAnalyzer()
    analyses = []
    summary_stats = {
        "total_analyzed": 0,
        "avg_yield": 0,
        "avg_roi_5yr": 0,
        "avg_price": 0,
        "investment_opportunities": 0,
    }

    for prop in properties:
        analysis = analyzer.analyze_property(prop)
        analyses.append(analysis)

    # Calculate summary statistics
    if analyses:
        summary_stats["total_analyzed"] = len(analyses)
        yields = []
        rois = []
        prices = []

        for a in analyses:
            try:
                yields.append(float(a["yield_analysis"]["net_yield"].rstrip("%")))
                rois.append(float(a["roi_projections"]["5_year_roi"].rstrip("%")))
                prices.append(float(a["property_info"]["price"].replace("$", "").replace(",", "")))
            except:
                pass

        if yields:
            summary_stats["avg_yield"] = sum(yields) / len(yields)
        if rois:
            summary_stats["avg_roi_5yr"] = sum(rois) / len(rois)
        if prices:
            summary_stats["avg_price"] = sum(prices) / len(prices)

        # Count investment opportunities
        summary_stats["investment_opportunities"] = sum(
            1 for a in analyses if "STRONG BUY" in a["investment_recommendation"]["recommendation"] or "BUY" in a["investment_recommendation"]["recommendation"]
        )

    return {
        "analysis_date": datetime.now().isoformat(),
        "properties_analyzed": analyses,
        "summary": summary_stats,
    }

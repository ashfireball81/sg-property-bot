"""
Property Analytics and Cross-Comparison Tools
═══════════════════════════════════════════════════════════════════════════
Query and compare properties by building, area, date, and investment metrics
"""

from database_persistence import PropertyDatabase
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json


class PropertyAnalytics:
    """Analytics and cross-comparison for stored properties"""

    def __init__(self):
        self.db = PropertyDatabase()
        if not self.db.connect():
            raise Exception("Cannot connect to database")

    def close(self):
        """Close database connection"""
        self.db.close()

    def compare_areas(self, days: int = 30) -> Dict[str, Any]:
        """Compare all areas by key metrics"""
        comparisons = self.db.get_cross_area_comparison(days)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'period_days': days,
            'areas': comparisons,
            'summary': {
                'total_areas': len(comparisons),
                'total_properties': sum(a['properties'] for a in comparisons),
                'avg_yield_all_areas': sum(a['avg_yield'] * a['properties'] for a in comparisons) / sum(a['properties'] for a in comparisons) if comparisons else 0,
                'best_yield_area': max(comparisons, key=lambda x: x['avg_yield'])['location'] if comparisons else 'N/A',
                'best_score_area': max(comparisons, key=lambda x: x['avg_score'])['location'] if comparisons else 'N/A',
            }
        }
        
        return result

    def compare_building(self, building_name: str, days: int = 30) -> Dict[str, Any]:
        """Compare all properties in a building"""
        properties = self.db.get_properties_by_building(building_name, days)
        
        if not properties:
            return {
                'building': building_name,
                'status': 'No properties found',
                'properties': []
            }
        
        prices = [p[3] for p in properties if p[3]]
        yields = [p[-3] for p in properties if p[-3]]
        scores = [p[-2] for p in properties if p[-2]]
        
        result = {
            'building': building_name,
            'properties_count': len(properties),
            'date_range': {
                'first': properties[-1][-1].isoformat() if properties[-1][-1] else None,
                'latest': properties[0][-1].isoformat() if properties[0][-1] else None,
            },
            'price_analysis': {
                'count': len(prices),
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'avg': sum(prices) / len(prices) if prices else 0,
                'median': sorted(prices)[len(prices)//2] if prices else 0,
            },
            'yield_analysis': {
                'count': len(yields),
                'min': min(yields) if yields else 0,
                'max': max(yields) if yields else 0,
                'avg': sum(yields) / len(yields) if yields else 0,
            },
            'score_analysis': {
                'count': len(scores),
                'min': min(scores) if scores else 0,
                'max': max(scores) if scores else 0,
                'avg': sum(scores) / len(scores) if scores else 0,
            },
            'properties': [
                {
                    'title': p[2],
                    'location': p[5],
                    'price': float(p[3]) if p[3] else 0,
                    'area': float(p[4]) if p[4] else 0,
                    'price_psft': float(p[3] / p[4]) if (p[3] and p[4]) else 0,
                    'yield': float(p[-3]) if p[-3] else 0,
                    'score': float(p[-2]) if p[-2] else 0,
                    'recommendation': p[-1],
                    'date': p[-1].isoformat() if p[-1] else None,
                }
                for p in properties
            ]
        }
        
        return result

    def compare_area(self, area_name: str, days: int = 30) -> Dict[str, Any]:
        """Compare all properties in an area"""
        summary = self.db.get_area_summary(area_name)
        properties = self.db.get_properties_by_area(area_name, days)
        
        result = {
            'area': area_name,
            'summary': summary,
            'property_count': len(properties),
            'properties': [
                {
                    'title': p[2],
                    'price': float(p[3]) if p[3] else 0,
                    'area': float(p[4]) if p[4] else 0,
                    'price_psft': float(p[3] / p[4]) if (p[3] and p[4]) else 0,
                    'tenure': p[13],
                    'yield': float(p[-3]) if p[-3] else 0,
                    'score': float(p[-2]) if p[-2] else 0,
                    'recommendation': p[-1],
                    'date': p[-1].isoformat() if len(p) > 14 and p[-1] else None,
                }
                for p in properties
            ]
        }
        
        return result

    def price_trend_analysis(self, area_name: str, days: int = 30) -> Dict[str, Any]:
        """Analyze price trends in an area"""
        properties = self.db.get_properties_by_area(area_name, days)
        
        if not properties:
            return {
                'area': area_name,
                'status': 'No data',
                'trend': 'N/A'
            }
        
        # Group by date
        by_date = {}
        for p in properties:
            date_str = p[-1].date().isoformat() if len(p) > 14 and p[-1] else None
            if date_str:
                if date_str not in by_date:
                    by_date[date_str] = []
                by_date[date_str].append(float(p[3]) if p[3] else 0)
        
        # Calculate trends
        dates = sorted(by_date.keys())
        avg_prices_by_date = [
            {
                'date': date,
                'count': len(by_date[date]),
                'avg_price': sum(by_date[date]) / len(by_date[date]),
                'min_price': min(by_date[date]),
                'max_price': max(by_date[date]),
            }
            for date in dates
        ]
        
        # Trend direction
        if len(avg_prices_by_date) > 1:
            first_price = avg_prices_by_date[0]['avg_price']
            last_price = avg_prices_by_date[-1]['avg_price']
            change = ((last_price - first_price) / first_price) * 100 if first_price > 0 else 0
            trend = 'UP' if change > 0.5 else 'DOWN' if change < -0.5 else 'STABLE'
        else:
            change = 0
            trend = 'INSUFFICIENT_DATA'
        
        return {
            'area': area_name,
            'period_days': days,
            'date_range': {
                'first': dates[0] if dates else None,
                'latest': dates[-1] if dates else None,
            },
            'price_trend': {
                'direction': trend,
                'change_pct': round(change, 2),
                'prices_by_date': avg_prices_by_date,
            }
        }

    def yield_comparison(self, limit: int = 20) -> Dict[str, Any]:
        """Compare yields across all properties"""
        opportunities = self.db.get_best_opportunities(days=30, limit=limit)
        
        if not opportunities:
            return {
                'status': 'No data',
                'opportunities': []
            }
        
        yields = [o['yield'] for o in opportunities if o['yield']]
        
        return {
            'opportunities_count': len(opportunities),
            'yield_stats': {
                'min': min(yields) if yields else 0,
                'max': max(yields) if yields else 0,
                'avg': sum(yields) / len(yields) if yields else 0,
                'median': sorted(yields)[len(yields)//2] if yields else 0,
            },
            'top_opportunities': opportunities
        }

    def roi_analysis_by_area(self, area_name: str) -> Dict[str, Any]:
        """Analyze ROI potential by area"""
        summary = self.db.get_area_summary(area_name)
        
        if not summary:
            return {'area': area_name, 'status': 'No data'}
        
        return {
            'area': area_name,
            'roi_potential': {
                'avg_yield': round(summary.get('avg_yield', 0), 2),
                'avg_investment_score': round(summary.get('avg_score', 0), 2),
                'buy_opportunities': summary.get('buy_opportunities', 0),
                'total_properties': summary.get('property_count', 0),
                'price_range': {
                    'min': summary.get('min_price', 0),
                    'max': summary.get('max_price', 0),
                    'avg': summary.get('avg_price', 0),
                },
                'estimate_5year_roi': round((summary.get('avg_yield', 0) * 5) + 12.5, 2),
                'estimate_10year_roi': round((summary.get('avg_yield', 0) * 10) + 25, 2),
            }
        }

    def export_comparison_report(self, filename: str = None) -> str:
        """Export complete comparison report to JSON"""
        if filename is None:
            filename = f"property_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'generated': datetime.now().isoformat(),
            'areas_comparison': self.compare_areas(),
            'yield_comparison': self.yield_comparison(),
            'areas': {}
        }
        
        # Add analysis for each area
        areas = ['Punggol Industrial Estate', 'Serangoon North', 'Geylang Industrial Estate',
                'Tampines Industrial Park', 'Kranji Avenue', 'Jurong East Industrial Zone',
                'Tuas South Industrial Estate', 'Woodlands Industrial Zone']
        
        for area in areas:
            report['areas'][area] = {
                'comparison': self.compare_area(area),
                'price_trend': self.price_trend_analysis(area),
                'roi_analysis': self.roi_analysis_by_area(area),
            }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename


def run_analytics():
    """Run complete analytics suite"""
    print("\n📊 Running Property Analytics...")
    print("═" * 70)
    
    analytics = PropertyAnalytics()
    
    try:
        # Area comparison
        print("\n1. Cross-Area Comparison")
        areas_comp = analytics.compare_areas()
        print(f"   Total areas: {areas_comp['summary']['total_areas']}")
        print(f"   Total properties: {areas_comp['summary']['total_properties']}")
        print(f"   Avg yield (all): {areas_comp['summary']['avg_yield_all_areas']:.2f}%")
        print(f"   Best yield area: {areas_comp['summary']['best_yield_area']}")
        print(f"   Best score area: {areas_comp['summary']['best_score_area']}")
        
        # Yield comparison
        print("\n2. Top Investment Opportunities")
        yield_comp = analytics.yield_comparison()
        print(f"   Opportunities analyzed: {yield_comp['opportunities_count']}")
        print(f"   Yield range: {yield_comp['yield_stats']['min']:.2f}% - {yield_comp['yield_stats']['max']:.2f}%")
        print(f"   Average yield: {yield_comp['yield_stats']['avg']:.2f}%")
        
        # Export report
        print("\n3. Exporting Full Report")
        filename = analytics.export_comparison_report()
        print(f"   ✓ Report saved: {filename}")
        
        print("\n✅ Analytics complete")
        
    except Exception as e:
        print(f"✗ Analytics failed: {e}")
    
    finally:
        analytics.close()


if __name__ == "__main__":
    run_analytics()

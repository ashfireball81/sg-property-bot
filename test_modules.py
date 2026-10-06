"""Quick test script for new modules"""
import sys
sys.path.insert(0, '/Users/ash_f/Desktop/python/sg-property-bot')

from scrapers.real_dataset_generator import generate_real_property_dataset
from scrapers.property_analyzer import analyze_all_properties

print("\n1. Testing Real Dataset Generator...")
data = generate_real_property_dataset()
print(f"   Generated {data['total_properties']} properties")
for source, info in data['sources'].items():
    print(f"   - {source}: {info['count']} properties")
    
print("\n2. Testing Property Analyzer...")
all_props = []
for source, info in data['sources'].items():
    all_props.extend(info['properties'])

analysis = analyze_all_properties(all_props)
print(f"   Analyzed {analysis['summary']['total_analyzed']} properties")
print(f"   - Avg Net Yield: {analysis['summary']['avg_yield']:.2f}%")
print(f"   - Avg 5-Yr ROI: {analysis['summary']['avg_roi_5yr']:.1f}%")
print(f"   - Investment Opportunities: {analysis['summary']['investment_opportunities']}")

print("\n3. Sample property analysis:")
first_analysis = analysis['properties_analyzed'][0]
print(f"   Property: {first_analysis['property_info']['title']}")
print(f"   Price: {first_analysis['property_info']['price']}")
print(f"   Net Yield: {first_analysis['yield_analysis']['net_yield']}")
print(f"   Investment Score: {first_analysis['investment_recommendation']['investment_score']}")
print(f"   Recommendation: {first_analysis['investment_recommendation']['recommendation']}")

print("\n✅ All modules working!")

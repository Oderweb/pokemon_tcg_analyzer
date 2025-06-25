from data_collector import PokemonDataCollector
from roi_calculator import ROICalculator
import time

def main():
    print("🎯 Pokemon TCG Investment Analyzer")
    print("=" * 50)
    
    # Initialize components
    collector = PokemonDataCollector()
    calculator = ROICalculator()
    
    # Test API connection first
    print("Testing API connection...")
    if not collector.test_api_connection():
        print("❌ Cannot connect to API. Please check your .env file and API key.")
        return
    
    # Pokemon sets to analyze (use search terms that work)
    sets_to_analyze = [
        "evolving skies",
        "brilliant stars",
        "lost origin", 
        "silver tempest",
        "paldea evolved",
        "obsidian flames",
        "paradox rift",
        "destined rivals"
    ]
    
    print(f"\n🎯 Analyzing {len(sets_to_analyze)} Pokemon sets...")
    print("=" * 60)
    
    all_results = []
    
    for set_name in sets_to_analyze:
        print(f"\n📦 Analyzing '{set_name}'...")
        
        # Get specific products (ETBs and Booster Boxes)
        products_data = collector.get_specific_products(set_name)
        etbs = products_data['etb']
        booster_boxes = products_data['booster_boxes']
        
        # Get top cards for pull value calculation
        print(f"   Getting top cards for '{set_name}'...")
        top_cards = collector.get_cards_by_set_name(set_name, limit=20)
        
        # Analyze ETBs
        for etb in etbs:
            analysis = calculator.analyze_product(etb, top_cards)
            if analysis:
                analysis['category'] = 'Elite Trainer Box'
                all_results.append(analysis)
                print(f"   📊 ETB: {analysis['product_name']}")
                print(f"       Price: €{analysis['current_price']} | ROI: {analysis['roi_percentage']}% | Risk: {analysis['risk_score']}/5")
        
        # Analyze Booster Boxes
        for box in booster_boxes:
            analysis = calculator.analyze_product(box, top_cards)
            if analysis:
                analysis['category'] = 'Booster Box'
                all_results.append(analysis)
                print(f"   📊 Booster Box: {analysis['product_name']}")
                print(f"       Price: €{analysis['current_price']} | ROI: {analysis['roi_percentage']}% | Risk: {analysis['risk_score']}/5")
        
        # Small delay to be nice to the API
        time.sleep(1)
    
    if not all_results:
        print("❌ No results found. Check your API key and connection.")
        return
    
    # Sort results by ROI (highest first)
    all_results.sort(key=lambda x: x['roi_percentage'], reverse=True)
    
    # Save results to file
    collector.save_data_to_file(all_results, "pokemon_investment_analysis")
    
    # Display top opportunities
    print("\n" + "=" * 80)
    print("🏆 TOP 15 INVESTMENT OPPORTUNITIES")
    print("=" * 80)
    
    for i, result in enumerate(all_results[:15], 1):
        category_emoji = "📦" if result['category'] == 'Elite Trainer Box' else "📦📦"
        
        print(f"\n{i:2d}. {category_emoji} {result['product_name']}")
        print(f"    💰 Price: €{result['current_price']}")
        print(f"    📈 ROI: {result['roi_percentage']}%")
        print(f"    ⚠️  Risk: {result['risk_score']}/5")
        print(f"    📅 Set: {result['set_name']} ({result['release_date']})")
        print(f"    📦 Type: {result['category']} ({result['packs_per_box']} packs)")
        print(f"    💎 Est. Pull Value: €{result['estimated_pull_value']}")
    
    # Category breakdown
    print("\n" + "=" * 60)
    print("📊 ANALYSIS BY CATEGORY")
    print("=" * 60)
    
    etb_results = [r for r in all_results if r['category'] == 'Elite Trainer Box']
    box_results = [r for r in all_results if r['category'] == 'Booster Box']
    
    print(f"\n📦 ELITE TRAINER BOXES ({len(etb_results)} analyzed):")
    if etb_results:
        avg_etb_roi = sum(r['roi_percentage'] for r in etb_results) / len(etb_results)
        best_etb = max(etb_results, key=lambda x: x['roi_percentage'])
        print(f"   Average ROI: {avg_etb_roi:.1f}%")
        print(f"   Best Opportunity: {best_etb['product_name']} ({best_etb['roi_percentage']}%)")
    
    print(f"\n📦📦 BOOSTER BOXES ({len(box_results)} analyzed):")
    if box_results:
        avg_box_roi = sum(r['roi_percentage'] for r in box_results) / len(box_results)
        best_box = max(box_results, key=lambda x: x['roi_percentage'])
        print(f"   Average ROI: {avg_box_roi:.1f}%")
        print(f"   Best Opportunity: {best_box['product_name']} ({best_box['roi_percentage']}%)")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("📊 OVERALL SUMMARY")
    print("=" * 60)
    
    positive_roi = [r for r in all_results if r['roi_percentage'] > 0]
    high_roi = [r for r in all_results if r['roi_percentage'] > 50]
    low_risk = [r for r in all_results if r['risk_score'] <= 3.0]
    
    avg_roi = sum(r['roi_percentage'] for r in all_results) / len(all_results)
    avg_risk = sum(r['risk_score'] for r in all_results) / len(all_results)
    
    print(f"Total products analyzed: {len(all_results)}")
    print(f"Products with positive ROI: {len(positive_roi)} ({len(positive_roi)/len(all_results)*100:.1f}%)")
    print(f"Products with >50% ROI: {len(high_roi)}")
    print(f"Products with low risk (≤3.0): {len(low_risk)}")
    print(f"Average ROI: {avg_roi:.1f}%")
    print(f"Average Risk Score: {avg_risk:.1f}/5")
    
    # Investment recommendations
    best_opportunity = all_results[0] if all_results else None
    if best_opportunity:
        print(f"\n🎯 BEST OVERALL OPPORTUNITY:")
        print(f"   {best_opportunity['product_name']}")
        print(f"   ROI: {best_opportunity['roi_percentage']}% | Risk: {best_opportunity['risk_score']}/5")
        print(f"   Price: €{best_opportunity['current_price']} | Category: {best_opportunity['category']}")
    
    # Safe investments (good ROI + low risk)
    safe_investments = [r for r in all_results if r['roi_percentage'] > 20 and r['risk_score'] <= 3.0]
    if safe_investments:
        print(f"\n🛡️  SAFEST HIGH-ROI INVESTMENTS:")
        for i, inv in enumerate(safe_investments[:3], 1):
            print(f"   {i}. {inv['product_name']} - ROI: {inv['roi_percentage']}%, Risk: {inv['risk_score']}/5")

if __name__ == "__main__":
    main()
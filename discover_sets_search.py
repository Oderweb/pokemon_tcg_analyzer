from data_collector import PokemonDataCollector

def main():
    print("🔍 Pokemon TCG Set Discovery (Using Search)")
    print("=" * 60)
    
    collector = PokemonDataCollector()
    
    # Test API connection
    if not collector.test_api_connection():
        print("❌ Cannot connect to API. Check your .env file.")
        return
    
    # Discover sets using search functionality
    found_sets = collector.discover_available_sets()
    
    if not found_sets:
        print("❌ No sets discovered.")
        return
    
    print(f"\n✅ Successfully discovered {len(found_sets)} sets!")
    print("=" * 80)
    print(f"{'SEARCH TERM':<20} {'SET NAME':<25} {'SLUG':<30} {'PRODUCTS'}")
    print("-" * 80)
    
    for set_info in found_sets:
        search_term = set_info['search_term'][:18]
        name = set_info['name'][:23]
        slug = set_info['slug'][:28]
        products = set_info['products_found']
        
        print(f"{search_term:<20} {name:<25} {slug:<30} {products}")
    
    print(f"\n🎯 TESTING SPECIFIC PRODUCT SEARCHES:")
    print("=" * 50)
    
    # Test specific searches for popular sets
    test_sets = ["evolving skies", "brilliant stars", "destined rivals"]
    
    for set_name in test_sets:
        print(f"\nTesting '{set_name}':")
        products_data = collector.get_specific_products(set_name)
        
        etbs = products_data['etb']
        boxes = products_data['booster_boxes']
        
        print(f"  📦 Elite Trainer Boxes: {len(etbs)}")
        for etb in etbs[:2]:  # Show first 2
            print(f"     • {etb.get('name', 'Unknown')} - €{etb.get('prices', {}).get('cardmarket', {}).get('lowest', 'N/A')}")
        
        print(f"  📦📦 Booster Boxes: {len(boxes)}")
        for box in boxes[:2]:  # Show first 2
            print(f"     • {box.get('name', 'Unknown')} - €{box.get('prices', {}).get('cardmarket', {}).get('lowest', 'N/A')}")

if __name__ == "__main__":
    main()
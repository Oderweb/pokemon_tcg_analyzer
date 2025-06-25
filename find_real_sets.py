from data_collector import PokemonDataCollector

def main():
    print("🔍 Finding REAL Pokemon Set Slugs")
    print("=" * 50)
    
    collector = PokemonDataCollector()
    
    # Test API connection
    if not collector.test_api_connection():
        print("❌ Cannot connect to API. Check your .env file.")
        return
    
    # Get a larger sample to find all sets
    print("Fetching large sample of products to find all unique sets...")
    
    try:
        url = f"{collector.base_url}/products"
        params = {"per_page": 200}  # Get more products
        
        response = requests.get(url, headers=collector.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        products = data.get('data', [])
        
        print(f"Got {len(products)} products, extracting unique sets...")
        
        # Extract ALL unique sets
        unique_sets = {}
        for product in products:
            episode = product.get('episode', {})
            if episode:
                slug = episode.get('slug')
                name = episode.get('name')
                release_date = episode.get('released_at', '')
                
                if slug and name:
                    unique_sets[slug] = {
                        'name': name,
                        'slug': slug,
                        'released_at': release_date,
                        'product_count': unique_sets.get(slug, {}).get('product_count', 0) + 1
                    }
                else:
                    unique_sets[slug]['product_count'] += 1
        
        print(f"\n✅ Found {len(unique_sets)} unique Pokemon sets:")
        print("=" * 80)
        
        # Sort by release date (newest first)
        sorted_sets = sorted(unique_sets.items(), 
                           key=lambda x: x[1]['released_at'] or '0000', 
                           reverse=True)
        
        print(f"{'SET NAME':<40} {'SLUG':<25} {'RELEASED':<12} {'PRODUCTS'}")
        print("-" * 80)
        
        for slug, info in sorted_sets:
            name = info['name'][:38] + '..' if len(info['name']) > 40 else info['name']
            release = info['released_at'][:10] if info['released_at'] else 'Unknown'
            count = info['product_count']
            
            print(f"{name:<40} {slug:<25} {release:<12} {count}")
        
        # Show popular sets for investment analysis
        print(f"\n🎯 BEST SETS FOR INVESTMENT ANALYSIS:")
        print("=" * 50)
        
        # Filter for sets with many products (usually means they're popular/current)
        popular_sets = [(slug, info) for slug, info in sorted_sets 
                       if info['product_count'] >= 3 and info['released_at'] and info['released_at'] >= '2020-01-01']
        
        for i, (slug, info) in enumerate(popular_sets[:10], 1):
            print(f"{i:2d}. '{slug}' - {info['name']} ({info['released_at'][:10]})")
        
        # Generate updated code
        print(f"\n📝 COPY THIS INTO YOUR main.py:")
        print("=" * 50)
        
        recommended_slugs = [slug for slug, info in popular_sets[:8]]
        
        print("# Updated sets_to_analyze with CORRECT slugs:")
        print("sets_to_analyze = [")
        for slug in recommended_slugs:
            print(f'    "{slug}",')
        print("]")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import requests  # Add this import
    main()
from data_collector import PokemonDataCollector

def main():
    print("🔍 Pokemon TCG Set Discovery Tool")
    print("=" * 50)
    
    collector = PokemonDataCollector()
    
    # Test API connection
    if not collector.test_api_connection():
        print("❌ Cannot connect to API. Check your .env file.")
        return
    
    # Discover all available sets
    sets = collector.discover_available_sets(limit=200)
    
    if not sets:
        print("❌ No sets discovered.")
        return
    
    print("\n" + "=" * 70)
    print("📋 COMPLETE LIST OF AVAILABLE SETS")
    print("=" * 70)
    
    # Group by year
    sets_by_year = {}
    for set_info in sets:
        year = set_info['released_at'][:4] if set_info['released_at'] else 'Unknown'
        if year not in sets_by_year:
            sets_by_year[year] = []
        sets_by_year[year].append(set_info)
    
    # Display sets grouped by year
    for year in sorted(sets_by_year.keys(), reverse=True):
        print(f"\n📅 {year}:")
        for set_info in sorted(sets_by_year[year], key=lambda x: x['released_at'] or '0000', reverse=True):
            print(f"   • {set_info['name']}")
            print(f"     Slug: '{set_info['slug']}'")
            print(f"     Released: {set_info['released_at'] or 'Unknown'}")
    
    # Test some common set slugs
    print("\n" + "=" * 50)
    print("🧪 TESTING COMMON SET SLUGS")
    print("=" * 50)
    
    test_slugs = [
        "evolving-skies",
        "brilliant-stars", 
        "lost-origin",
        "silver-tempest",
        "paldea-evolved",
        "paldean-fates",
        "obsidian-flames",
        "paradox-rift",
        "151",
        "temporal-forces"
    ]
    
    for slug in test_slugs:
        print(f"\nTesting '{slug}':")
        is_valid, message = collector.validate_set_slug(slug)
        status = "✅" if is_valid else "❌"
        print(f"   {status} {message}")
    
    # Recommend best sets for analysis
    print("\n" + "=" * 50)
    print("💡 RECOMMENDED SETS FOR ANALYSIS")
    print("=" * 50)
    
    # Filter for recent, popular sets
    recent_sets = [s for s in sets if s['released_at'] and s['released_at'] >= '2021-01-01']
    recent_sets = sorted(recent_sets, key=lambda x: x['released_at'], reverse=True)
    
    print("Based on release date, here are good sets to analyze:")
    for i, set_info in enumerate(recent_sets[:10], 1):
        print(f"{i:2d}. {set_info['name']} ('{set_info['slug']}')")
        print(f"    Released: {set_info['released_at']}")

if __name__ == "__main__":
    main()
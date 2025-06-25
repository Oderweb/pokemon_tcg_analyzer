from data_collector import PokemonDataCollector
import requests

def test_episodes_correctly():
    print("🧪 Testing Episodes API - Correct Approach")
    print("=" * 60)
    
    collector = PokemonDataCollector()
    
    # Test API connection
    if not collector.test_api_connection():
        print("❌ Cannot connect to API. Check your .env file.")
        return
    
    print("\n1. Testing episodes pagination (pages 1-3)...")
    print("=" * 50)
    
    all_episodes = []
    
    # Test pages 1, 2, 3 to get all episodes/sets
    for page in [1, 2, 3]:
        print(f"\n--- PAGE {page} ---")
        
        try:
            url = f"{collector.base_url}/episodes"
            params = {"page": page, "per_page": 20}
            
            response = requests.get(url, headers=collector.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            episodes = data.get('data', [])
            
            print(f"Found {len(episodes)} episodes on page {page}")
            
            for episode in episodes:
                episode_id = episode.get('id')
                name = episode.get('name', 'Unknown')
                slug = episode.get('slug', 'unknown')
                release_date = episode.get('released_at', 'Unknown')
                cards_total = episode.get('cards_total', 0)
                
                print(f"  ID {episode_id:3d}: {name} ({slug}) - {cards_total} cards - {release_date}")
                all_episodes.append(episode)
                
        except Exception as e:
            print(f"Error getting page {page}: {e}")
    
    print(f"\n📊 TOTAL EPISODES FOUND: {len(all_episodes)}")
    
    # Test getting cards for a few specific episodes
    print(f"\n2. Testing card retrieval for specific episodes...")
    print("=" * 50)
    
    # Test first 3 episodes from our list
    test_episodes = all_episodes[:3] if all_episodes else []
    
    for episode in test_episodes:
        episode_id = episode.get('id')
        episode_name = episode.get('name')
        cards_total = episode.get('cards_total', 0)
        
        print(f"\n--- EPISODE {episode_id}: {episode_name} ---")
        print(f"Expected cards: {cards_total}")
        
        try:
            # Test getting cards for this episode
            url = f"{collector.base_url}/cards"
            params = {
                "episode": episode_id,
                "per_page": 10,
                "sort": "price_desc"  # Get highest value cards
            }
            
            response = requests.get(url, headers=collector.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            cards = data.get('data', [])
            
            print(f"✅ Successfully got {len(cards)} cards")
            
            if cards:
                # Check first few cards
                cards_with_prices = 0
                total_value = 0
                
                for i, card in enumerate(cards[:5]):
                    card_name = card.get('name', 'Unknown')
                    price = card.get('prices', {}).get('cardmarket', {}).get('lowest')
                    
                    if price and price > 0:
                        cards_with_prices += 1
                        total_value += price
                        print(f"  {i+1}. {card_name} - €{price}")
                    else:
                        print(f"  {i+1}. {card_name} - No price")
                
                if cards_with_prices > 0:
                    avg_price = total_value / cards_with_prices
                    print(f"  💰 Cards with prices: {cards_with_prices}/5, Avg: €{avg_price:.2f}")
                else:
                    print(f"  ⚠️ No cards have valid prices!")
            
        except Exception as e:
            print(f"❌ Error getting cards for episode {episode_id}: {e}")
    
    # Test finding specific sets we want to analyze
    print(f"\n3. Finding episodes for our target sets...")
    print("=" * 50)
    
    target_sets = [
        "evolving skies", "brilliant stars", "lost origin", 
        "destined rivals", "silver tempest", "paldea evolved"
    ]
    
    found_sets = {}
    
    for target in target_sets:
        print(f"\nSearching for: '{target}'")
        found = False
        
        for episode in all_episodes:
            episode_name = episode.get('name', '').lower()
            episode_slug = episode.get('slug', '').lower()
            
            # Check if target matches episode name or slug
            if (target.lower() in episode_name or 
                episode_name in target.lower() or
                target.lower().replace(' ', '-') in episode_slug):
                
                episode_id = episode.get('id')
                print(f"  ✅ Found: {episode.get('name')} (ID: {episode_id})")
                found_sets[target] = episode
                found = True
                break
        
        if not found:
            print(f"  ❌ Not found")
    
    print(f"\n📋 SUMMARY FOR ANALYSIS:")
    print("=" * 40)
    
    if found_sets:
        print("Sets we can analyze:")
        for target, episode in found_sets.items():
            episode_id = episode.get('id')
            episode_name = episode.get('name')
            cards_total = episode.get('cards_total', 0)
            print(f"  • {episode_name} (ID: {episode_id}) - {cards_total} cards")
        
        print(f"\n💡 Update your main.py to use these episode IDs for better results!")
    else:
        print("❌ No matching sets found. Check episode names.")

if __name__ == "__main__":
    test_episodes_correctly()
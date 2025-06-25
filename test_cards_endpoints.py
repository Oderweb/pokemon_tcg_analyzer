import requests
from config import Config

def test_cards_endpoints():
    print("🧪 Testing Cards API Endpoints")
    print("=" * 50)
    
    config = Config()
    base_url = config.POKEMON_API_BASE_URL
    headers = config.RAPIDAPI_HEADERS
    
    # First, get a product to find episode ID
    print("1. Getting episode ID from a product...")
    try:
        response = requests.get(f"{base_url}/products", headers=headers, params={"search": "evolving skies", "per_page": 1})
        if response.status_code == 200:
            data = response.json()
            products = data.get('data', [])
            if products:
                episode = products[0].get('episode', {})
                episode_id = episode.get('id')
                episode_name = episode.get('name')
                print(f"   Found episode: {episode_name} (ID: {episode_id})")
                
                # Now test different ways to get cards for this episode
                print(f"\n2. Testing different cards endpoints for episode {episode_id}...")
                
                test_endpoints = [
                    # Direct search
                    ("Search method", f"/cards", {"search": "evolving skies", "per_page": 5}),
                    
                    # Episode-based methods
                    ("Episode param", f"/cards", {"episode": episode_id, "per_page": 5}),
                    ("Episode_id param", f"/cards", {"episode_id": episode_id, "per_page": 5}),
                    
                    # Path-based methods
                    ("Episode in path 1", f"/cards/episode/{episode_id}", {"per_page": 5}),
                    ("Episode in path 2", f"/episodes/{episode_id}/cards", {"per_page": 5}),
                    
                    # Try the RapidAPI documented endpoints
                    ("List All Cards", f"/cards", {"per_page": 5}),
                ]
                
                for method_name, endpoint, params in test_endpoints:
                    try:
                        url = f"{base_url}{endpoint}"
                        print(f"\n   Testing {method_name}:")
                        print(f"   URL: {url}")
                        print(f"   Params: {params}")
                        
                        response = requests.get(url, headers=headers, params=params)
                        print(f"   Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            cards = data.get('data', [])
                            print(f"   Cards found: {len(cards)}")
                            
                            if cards:
                                # Check first card
                                first_card = cards[0]
                                card_name = first_card.get('name', 'Unknown')
                                card_episode = first_card.get('episode', {}).get('name', 'Unknown')
                                price = first_card.get('prices', {}).get('cardmarket', {}).get('lowest', 'No price')
                                
                                print(f"   Sample card: {card_name}")
                                print(f"   From episode: {card_episode}")
                                print(f"   Price: €{price}")
                                
                                # Check if it's from the right episode
                                if card_episode == episode_name:
                                    print(f"   ✅ CORRECT EPISODE MATCH!")
                                else:
                                    print(f"   ❌ Wrong episode (expected {episode_name})")
                        else:
                            print(f"   Error: {response.text[:100]}...")
                            
                    except Exception as e:
                        print(f"   Exception: {e}")
                
            else:
                print("   No products found")
        else:
            print(f"   Failed to get products: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cards_endpoints()
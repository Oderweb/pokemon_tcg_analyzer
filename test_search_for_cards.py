import requests
import json
from config import Config

def test_search_cards_endpoint():
    """
    Test the 'Search for Cards' endpoint to see if it has pricing data
    """
    print("🧪 Testing 'Search for Cards' Endpoint")
    print("=" * 50)
    
    config = Config()
    base_url = config.POKEMON_API_BASE_URL
    headers = config.RAPIDAPI_HEADERS
    
    # Test different search approaches
    test_searches = [
        "charizard",
        "pikachu", 
        "destined rivals",
        "evolving skies",
        "brilliant stars"
    ]
    
    for search_term in test_searches:
        print(f"\n--- SEARCHING FOR: '{search_term}' ---")
        
        try:
            # Use Search for Cards endpoint
            url = f"{base_url}/cards"
            params = {
                "search": search_term,
                "per_page": 10,
                "page": 0  # Start from page 0 as shown in API
            }
            
            print(f"Request: {url}")
            print(f"Params: {params}")
            
            response = requests.get(url, headers=headers, params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                cards = data.get('data', [])
                
                print(f"Found {len(cards)} cards")
                
                if cards:
                    print(f"\nFirst 5 cards:")
                    
                    cards_with_prices = 0
                    
                    for i, card in enumerate(cards[:5]):
                        card_name = card.get('name', 'Unknown')
                        prices = card.get('prices', {})
                        episode_info = card.get('episode', {})
                        episode_name = episode_info.get('name', 'Unknown Set')
                        
                        print(f"\n  {i+1}. {card_name} (from {episode_name})")
                        
                        if prices:
                            print(f"     Prices structure: {prices}")
                            
                            # Check for different price sources
                            cardmarket = prices.get('cardmarket', {})
                            tcgplayer = prices.get('tcgplayer', {})
                            
                            if cardmarket and cardmarket.get('lowest'):
                                price = cardmarket.get('lowest')
                                print(f"     💰 Cardmarket: €{price}")
                                cards_with_prices += 1
                            elif tcgplayer and tcgplayer.get('lowest'):
                                price = tcgplayer.get('lowest')
                                print(f"     💰 TCGPlayer: ${price}")
                                cards_with_prices += 1
                            else:
                                print(f"     ❌ No valid prices in structure")
                        else:
                            print(f"     ❌ No prices object")
                    
                    print(f"\n  📊 Cards with valid prices: {cards_with_prices}/5")
                    
                    if cards_with_prices > 0:
                        print(f"  ✅ This search method works for pricing!")
                    else:
                        print(f"  ❌ No pricing data available")
                else:
                    print("No cards found")
            else:
                print(f"Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"Error: {e}")

def test_list_cards_by_episode_corrected():
    """
    Test the List Cards by Episode with correct parameter name
    """
    print(f"\n🧪 Testing 'List Cards by Episode' with episode_id parameter")
    print("=" * 60)
    
    config = Config()
    base_url = config.POKEMON_API_BASE_URL
    headers = config.RAPIDAPI_HEADERS
    
    # Test with episode IDs 221, 220 (recent sets)
    test_episode_ids = [221, 220, 219]
    
    for episode_id in test_episode_ids:
        print(f"\n--- EPISODE ID: {episode_id} ---")
        
        try:
            url = f"{base_url}/cards"
            params = {
                "episode_id": episode_id,  # Use episode_id instead of episode
                "per_page": 10,
                "page": 0
            }
            
            print(f"Request: {url}")
            print(f"Params: {params}")
            
            response = requests.get(url, headers=headers, params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                cards = data.get('data', [])
                
                print(f"Found {len(cards)} cards for episode {episode_id}")
                
                if cards:
                    # Check first card for episode verification and pricing
                    first_card = cards[0]
                    card_name = first_card.get('name', 'Unknown')
                    episode_info = first_card.get('episode', {})
                    episode_name = episode_info.get('name', 'Unknown')
                    returned_episode_id = episode_info.get('id', 'Unknown')
                    
                    print(f"  First card: {card_name}")
                    print(f"  From episode: {episode_name} (ID: {returned_episode_id})")
                    
                    # Check if we got the right episode
                    if returned_episode_id == episode_id:
                        print(f"  ✅ Correct episode match!")
                    else:
                        print(f"  ❌ Episode mismatch (wanted {episode_id}, got {returned_episode_id})")
                    
                    # Check pricing
                    prices = first_card.get('prices', {})
                    if prices:
                        print(f"  Prices: {prices}")
                    else:
                        print(f"  ❌ No pricing data")
                else:
                    print(f"No cards returned")
            else:
                print(f"Error: {response.text[:200]}...")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Test both approaches
    test_search_cards_endpoint()
    test_list_cards_by_episode_corrected()
import requests
import json
from config import Config

def get_top_expensive_cards_by_episode(episode_id, episode_name, limit=50):
    """
    Get TOP 50 most expensive cards from a specific Episode ID
    """
    print(f"\n🎯 Getting TOP {limit} most expensive cards from Episode {episode_id}: {episode_name}")
    print("-" * 80)
    
    config = Config()
    base_url = config.POKEMON_API_BASE_URL
    headers = config.RAPIDAPI_HEADERS
    
    try:
        # Get ALL cards from this episode first (not just 10)
        url = f"{base_url}/cards"
        params = {
            "episode": episode_id,
            "per_page": 200  # Get many cards at once
        }
        
        print(f"Fetching cards from episode {episode_id}...")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        all_cards = data.get('data', [])
        
        print(f"Got {len(all_cards)} cards from the API")
        
        if not all_cards:
            print("❌ No cards found")
            return []
        
        # Extract cards with valid prices and sort manually
        cards_with_prices = []
        
        for card in all_cards:
            card_name = card.get('name', 'Unknown')
            prices = card.get('prices', {})
            
            # Try to get price from different sources
            price = None
            currency = "EUR"
            
            # Try Cardmarket first (EUR)
            if prices and 'cardmarket' in prices:
                cardmarket_price = prices['cardmarket'].get('lowest')
                if cardmarket_price and cardmarket_price > 0:
                    price = cardmarket_price
                    currency = "EUR"
            
            # Fallback to TCGPlayer (USD)
            if not price and prices and 'tcgplayer' in prices:
                tcg_price = prices['tcgplayer'].get('lowest')
                if tcg_price and tcg_price > 0:
                    price = tcg_price
                    currency = "USD"
            
            if price and price > 0:
                cards_with_prices.append({
                    'name': card_name,
                    'price': price,
                    'currency': currency,
                    'full_card_data': card
                })
        
        print(f"Found {len(cards_with_prices)} cards with valid prices")
        
        if not cards_with_prices:
            print("❌ No cards have valid prices!")
            return []
        
        # Sort by price (highest first)
        cards_with_prices.sort(key=lambda x: x['price'], reverse=True)
        
        # Get top N cards
        top_cards = cards_with_prices[:limit]
        
        print(f"\n💰 TOP {len(top_cards)} MOST EXPENSIVE CARDS:")
        print("-" * 60)
        print(f"{'RANK':<4} {'CARD NAME':<35} {'PRICE':<10} {'CURRENCY'}")
        print("-" * 60)
        
        for i, card in enumerate(top_cards[:20], 1):  # Show top 20 in console
            name = card['name'][:33]
            price = card['price']
            currency = card['currency']
            print(f"{i:<4} {name:<35} {price:<10.2f} {currency}")
        
        if len(top_cards) > 20:
            print(f"... and {len(top_cards) - 20} more expensive cards")
        
        # Calculate some stats
        total_value = sum(card['price'] for card in top_cards)
        avg_value = total_value / len(top_cards)
        
        print(f"\n📊 STATISTICS FOR TOP {len(top_cards)} CARDS:")
        print(f"Total value: {total_value:.2f}")
        print(f"Average value: {avg_value:.2f}")
        print(f"Most expensive: {top_cards[0]['name']} - {top_cards[0]['price']:.2f} {top_cards[0]['currency']}")
        print(f"Least expensive in top {limit}: {top_cards[-1]['name']} - {top_cards[-1]['price']:.2f} {top_cards[-1]['currency']}")
        
        return [card['full_card_data'] for card in top_cards]
        
    except Exception as e:
        print(f"❌ Error getting cards for episode {episode_id}: {e}")
        return []

def test_top_cards_for_episodes():
    """
    Test getting top expensive cards for multiple episodes
    """
    print("🎯 Testing TOP EXPENSIVE CARDS by Episode ID")
    print("=" * 60)
    
    # Load episode IDs
    try:
        with open("pokemon_episode_ids.json", 'r') as f:
            episodes = json.load(f)
        print(f"✅ Loaded {len(episodes)} episodes from file")
    except FileNotFoundError:
        print("❌ Run get_episode_ids.py first to get episode data")
        return
    
    # Test with first 3 episodes
    test_episodes = episodes[:3]
    
    all_results = {}
    
    for episode in test_episodes:
        episode_id = episode['id']
        episode_name = episode['name']
        
        print(f"\n{'='*80}")
        print(f"EPISODE {episode_id}: {episode_name}")
        print(f"{'='*80}")
        
        # Get top 50 most expensive cards
        top_cards = get_top_expensive_cards_by_episode(episode_id, episode_name, limit=50)
        
        if top_cards:
            all_results[episode_name] = {
                'episode_id': episode_id,
                'episode_name': episode_name,
                'top_cards': top_cards
            }
        
        print(f"\n" + "="*80)
    
    # Save results
    if all_results:
        with open("top_expensive_cards_by_episode.json", 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved top expensive cards data to: top_expensive_cards_by_episode.json")
        
        print(f"\n🎯 SUMMARY:")
        for episode_name, data in all_results.items():
            print(f"  {episode_name}: {len(data['top_cards'])} expensive cards found")

if __name__ == "__main__":
    test_top_cards_for_episodes()
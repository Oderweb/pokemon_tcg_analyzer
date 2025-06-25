import requests
import json
from config import Config

def get_all_cards_from_episode(episode_id):
    """
    Get ALL cards from an episode (not just first page)
    """
    config = Config()
    base_url = config.POKEMON_API_BASE_URL
    headers = config.RAPIDAPI_HEADERS
    
    all_cards = []
    page = 0
    max_pages = 50  # Safety limit
    
    print(f"Getting ALL cards from episode {episode_id}...")
    
    while page < max_pages:
        try:
            url = f"{base_url}/cards"
            params = {
                "episode_id": episode_id,
                "per_page": 20,  # Get 20 cards per page
                "page": page
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            cards = data.get('data', [])
            
            if not cards:
                print(f"No more cards found at page {page}")
                break
            
            print(f"  Page {page}: Got {len(cards)} cards")
            all_cards.extend(cards)
            
            # Check if we've reached the end
            paging = data.get('paging', {})
            current_page = paging.get('current', page)
            total_pages = paging.get('total', 1)
            
            if current_page >= total_pages:
                print(f"Reached last page ({total_pages})")
                break
            
            page += 1
            
        except Exception as e:
            print(f"Error getting page {page}: {e}")
            break
    
    print(f"Total cards retrieved: {len(all_cards)}")
    return all_cards

def extract_card_price(card):
    """
    Extract the best available price from a card
    """
    prices = card.get('prices', {})
    
    if not prices:
        return 0
    
    # Try Cardmarket first (EUR)
    cardmarket = prices.get('cardmarket', {})
    if cardmarket:
        # Use lowest_near_mint as the primary price
        price = cardmarket.get('lowest_near_mint')
        if price and price > 0:
            return price
    
    # Fallback to TCGPlayer
    tcgplayer = prices.get('tcg_player', {})
    if tcgplayer:
        price = tcgplayer.get('market_price')
        if price and price > 0:
            return price
    
    return 0

def get_top_expensive_cards_from_episode(episode_id, episode_name, top_count=50):
    """
    Get the TOP most expensive cards from a specific episode
    """
    print(f"\n🎯 Getting TOP {top_count} cards from Episode {episode_id}: {episode_name}")
    print("=" * 80)
    
    # Get all cards from this episode
    all_cards = get_all_cards_from_episode(episode_id)
    
    if not all_cards:
        print("❌ No cards found")
        return []
    
    # Extract prices and create sortable list
    cards_with_prices = []
    
    for card in all_cards:
        card_name = card.get('name', 'Unknown')
        price = extract_card_price(card)
        
        if price > 0:
            cards_with_prices.append({
                'name': card_name,
                'price': price,
                'card_data': card
            })
    
    print(f"Cards with valid prices: {len(cards_with_prices)}/{len(all_cards)}")
    
    if not cards_with_prices:
        print("❌ No cards have valid prices!")
        return []
    
    # Sort by price (highest first)
    cards_with_prices.sort(key=lambda x: x['price'], reverse=True)
    
    # Get top N cards
    top_cards = cards_with_prices[:top_count]
    
    print(f"\n💰 TOP {len(top_cards)} MOST EXPENSIVE CARDS:")
    print("-" * 70)
    print(f"{'RANK':<4} {'CARD NAME':<40} {'PRICE (EUR)':<12}")
    print("-" * 70)
    
    for i, card in enumerate(top_cards[:20], 1):  # Show top 20
        name = card['name'][:38]
        price = card['price']
        print(f"{i:<4} {name:<40} €{price:<11.2f}")
    
    if len(top_cards) > 20:
        print(f"... and {len(top_cards) - 20} more expensive cards")
    
    # Show statistics
    total_value = sum(card['price'] for card in top_cards)
    avg_value = total_value / len(top_cards)
    
    print(f"\n📊 STATISTICS:")
    print(f"Total value of top {len(top_cards)}: €{total_value:.2f}")
    print(f"Average value: €{avg_value:.2f}")
    print(f"Most expensive: {top_cards[0]['name']} - €{top_cards[0]['price']:.2f}")
    print(f"Least expensive in top {top_count}: {top_cards[-1]['name']} - €{top_cards[-1]['price']:.2f}")
    
    return [card['card_data'] for card in top_cards]

def test_multiple_episodes():
    """
    Test getting top cards for multiple episodes
    """
    print("🎯 TESTING TOP EXPENSIVE CARDS FROM MULTIPLE EPISODES")
    print("=" * 80)
    
    # Load episodes if available
    try:
        with open("pokemon_episode_ids.json", 'r') as f:
            episodes = json.load(f)
        print(f"✅ Loaded {len(episodes)} episodes")
    except FileNotFoundError:
        print("❌ Run get_episode_ids.py first")
        return
    
    # Test with first few episodes that have cards
    test_episodes = [
        {"id": 221, "name": "Destined Rivals"},
        {"id": 220, "name": "Journey Together"},
        {"id": episodes[2]["id"], "name": episodes[2]["name"]} if len(episodes) > 2 else None
    ]
    
    # Remove None entries
    test_episodes = [ep for ep in test_episodes if ep]
    
    results = {}
    
    for episode in test_episodes:
        episode_id = episode["id"]
        episode_name = episode["name"]
        
        top_cards = get_top_expensive_cards_from_episode(episode_id, episode_name, top_count=50)
        
        if top_cards:
            results[episode_name] = {
                'episode_id': episode_id,
                'top_cards_count': len(top_cards),
                'top_cards': top_cards
            }
            
            print(f"\n✅ {episode_name}: Found {len(top_cards)} expensive cards")
        else:
            print(f"\n❌ {episode_name}: No expensive cards found")
    
    # Save results
    if results:
        with open("top_expensive_cards_fixed.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Saved results to: top_expensive_cards_fixed.json")
        
        print(f"\n🎯 SUMMARY FOR ROI CALCULATIONS:")
        for episode_name, data in results.items():
            print(f"  {episode_name}: {data['top_cards_count']} cards available for ROI calculation")

if __name__ == "__main__":
    test_multiple_episodes()
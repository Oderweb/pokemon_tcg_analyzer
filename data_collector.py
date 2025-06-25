import requests
import json
import time
from datetime import datetime
from config import Config

class PokemonDataCollector:
    def __init__(self):
        self.config = Config()
        self.base_url = self.config.POKEMON_API_BASE_URL
        self.headers = self.config.RAPIDAPI_HEADERS
    
    def get_products_by_set_name(self, set_name):
        """
        Get all products for a Pokemon set using search parameter
        Example: set_name = "evolving skies" or "destined rivals"
        """
        try:
            url = f"{self.base_url}/products"
            params = {
                "search": set_name,
                "per_page": 50
            }
            
            print(f"Searching for products: '{set_name}'")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            products = data.get('data', [])
            
            print(f"Found {len(products)} products for '{set_name}'")
            
            # Debug: Show what we found
            if products:
                product_types = {}
                for product in products:
                    name = product.get('name', '').lower()
                    if 'elite trainer box' in name or 'etb' in name:
                        product_types['ETB'] = product_types.get('ETB', 0) + 1
                    elif 'booster box' in name:
                        product_types['Booster Box'] = product_types.get('Booster Box', 0) + 1
                    else:
                        product_types['Other'] = product_types.get('Other', 0) + 1
                
                print(f"   Product breakdown: {dict(product_types)}")
            
            return products
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching products for '{set_name}': {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def get_all_episodes(self):
        """
        Get all available episodes/sets by going through all pages
        """
        try:
            all_episodes = []
            page = 1
            max_pages = 10  # Safety limit
            
            print("Fetching all episodes from all pages...")
            
            while page <= max_pages:
                url = f"{self.base_url}/episodes"
                params = {"page": page, "per_page": 20}
                
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                episodes = data.get('data', [])
                
                if not episodes:
                    print(f"No more episodes found at page {page}")
                    break
                
                print(f"Page {page}: Found {len(episodes)} episodes")
                all_episodes.extend(episodes)
                
                # Check if there are more pages
                paging = data.get('paging', {})
                current_page = paging.get('current', page)
                total_pages = paging.get('total', 1)
                
                if current_page >= total_pages:
                    print(f"Reached last page ({total_pages})")
                    break
                
                page += 1
            
            print(f"Total episodes found: {len(all_episodes)}")
            
            # Show first few episodes
            for episode in all_episodes[:5]:
                episode_id = episode.get('id')
                name = episode.get('name', 'Unknown')
                slug = episode.get('slug', 'unknown')
                release_date = episode.get('released_at', 'Unknown')
                print(f"   Episode {episode_id}: {name} ({slug}) - {release_date}")
            
            return all_episodes
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching episodes: {e}")
            return []
    
    def find_episode_by_name(self, set_name):
        """
        Find episode ID by searching for set name
        """
        episodes = self.get_all_episodes()
        
        # Search for matching episode
        for episode in episodes:
            episode_name = episode.get('name', '').lower()
            episode_slug = episode.get('slug', '').lower()
            
            # Check if set_name matches episode name or slug
            if (set_name.lower() in episode_name or 
                episode_name in set_name.lower() or
                set_name.lower().replace(' ', '-') in episode_slug):
                
                print(f"Found matching episode: {episode.get('name')} (ID: {episode.get('id')})")
                return episode
        
        print(f"No matching episode found for '{set_name}'")
        return None
    
    def get_cards_by_episode_id(self, episode_id, limit=50):
        """
        Get cards by episode ID using the correct endpoint
        """
        try:
            url = f"{self.base_url}/cards"
            params = {
                "episode": episode_id,
                "per_page": limit,
                "sort": "price_desc"  # Get highest value cards first
            }
            
            print(f"Getting cards for episode ID {episode_id}...")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            cards = data.get('data', [])
            
            print(f"Found {len(cards)} cards for episode {episode_id}")
            
            return cards
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching cards for episode {episode_id}: {e}")
            return []
    
    def get_cards_by_set_name(self, set_name, limit=50):
        """
        Get top expensive cards from a set using episode ID method
        """
        try:
            # Step 1: Find the episode ID for this set name
            episode = self.find_episode_by_name(set_name)
            
            if not episode:
                print(f"Could not find episode for '{set_name}'")
                return []
            
            episode_id = episode.get('id')
            episode_name = episode.get('name')
            
            # Step 2: Get ALL cards from this episode
            print(f"Getting cards for '{episode_name}' (Episode ID: {episode_id})")
            all_cards = self.get_all_cards_from_episode(episode_id)
            
            if not all_cards:
                return []
            
            # Step 3: Extract cards with prices and sort by price
            cards_with_prices = []
            for card in all_cards:
                price = self.extract_card_price(card)
                if price > 0:
                    cards_with_prices.append({
                        'price': price,
                        'card': card
                    })
            
            print(f"   Found {len(cards_with_prices)} cards with valid prices")
            
            if not cards_with_prices:
                print(f"   ⚠️ No cards have valid prices!")
                return []
            
            # Sort by price (highest first) and get top cards
            cards_with_prices.sort(key=lambda x: x['price'], reverse=True)
            top_cards = [item['card'] for item in cards_with_prices[:limit]]
            
            # Show sample of top cards
            print(f"   Top 3 most expensive cards:")
            for i, item in enumerate(cards_with_prices[:3], 1):
                card_name = item['card'].get('name', 'Unknown')
                price = item['price']
                print(f"     {i}. {card_name} - €{price:.2f}")
            
            return top_cards
            
        except Exception as e:
            print(f"Unexpected error getting cards for '{set_name}': {e}")
            return []
    
    def get_all_cards_from_episode(self, episode_id):
        """
        Get ALL cards from an episode (multiple pages)
        """
        all_cards = []
        page = 0
        max_pages = 50
        
        while page < max_pages:
            try:
                url = f"{self.base_url}/cards"
                params = {
                    "episode_id": episode_id,
                    "per_page": 20,
                    "page": page
                }
                
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                cards = data.get('data', [])
                
                if not cards:
                    break
                
                all_cards.extend(cards)
                
                # Check pagination
                paging = data.get('paging', {})
                if paging.get('current', page) >= paging.get('total', 1):
                    break
                
                page += 1
                
            except Exception as e:
                print(f"Error getting page {page}: {e}")
                break
        
        return all_cards
    
    def extract_card_price(self, card):
        """
        Extract price using correct API fields
        """
        prices = card.get('prices', {})
        
        if not prices:
            return 0
        
        # Try Cardmarket first (EUR)
        cardmarket = prices.get('cardmarket', {})
        if cardmarket:
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
    
    def get_specific_products(self, set_name):
        """
        Get specific ETB and Booster Box products for a set
        Returns: {'etb': [...], 'booster_boxes': [...]}
        """
        all_products = self.get_products_by_set_name(set_name)
        
        etbs = []
        booster_boxes = []
        
        for product in all_products:
            name = product.get('name', '').lower()
            slug = product.get('slug', '')
            
            # Check for Elite Trainer Box
            if 'elite trainer box' in name or 'etb' in name:
                etbs.append(product)
            
            # Check for Booster Box (but not Elite Trainer Box)
            elif 'booster box' in name and 'elite trainer' not in name:
                booster_boxes.append(product)
        
        print(f"   Found {len(etbs)} ETBs and {len(booster_boxes)} Booster Boxes")
        
        return {
            'etb': etbs,
            'booster_boxes': booster_boxes,
            'all_products': all_products
        }
    
    def discover_available_sets(self):
        """
        Discover available Pokemon sets by searching for common set names
        """
        # Common Pokemon set names to search for
        popular_sets = [
            "evolving skies",
            "brilliant stars", 
            "lost origin",
            "silver tempest",
            "paldea evolved",
            "obsidian flames",
            "paradox rift",
            "paldean fates",
            "temporal forces",
            "twilight masquerade",
            "shrouded fable",
            "stellar crown",
            "surging sparks",
            "destined rivals",
            "151",
            "crown zenith",
            "pokemon go",
            "astral radiance",
            "fusion strike",
            "chilling reign"
        ]
        
        found_sets = []
        
        print("🔍 Discovering available Pokemon sets...")
        print("=" * 50)
        
        for set_name in popular_sets:
            print(f"\nSearching for: {set_name}")
            products = self.get_products_by_set_name(set_name)
            
            if products:
                # Get unique episode info
                episodes = set()
                for product in products:
                    episode = product.get('episode', {})
                    if episode:
                        episodes.add((episode.get('name', ''), episode.get('slug', ''), episode.get('released_at', '')))
                
                for episode_name, episode_slug, release_date in episodes:
                    found_sets.append({
                        'search_term': set_name,
                        'name': episode_name,
                        'slug': episode_slug, 
                        'released_at': release_date,
                        'products_found': len(products)
                    })
                    print(f"   ✅ Found: {episode_name} ({episode_slug}) - {len(products)} products")
            else:
                print(f"   ❌ No products found for '{set_name}'")
            
            # Small delay to be nice to the API
            time.sleep(0.5)
        
        return found_sets
    
    def save_data_to_file(self, data, filename):
        """
        Save data to JSON file with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{timestamp}_{filename}.json"
        
        try:
            with open(full_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Data saved to {full_filename}")
            
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def test_api_connection(self):
        """
        Test if API connection is working
        """
        try:
            url = f"{self.base_url}/products"
            params = {"per_page": 1}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            print("✅ API connection successful!")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API connection failed: {e}")
            return False
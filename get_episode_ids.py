import requests
import json
from config import Config

def get_all_episode_ids():
    """
    Get all Pokemon set episode IDs and save them to a file
    """
    print("🔍 Getting All Pokemon Set Episode IDs")
    print("=" * 50)
    
    config = Config()
    base_url = config.POKEMON_API_BASE_URL
    headers = config.RAPIDAPI_HEADERS
    
    all_episodes = []
    page = 1
    max_pages = 10
    
    print("Fetching episodes from all pages...")
    
    while page <= max_pages:
        try:
            url = f"{base_url}/episodes"
            params = {"page": page, "per_page": 20}
            
            print(f"Getting page {page}...")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            episodes = data.get('data', [])
            
            if not episodes:
                print(f"No episodes found on page {page}")
                break
            
            print(f"  Found {len(episodes)} episodes on page {page}")
            
            for episode in episodes:
                episode_info = {
                    'id': episode.get('id'),
                    'name': episode.get('name'),
                    'slug': episode.get('slug'),
                    'released_at': episode.get('released_at'),
                    'cards_total': episode.get('cards_total', 0),
                    'cards_printed_total': episode.get('cards_printed_total', 0)
                }
                all_episodes.append(episode_info)
                
                print(f"    ID {episode_info['id']:3d}: {episode_info['name']} ({episode_info['cards_total']} cards)")
            
            # Check pagination
            paging = data.get('paging', {})
            if paging.get('current', page) >= paging.get('total', 1):
                print(f"Reached last page")
                break
            
            page += 1
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
    
    print(f"\n📊 TOTAL EPISODES FOUND: {len(all_episodes)}")
    
    # Save to JSON file
    filename = "pokemon_episode_ids.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_episodes, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved all episode data to: {filename}")
    
    # Show summary of what we found
    print(f"\n📋 EPISODE SUMMARY:")
    print("-" * 60)
    print(f"{'ID':<4} {'NAME':<30} {'SLUG':<25} {'CARDS'}")
    print("-" * 60)
    
    for episode in all_episodes[:15]:  # Show first 15
        print(f"{episode['id']:<4} {episode['name'][:28]:<30} {episode['slug'][:23]:<25} {episode['cards_total']}")
    
    if len(all_episodes) > 15:
        print(f"... and {len(all_episodes) - 15} more episodes")
    
    # Find episodes for common sets
    print(f"\n🎯 EPISODES FOR POPULAR SETS:")
    print("-" * 40)
    
    target_sets = [
        "evolving skies", "brilliant stars", "lost origin", 
        "destined rivals", "silver tempest", "paldea evolved",
        "obsidian flames", "paradox rift", "151"
    ]
    
    found_episodes = {}
    
    for target in target_sets:
        for episode in all_episodes:
            episode_name = episode['name'].lower()
            episode_slug = episode['slug'].lower()
            
            if (target.lower() in episode_name or 
                episode_name in target.lower() or
                target.lower().replace(' ', '-') in episode_slug):
                
                found_episodes[target] = episode
                print(f"  {target:<20} -> ID {episode['id']:3d}: {episode['name']}")
                break
    
    # Save just the IDs for easy use
    episode_ids_only = {episode['name']: episode['id'] for episode in all_episodes}
    
    with open("episode_ids_simple.json", 'w') as f:
        json.dump(episode_ids_only, f, indent=2)
    
    print(f"\n💡 NEXT STEP:")
    print("Use these Episode IDs in the 'List Cards by Episode' endpoint")
    print("Example: GET /cards with parameter 'episode=221' for Destined Rivals")
    
    return all_episodes

if __name__ == "__main__":
    episodes = get_all_episode_ids()
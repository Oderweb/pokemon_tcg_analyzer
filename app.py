from flask import Flask, render_template, jsonify, request, redirect, url_for
from data_collector import PokemonDataCollector
from roi_calculator import ROICalculator
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Global variables to store our components
collector = PokemonDataCollector()
calculator = ROICalculator()

def load_available_episodes():
    """
    Load all available Pokemon episodes/sets from our saved data
    """
    try:
        with open("pokemon_episode_ids.json", 'r', encoding='utf-8') as f:
            episodes = json.load(f)
        
        # Convert to the format we need and filter for sets with cards
        available_sets = []
        for episode in episodes:
            if episode.get('cards_total', 0) > 0:  # Only include sets with cards
                available_sets.append({
                    "name": episode.get('name', 'Unknown'),
                    "search_term": episode.get('name', '').lower(),
                    "slug": episode.get('slug', ''),
                    "episode_id": episode.get('id'),
                    "cards_total": episode.get('cards_total', 0),
                    "released_at": episode.get('released_at', '')
                })
        
        # Sort by release date (newest first)
        available_sets.sort(key=lambda x: x['released_at'] or '0000', reverse=True)
        
        print(f"✅ Loaded {len(available_sets)} available Pokemon sets")
        return available_sets
        
    except FileNotFoundError:
        print("⚠️ pokemon_episode_ids.json not found, using fallback sets")
        # Fallback to manual list
        return [
            {"name": "Destined Rivals", "search_term": "destined rivals", "episode_id": 221},
            {"name": "Journey Together", "search_term": "journey together", "episode_id": 220},
            {"name": "Prismatic Evolutions", "search_term": "prismatic evolutions", "episode_id": 212}
        ]

def analyze_sets(sets_list):
    """
    Analyze multiple Pokemon sets and return results
    """
    all_results = []
    
    for set_info in sets_list:
        # Handle both old format (strings) and new format (objects)
        if isinstance(set_info, str):
            set_name = set_info
            print(f"Analyzing '{set_name}' for web interface...")
        else:
            set_name = set_info.get('search_term') or set_info.get('name', '').lower()
            print(f"Analyzing '{set_info.get('name')}' (ID: {set_info.get('episode_id')}) for web interface...")
        
        # Get specific products using search
        products_data = collector.get_specific_products(set_name)
        etbs = products_data['etb']
        booster_boxes = products_data['booster_boxes']
        
        # Get top cards
        top_cards = collector.get_cards_by_set_name(set_name, limit=50)
        
        # Analyze ETBs
        for etb in etbs:
            analysis = calculator.analyze_product(etb, top_cards)
            if analysis:
                analysis['category'] = 'Elite Trainer Box'
                all_results.append(analysis)
        
        # Analyze Booster Boxes
        for box in booster_boxes:
            analysis = calculator.analyze_product(box, top_cards)
            if analysis:
                analysis['category'] = 'Booster Box'
                all_results.append(analysis)
    
    # Sort by ROI descending
    all_results.sort(key=lambda x: x['roi_percentage'], reverse=True)
    return all_results

@app.route('/')
def home():
    """
    Main homepage showing the analysis table
    """
    return render_template('index.html')

@app.route('/api/analyze')
def api_analyze():
    """
    API endpoint that returns JSON data for the frontend
    """
    try:
        # Test API connection first
        if not collector.test_api_connection():
            return jsonify({
                'error': 'Cannot connect to Pokemon TCG API. Please check your API key.'
            }), 500
        
        # Load available sets dynamically
        available_sets = load_available_episodes()
        
        # Get custom sets from query parameter if provided
        custom_sets_param = request.args.get('sets')
        limit = int(request.args.get('limit', 15))  # Allow limiting number of sets
        
        if custom_sets_param:
            # Parse custom sets (comma-separated names)
            custom_set_names = [name.strip().lower() for name in custom_sets_param.split(',')]
            sets_to_analyze = []
            
            for name in custom_set_names:
                # Find matching episode
                for episode in available_sets:
                    if name in episode['name'].lower() or name in episode.get('search_term', ''):
                        sets_to_analyze.append(episode)
                        break
        else:
            # Use top N most recent sets
            sets_to_analyze = available_sets[:limit]
        
        print(f"Analyzing {len(sets_to_analyze)} sets: {[s.get('name') for s in sets_to_analyze]}")
        
        # Analyze the sets
        results = analyze_sets(sets_to_analyze)
        
        # Calculate summary stats
        summary = {
            'total_products': len(results),
            'positive_roi_count': len([r for r in results if r['roi_percentage'] > 0]),
            'average_roi': round(sum(r['roi_percentage'] for r in results) / len(results), 1) if results else 0,
            'average_risk': round(sum(r['risk_score'] for r in results) / len(results), 1) if results else 0,
            'best_opportunity': results[0] if results else None,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sets_analyzed': len(sets_to_analyze),
            'available_sets_total': len(available_sets)
        }
        
        return jsonify({
            'success': True,
            'data': results,
            'summary': summary
        })
        
    except Exception as e:
        print(f"Error in API analysis: {e}")
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/sets')
def api_sets():
    """
    Return list of all available Pokemon sets dynamically
    """
    try:
        available_sets = load_available_episodes()
        
        # Format for frontend
        formatted_sets = []
        for episode in available_sets:
            formatted_sets.append({
                "name": episode['name'],
                "search_term": episode.get('search_term', episode['name'].lower()),
                "episode_id": episode.get('episode_id'),
                "cards_total": episode.get('cards_total', 0),
                "released_at": episode.get('released_at', ''),
                "slug": episode.get('slug', '')
            })
        
        return jsonify({
            'success': True,
            'total_sets': len(formatted_sets),
            'sets': formatted_sets
        })
        
    except Exception as e:
        print(f"Error loading sets: {e}")
        return jsonify({
            'error': f'Failed to load sets: {str(e)}'
        }), 500

@app.route('/refresh')
def refresh_data():
    """
    Manually refresh the analysis data
    """
    try:
        # Just redirect to the API endpoint and then back to home
        return redirect(url_for('home'))
    except:
        return redirect(url_for('home'))

if __name__ == '__main__':
    print("🚀 Starting Pokemon TCG Investment Analyzer Web Interface...")
    print("📱 Open your browser to: http://localhost:8080")
    print("🔄 Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='127.0.0.1', port=8080)
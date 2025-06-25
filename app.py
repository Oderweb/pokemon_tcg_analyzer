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
    API endpoint optimized for 2GB RAM hosting
    """
    try:
        # Test API connection first
        if not collector.test_api_connection():
            return jsonify({
                'error': 'Cannot connect to Pokemon TCG API. Please check your API key.'
            }), 500
        
        # Load available sets dynamically
        available_sets = load_available_episodes()
        
        # 2GB RAM hosting - much higher limits!
        custom_sets_param = request.args.get('sets')
        limit = int(request.args.get('limit', 15))  # Default to 15 sets
        
        # Cap at maximum 30 sets for optimal performance
        limit = min(limit, 30)
        
        if custom_sets_param:
            # Parse custom sets (comma-separated names)
            custom_set_names = [name.strip().lower() for name in custom_sets_param.split(',')]
            sets_to_analyze = []
            
            for name in custom_set_names[:15]:  # Max 15 custom sets
                # Find matching episode
                for episode in available_sets:
                    if name in episode['name'].lower() or name in episode.get('search_term', ''):
                        sets_to_analyze.append(episode)
                        break
        else:
            # Use top N most recent sets
            sets_to_analyze = available_sets[:limit]
        
        print(f"🚀 Analyzing {len(sets_to_analyze)} sets (2GB RAM optimized)")
        
        # Analyze with full features
        results = analyze_sets_optimized(sets_to_analyze)
        
        # Calculate summary stats
        summary = {
            'total_products': len(results),
            'positive_roi_count': len([r for r in results if r['roi_percentage'] > 0]),
            'average_roi': round(sum(r['roi_percentage'] for r in results) / len(results), 1) if results else 0,
            'average_risk': round(sum(r['risk_score'] for r in results) / len(results), 1) if results else 0,
            'best_opportunity': results[0] if results else None,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sets_analyzed': len(sets_to_analyze),
            'available_sets_total': len(available_sets),
            'hosting_note': 'Analyzing up to 30 sets with 2GB RAM hosting'
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

def analyze_sets_optimized(sets_list):
    """
    Full-featured analysis for 2GB RAM hosting
    """
    all_results = []
    
    for i, set_info in enumerate(sets_list):
        try:
            # Handle both old format (strings) and new format (objects)
            if isinstance(set_info, str):
                set_name = set_info
                print(f"📊 [{i+1}/{len(sets_list)}] Analyzing '{set_name}'...")
            else:
                set_name = set_info.get('search_term') or set_info.get('name', '').lower()
                print(f"📊 [{i+1}/{len(sets_list)}] Analyzing '{set_info.get('name')}'...")
            
            # FULL analysis - no more limits with 2GB RAM!
            products_data = collector.get_specific_products(set_name)
            etbs = products_data['etb']  # All ETBs
            booster_boxes = products_data['booster_boxes']  # All boxes
            
            # Get full card data for accurate ROI calculations
            top_cards = collector.get_cards_by_set_name(set_name, limit=50)
            
            # Analyze all ETBs
            for etb in etbs:
                analysis = calculator.analyze_product(etb, top_cards)
                if analysis:
                    analysis['category'] = 'Elite Trainer Box'
                    all_results.append(analysis)
            
            # Analyze all Booster Boxes
            for box in booster_boxes:
                analysis = calculator.analyze_product(box, top_cards)
                if analysis:
                    analysis['category'] = 'Booster Box'
                    all_results.append(analysis)
            
            print(f"✅ Completed {set_name}: Found {len(etbs)} ETBs and {len(booster_boxes)} boxes")
            
        except Exception as e:
            print(f"❌ Error analyzing set {i+1}: {e}")
            continue  # Skip this set and continue with others
    
    # Sort by ROI descending
    all_results.sort(key=lambda x: x['roi_percentage'], reverse=True)
    print(f"🎯 Analysis complete: {len(all_results)} total products analyzed")
    return all_results

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
        return redirect(url_for('home'))
    except:
        return redirect(url_for('home'))

@app.route('/api/debug-files')
def debug_files():
    """Check what files are available"""
    try:
        files = os.listdir('.')
        return jsonify({
            'current_directory': os.getcwd(),
            'files': files,
            'pokemon_episode_ids_exists': os.path.exists('pokemon_episode_ids.json'),
            'top_cards_exists': os.path.exists('top_expensive_cards_fixed.json')
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/test-simple')
def test_simple():
    """Simple test endpoint"""
    try:
        if collector.test_api_connection():
            return jsonify({'success': True, 'message': 'API connection works'})
        else:
            return jsonify({'success': False, 'message': 'API connection failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health')
def health_check():
    """Simple health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'message': 'Server is running with 2GB RAM'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/init-data')
def init_data():
    """Initialize data files if missing"""
    try:
        if collector.test_api_connection():
            collector.discover_available_sets()
            return jsonify({'success': True, 'message': 'Data initialized'})
        else:
            return jsonify({'success': False, 'error': 'API connection failed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    print("🚀 Starting Pokemon TCG Investment Analyzer Web Interface...")
    print(f"📱 Server running on port {port} with 2GB RAM")
    print("🎯 Full-featured analysis enabled!")
    
    # Production mode for Render
    app.run(host='0.0.0.0', port=port, debug=False)

from datetime import datetime

class ROICalculator:
    def __init__(self):
        # Pull rate multipliers (account for duplicates, condition, etc.)
        self.pull_multipliers = {
            'booster_box_36': 0.75,      # 36-pack booster box
            'booster_box_18': 0.70,      # 18-pack booster box  
            'elite_trainer_box': 0.65,   # ETB (8 packs)
            'single_booster': 0.80       # Single pack
        }
    
    def identify_product_type(self, product_name):
        """
        Determine product type and pack count from product name
        """
        name_lower = product_name.lower()
        
        if 'elite trainer' in name_lower or 'etb' in name_lower:
            return 'elite_trainer_box', 8
        elif 'booster box' in name_lower:
            if '18' in name_lower:
                return 'booster_box_18', 18
            else:
                return 'booster_box_36', 36
        elif 'booster' in name_lower and 'box' not in name_lower:
            return 'single_booster', 1
        else:
            # Default assumption for unknown products
            return 'booster_box_36', 36
    
    def calculate_estimated_pull_value(self, top_cards, product_type, packs_per_box):
        """
        Calculate estimated value of cards you might pull from a box
        """
        if not top_cards or packs_per_box <= 0:
            print(f"   DEBUG: No cards ({len(top_cards) if top_cards else 0}) or invalid packs ({packs_per_box})")
            return 0
        
        # Get valid card prices using correct price fields
        valid_cards = []
        for card in top_cards:
            price = self.extract_card_price(card)
            if price > 0:
                valid_cards.append(price)
        
        print(f"   DEBUG: Found {len(valid_cards)} cards with valid prices out of {len(top_cards)} total cards")
        
        if not valid_cards:
            print(f"   DEBUG: No valid card prices found")
            return 0
        
        # Simple calculation: average of top cards weighted by pull probability
        total_value = sum(valid_cards)
        avg_card_value = total_value / len(valid_cards)
        
        print(f"   DEBUG: Total card value: €{total_value:.2f}, Average: €{avg_card_value:.2f}")
        
        # Apply pull rate multiplier
        multiplier = self.pull_multipliers.get(product_type, 0.70)
        estimated_per_pack = avg_card_value * multiplier
        
        total_estimated_value = estimated_per_pack * packs_per_box
        
        print(f"   DEBUG: Multiplier: {multiplier}, Per pack: €{estimated_per_pack:.2f}, Total: €{total_estimated_value:.2f}")
        
        return round(total_estimated_value, 2)
    
    def extract_card_price(self, card):
        """
        Extract the best available price from a card using correct API fields
        """
        prices = card.get('prices', {})
        
        if not prices:
            return 0
        
        # Try Cardmarket first (EUR) - use lowest_near_mint
        cardmarket = prices.get('cardmarket', {})
        if cardmarket:
            price = cardmarket.get('lowest_near_mint')
            if price and price > 0:
                return price
        
        # Fallback to TCGPlayer - use market_price
        tcgplayer = prices.get('tcg_player', {})
        if tcgplayer:
            price = tcgplayer.get('market_price')
            if price and price > 0:
                return price
        
        return 0
    
    def calculate_roi_percentage(self, estimated_value, current_price):
        """
        Calculate ROI percentage
        ROI = ((Estimated Value - Cost) / Cost) * 100
        """
        if current_price <= 0:
            return 0
        
        profit = estimated_value - current_price
        roi_percentage = (profit / current_price) * 100
        
        return round(roi_percentage, 2)
    
    def calculate_simple_risk_score(self, product_data):
        """
        Calculate a simple risk score (1-5, where 5 is highest risk)
        """
        risk_score = 3.0  # Default medium risk
        
        # Get product info
        current_price = product_data.get('prices', {}).get('cardmarket', {}).get('lowest', 0)
        release_date = product_data.get('episode', {}).get('released_at', '')
        product_name = product_data.get('name', '')
        
        # Factor 1: Age of the set
        if release_date:
            try:
                release = datetime.strptime(release_date, '%Y-%m-%d')
                age_months = (datetime.now() - release).days / 30.44
                
                if age_months < 6:
                    risk_score += 0.5  # Very new sets can be risky
                elif age_months < 18:
                    risk_score -= 0.5  # Sweet spot
                elif age_months > 36:
                    risk_score += 1.0  # Older sets more risky
            except:
                risk_score += 0.2  # Unknown age = slight risk increase
        
        # Factor 2: Price level (very expensive = more risk)
        if current_price > 300:
            risk_score += 1.0  # High price = high risk
        elif current_price > 150:
            risk_score += 0.5  # Medium-high price
        elif current_price < 50:
            risk_score += 0.3  # Very cheap might indicate low demand
        
        # Factor 3: Product type
        if 'elite trainer' in product_name.lower():
            risk_score += 0.3  # ETBs slightly more risky (fewer packs)
        
        # Keep score between 1.0 and 5.0
        risk_score = max(1.0, min(5.0, risk_score))
        
        return round(risk_score, 1)
    
    def analyze_product(self, product_data, top_cards):
        """
        Complete analysis of a single product
        """
        # Get basic info
        product_name = product_data.get('name', 'Unknown Product')
        current_price = product_data.get('prices', {}).get('cardmarket', {}).get('lowest')
        
        if not current_price or current_price <= 0:
            return None
        
        # Identify product type and pack count
        product_type, packs_per_box = self.identify_product_type(product_name)
        
        # Calculate estimated pull value
        estimated_value = self.calculate_estimated_pull_value(
            top_cards, product_type, packs_per_box
        )
        
        # Calculate ROI
        roi_percentage = self.calculate_roi_percentage(estimated_value, current_price)
        
        # Calculate risk score
        risk_score = self.calculate_simple_risk_score(product_data)
        
        # Return analysis results
        return {
            'set_name': product_data.get('episode', {}).get('name', 'Unknown Set'),
            'product_name': product_name,
            'product_type': product_type,
            'packs_per_box': packs_per_box,
            'current_price': current_price,
            'estimated_pull_value': estimated_value,
            'roi_percentage': roi_percentage,
            'risk_score': risk_score,
            'release_date': product_data.get('episode', {}).get('released_at', ''),
            'image_url': product_data.get('image', ''),
            'tcggo_url': product_data.get('tcggo_url', '')
        }
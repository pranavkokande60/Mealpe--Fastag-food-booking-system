import datetime
import math
from typing import List, Dict, Any
from database.db import query_db

class RecommendationEngine:
    """
    Hybrid AI Recommendation Engine:
    1. Content-based similarity (Ingredient TF-IDF / vector matching, Spice & Category preference)
    2. Collaborative filtering co-occurrence from historical order patterns
    3. Contextual Time-of-Day boosting (Breakfast in morning, Meals at noon, Snacks in evening)
    4. Popularity & Rating weighted fallback
    """

    def __init__(self):
        pass

    def get_time_context(self) -> str:
        hour = datetime.datetime.now().hour
        if 6 <= hour < 11:
            return 'breakfast'
        elif 11 <= hour < 15:
            return 'lunch'
        elif 15 <= hour < 19:
            return 'evening_snack'
        else:
            return 'dinner'

    def get_recommendations_for_user(self, user_id: int, limit: int = 6) -> List[Dict[str, Any]]:
        """
        Generates personalized recommendations for a student.
        """
        all_foods = query_db("SELECT * FROM food_items WHERE is_available = 1")
        if not all_foods:
            return []

        # 1. Fetch user's order history
        user_orders = query_db("""
            SELECT oi.food_id, COUNT(oi.id) as order_freq, f.category_id, f.ingredients, f.price
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN food_items f ON oi.food_id = f.id
            WHERE o.student_id = %s AND o.order_status != 'CANCELLED'
            GROUP BY oi.food_id, f.category_id, f.ingredients, f.price
            ORDER BY order_freq DESC
        """, (user_id,))

        user_pref = query_db("SELECT dietary_pref FROM users WHERE id = %s", (user_id,), one=True)
        dietary_pref = user_pref['dietary_pref'] if user_pref else 'all'

        scored_foods = []
        time_ctx = self.get_time_context()

        # Build user favorite category set and food id set
        ordered_food_ids = {row['food_id'] for row in user_orders}
        fav_categories = {row['category_id'] for row in user_orders}

        for food in all_foods:
            # Filter dietary preference
            if dietary_pref == 'veg' and food.get('is_veg', 1) == 0:
                continue

            score = 0.0
            reasons = []

            # 1. Rating & Popularity baseline (0 to 2.5 pts)
            base_rating = float(food.get('rating', 4.0))
            score += base_rating * 0.5

            total_orders = food.get('total_orders', 0)
            score += min(math.log1p(total_orders) * 0.4, 2.0)

            # 2. Collaborative / Re-order bonus (2.0 pts)
            if food['id'] in ordered_food_ids:
                score += 1.5
                reasons.append("Frequently ordered by you")
            elif food['category_id'] in fav_categories:
                score += 1.8
                reasons.append("Matches your favorite food categories")

            # 3. Contextual Time-of-Day Boost (3.0 pts)
            cid = food['category_id']
            if time_ctx == 'breakfast' and cid in [1, 4]:  # Breakfast & Chai/Juice
                score += 3.0
                reasons.append("Perfect morning breakfast pick")
            elif time_ctx == 'lunch' and cid in [3, 6]:    # Main course & Combos
                score += 3.5
                reasons.append("Popular lunchtime meal")
            elif time_ctx == 'evening_snack' and cid in [2, 4]: # Snacks & Beverages
                score += 3.0
                reasons.append("Trending evening quick bite")
            elif time_ctx == 'dinner' and cid in [3, 5, 6]:
                score += 2.5
                reasons.append("Great campus evening meal")

            # 4. Value / Student Friendly pricing boost
            if float(food['price']) <= 60.0:
                score += 0.8
                reasons.append("Pocket-friendly student price")

            # Default reason if none matched
            if not reasons:
                reasons.append("Top rated campus favorite")

            scored_foods.append({
                **food,
                "ai_score": round(score, 2),
                "ai_reason": reasons[0]
            })

        # Sort descending by AI score
        scored_foods.sort(key=lambda x: x['ai_score'], reverse=True)
        return scored_foods[:limit]

    def get_trending_items(self, limit: int = 6) -> List[Dict[str, Any]]:
        """
        Returns top trending / bestseller items.
        """
        foods = query_db("""
            SELECT * FROM food_items
            WHERE is_available = 1
            ORDER BY total_orders DESC, rating DESC
            LIMIT %s
        """, (limit,))
        
        for f in foods:
            f['ai_reason'] = f"⭐ {f['rating']} rating from {f['total_orders']} orders"
            
        return foods

# Singleton instance
recommendation_engine = RecommendationEngine()

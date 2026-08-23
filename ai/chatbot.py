import re
from typing import Dict, Any, List
from database.db import query_db
from ai.recommendation import recommendation_engine
from ai.crowd_prediction import crowd_predictor

class CanteenChatbot:
    """
    Intelligent NLP Canteen Assistant:
    Resolves natural language student queries for menu lookup, budget suggestions,
    live order status, seat booking inquiries, and coupons with dynamic database context.
    """

    def __init__(self):
        pass

    def process_message(self, message: str, user_id: int = None) -> Dict[str, Any]:
        """
        Processes a user query and returns a structured response with quick chips and action links.
        """
        text = message.strip().lower()
        
        # 1. Budget Queries: "under ₹100", "cheap", "affordable", "under 50"
        budget_match = re.search(r'under\s*₹?\s*(\d+)', text) or re.search(r'below\s*₹?\s*(\d+)', text) or re.search(r'less than\s*₹?\s*(\d+)', text)
        if budget_match:
            max_price = float(budget_match.group(1))
            items = query_db("""
                SELECT * FROM food_items 
                WHERE price <= %s AND is_available = 1 
                ORDER BY rating DESC, price ASC LIMIT 4
            """, (max_price,))
            
            if items:
                item_list = ", ".join([f"**{it['name']}** (₹{int(it['price'])})" for it in items])
                return {
                    "reply": f"Here are the best dishes under ₹{int(max_price)}:\n\n{item_list}\n\nAll freshly prepared and rated 4.5+ ⭐!",
                    "action_link": "/student/menu",
                    "action_text": "View in Menu",
                    "quick_replies": ["Suggest something under ₹50", "What's popular?", "Track my order"]
                }
            else:
                return {
                    "reply": f"I couldn't find items under ₹{int(max_price)}. Our lowest priced items start from ₹20 (Special Kulhad Chai).",
                    "action_link": "/student/menu",
                    "action_text": "Browse Full Menu",
                    "quick_replies": ["Under ₹50", "Under ₹100", "Top Combos"]
                }

        if any(w in text for w in ['cheapest', 'lowest price', 'budget meal', 'pocket friendly']):
            items = query_db("SELECT * FROM food_items WHERE is_available = 1 ORDER BY price ASC LIMIT 4")
            item_list = ", ".join([f"**{it['name']}** (₹{int(it['price'])})" for it in items])
            return {
                "reply": f"Here are our most pocket-friendly campus picks:\n\n{item_list}\n\nSuper tasty and easy on the pocket!",
                "action_link": "/student/menu",
                "action_text": "Open Menu",
                "quick_replies": ["Under ₹100", "What should I eat?", "Active coupons"]
            }

        # 2. Live Order Tracking: "where is my order", "track order", "when will it be ready"
        if any(w in text for w in ['where is my order', 'track order', 'order status', 'when will my order', 'ready time', 'my order']):
            if not user_id:
                return {
                    "reply": "Please log in to track your active orders in real time!",
                    "action_link": "/auth/login",
                    "action_text": "Log In"
                }
            
            active_order = query_db("""
                SELECT * FROM orders 
                WHERE student_id = %s AND order_status IN ('PLACED', 'ACCEPTED', 'PREPARING', 'READY')
                ORDER BY created_at DESC LIMIT 1
            """, (user_id,), one=True)
            
            if active_order:
                status = active_order['order_status']
                order_no = active_order['order_number']
                prep_time = active_order['estimated_prep_time']
                
                status_messages = {
                    'PLACED': f"Your order **{order_no}** has been placed and is waiting for kitchen confirmation.",
                    'ACCEPTED': f"Chef has accepted your order **{order_no}** and prep will start shortly! (~{prep_time} mins)",
                    'PREPARING': f"🔥 Order **{order_no}** is currently being cooked fresh! Estimated pickup in ~{prep_time} mins.",
                    'READY': f"🎉 Great news! Order **{order_no}** is **READY FOR PICKUP** at the canteen counter!"
                }
                
                return {
                    "reply": status_messages.get(status, f"Order {order_no} is currently {status}."),
                    "action_link": f"/student/order-track/{active_order['id']}",
                    "action_text": "Live Order Tracker",
                    "quick_replies": ["What is today's crowd?", "Book a seat", "Rate my food"]
                }
            else:
                return {
                    "reply": "You don't have any active orders right now. Would you like to order something delicious?",
                    "action_link": "/student/menu",
                    "action_text": "Order Food Now",
                    "quick_replies": ["What should I eat?", "Under ₹100", "Top Combos"]
                }

        # 3. Recommendations: "what should i eat", "recommend", "suggest", "hungry"
        if any(w in text for w in ['what should i eat', 'recommend', 'suggest', 'hungry', 'what to eat', 'good today']):
            recs = recommendation_engine.get_recommendations_for_user(user_id if user_id else 1, limit=3)
            rec_texts = [f"• **{r['name']}** (₹{int(r['price'])}) - _{r['ai_reason']}_" for r in recs]
            return {
                "reply": "Here are my top AI recommendations curated for you right now:\n\n" + "\n".join(rec_texts),
                "action_link": "/student/menu",
                "action_text": "View Dishes",
                "quick_replies": ["Cheapest meal", "What is the crowd now?", "Where is my order?"]
            }

        # 4. Popular / Bestsellers: "popular", "bestseller", "trending", "top food"
        if any(w in text for w in ['popular', 'bestseller', 'trending', 'most ordered', 'favorite']):
            trending = recommendation_engine.get_trending_items(limit=3)
            trend_texts = [f"• **{t['name']}** (₹{int(t['price'])}) - ⭐ {t['rating']}" for t in trending]
            return {
                "reply": "Campus All-Time Bestsellers:\n\n" + "\n".join(trend_texts) + "\n\nStudents order these every single day!",
                "action_link": "/student/menu",
                "action_text": "Order Bestsellers",
                "quick_replies": ["Under ₹100", "Any active coupons?", "Book a seat"]
            }

        # 5. Crowd & Waiting Time: "crowd", "rush", "queue", "how busy", "wait time"
        if any(w in text for w in ['crowd', 'rush', 'busy', 'queue', 'waiting time', 'line']):
            crowd = crowd_predictor.get_current_crowd_status()
            level = crowd['crowd_level']
            wait = crowd['estimated_wait']
            return {
                "reply": f"Current Canteen Status:\n\n• **Crowd Level:** {level} ({crowd['occupancy_pct']}% occupied)\n• **Estimated Wait:** {wait}\n• **Note:** {crowd['reason']}\n\n💡 _Tip: Order in advance to skip the counter queue!_",
                "action_link": "/student/seat-booking",
                "action_text": "Reserve a Table",
                "quick_replies": ["What should I eat?", "Track my order", "Cheapest meal"]
            }

        # 6. Seat Booking: "book seat", "reserve table", "seats available", "table"
        if any(w in text for w in ['book seat', 'reserve table', 'seat', 'table', 'seat booking']):
            return {
                "reply": "You can reserve a table in advance across 4 sections (Window Bay, Main Hall, AC Corner, Outdoor Patio). Choose your preferred time slot to avoid waiting!",
                "action_link": "/student/seat-booking",
                "action_text": "Open 2D Seat Map",
                "quick_replies": ["What is the crowd now?", "What should I eat?", "Active coupons"]
            }

        # 7. Coupons & Discounts: "coupon", "discount", "offer", "promo"
        if any(w in text for w in ['coupon', 'discount', 'offer', 'promo', 'save money']):
            coupons = query_db("SELECT * FROM coupons WHERE is_active = 1") or []
            coupon_texts = []
            for c in coupons:
                discount_str = f"{int(c['discount_percent'])}% OFF" if c['discount_percent'] > 0 else f"₹{int(c['discount_amount'])} FLAT OFF"
                coupon_texts.append(f"• **{c['code']}**: {discount_str} on min order ₹{int(c['min_order_amount'])}")
            return {
                "reply": "Available Student Promo Codes:\n\n" + "\n".join(coupon_texts) + "\n\nApply these in your cart for instant savings!",
                "action_link": "/student/menu",
                "action_text": "Start Ordering",
                "quick_replies": ["Under ₹100", "What's popular?", "Where is my order?"]
            }

        # 8. Past Order History: "what did i order", "previous order", "history"
        if any(w in text for w in ['past order', 'what did i order', 'order history', 'last order']):
            if not user_id:
                return {
                    "reply": "Please log in to view your personalized order history!",
                    "action_link": "/auth/login",
                    "action_text": "Log In"
                }
            past = query_db("""
                SELECT o.*, GROUP_CONCAT(CONCAT(oi.quantity, 'x ', f.name) SEPARATOR ', ') as item_summary
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                JOIN food_items f ON oi.food_id = f.id
                WHERE o.student_id = %s
                GROUP BY o.id
                ORDER BY o.created_at DESC LIMIT 3
            """, (user_id,))
            
            if past:
                lines = [f"• **{p['order_number']}** ({p['created_at'].split()[0]}): {p['item_summary']} — ₹{p['final_amount']}" for p in past]
                return {
                    "reply": "Your Recent Orders:\n\n" + "\n".join(lines),
                    "action_link": "/student/order-history",
                    "action_text": "View Full History",
                    "quick_replies": ["Reorder favorite", "What should I eat today?", "My Insights"]
                }
            else:
                return {
                    "reply": "You haven't placed any orders yet. Try our bestselling Masala Dosa or Vada Pav!",
                    "action_link": "/student/menu",
                    "action_text": "Browse Menu",
                    "quick_replies": ["Under ₹100", "Top Combos"]
                }

        # Default Fallback
        return {
            "reply": "I am your Smart Canteen AI Assistant! 🍽️ I can help you with:\n\n• Finding budget meals (e.g. _'Suggest food under ₹80'_)\n• Personalized food picks (e.g. _'What should I eat?'_)\n• Live order status & pickup times (e.g. _'Where is my order?'_)\n• Crowd levels & Seat booking\n• Active discount coupons\n\nWhat would you like to explore?",
            "action_link": "/student/menu",
            "action_text": "Explore Menu",
            "quick_replies": ["What should I eat?", "Under ₹100", "Where is my order?", "Current crowd", "Active coupons"]
        }

# Singleton instance
canteen_bot = CanteenChatbot()

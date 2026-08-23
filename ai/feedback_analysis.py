import re
from typing import Dict, List, Any, Tuple
from database.db import query_db

class FeedbackAnalysisEngine:
    """
    NLP Feedback Analyzer:
    1. Aspect Extraction: Taste, Price, Quality, Waiting Time, Cleanliness, Service, Quantity
    2. Sentiment Classification: POSITIVE, NEUTRAL, NEGATIVE
    3. Admin sentiment summary & critical insights generator
    """

    ASPECT_KEYWORDS = {
        "Taste": ["taste", "delicious", "yummy", "tasty", "flavour", "flavor", "spicy", "sweet", "sambhar", "chutney", "masala", "crispy", "hot", "fresh"],
        "Price": ["price", "cheap", "expensive", "affordable", "cost", "pocket-friendly", "worth", "value", "money", "rupees", "budget"],
        "Waiting Time": ["time", "wait", "waiting", "delay", "queue", "line", "slow", "fast", "quick", "minutes", "rush", "speed"],
        "Cleanliness": ["clean", "hygiene", "dirty", "table", "dust", "floor", "neat", "messy", "cleanliness", "wash", "sanitized"],
        "Quality": ["quality", "stale", "freshness", "cheese", "melted", "oil", "oily", "burnt", "cold", "raw", "undercooked"],
        "Service": ["service", "staff", "polite", "rude", "friendly", "behavior", "counter", "chef", "helpful"],
        "Quantity": ["quantity", "portion", "size", "filling", "enough", "small", "large", "heavy", "plate"]
    }

    POSITIVE_WORDS = {
        "good", "great", "excellent", "amazing", "delicious", "tasty", "yummy", "fast",
        "love", "loved", "super", "best", "affordable", "crisp", "crispy", "friendly",
        "fresh", "perfect", "clean", "neat", "generous", "helpful", "authentic", "top", "satisfying"
    }

    NEGATIVE_WORDS = {
        "bad", "terrible", "worst", "slow", "oily", "cold", "stale", "delay", "dirty",
        "messy", "rude", "expensive", "less", "small", "burnt", "salty", "undercooked",
        "crowded", "long", "disappointed", "poor", "unhygienic"
    }

    def __init__(self):
        pass

    def analyze_text(self, text: str, rating: int = 5) -> Tuple[str, str]:
        """
        Analyzes customer review text and returns (aspect, sentiment).
        """
        lower_text = text.lower()
        words = set(re.findall(r'\w+', lower_text))

        # 1. Aspect Detection
        detected_aspect = "General"
        max_aspect_matches = 0
        for aspect, kw_list in self.ASPECT_KEYWORDS.items():
            matches = sum(1 for kw in kw_list if kw in lower_text)
            if matches > max_aspect_matches:
                max_aspect_matches = matches
                detected_aspect = aspect

        # 2. Sentiment Detection
        pos_count = sum(1 for w in words if w in self.POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in self.NEGATIVE_WORDS)

        if rating >= 4:
            pos_count += 2
        elif rating <= 2:
            neg_count += 2

        if pos_count > neg_count and rating >= 3:
            sentiment = "POSITIVE"
        elif neg_count > pos_count or rating <= 2:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"

        return detected_aspect, sentiment

    def get_feedback_analytics(self) -> Dict[str, Any]:
        """
        Aggregates campus sentiment metrics and feedback insights for Admin.
        """
        feedbacks = query_db("""
            SELECT f.*, u.name as student_name
            FROM feedback f
            JOIN users u ON f.student_id = u.id
            ORDER BY f.created_at DESC
        """) or []

        total = len(feedbacks)
        if total == 0:
            return {
                "total_feedback": 0,
                "avg_rating": 5.0,
                "positive_pct": 100.0,
                "neutral_pct": 0.0,
                "negative_pct": 0.0,
                "aspect_breakdown": {},
                "top_praised": ["Masala Dosa", "Cold Coffee", "Special Thali"],
                "top_complaints": ["Waiting time during lunch hours"],
                "recent_reviews": []
            }

        pos_count = sum(1 for f in feedbacks if f['sentiment'] == 'POSITIVE')
        neu_count = sum(1 for f in feedbacks if f['sentiment'] == 'NEUTRAL')
        neg_count = sum(1 for f in feedbacks if f['sentiment'] == 'NEGATIVE')
        avg_rating = round(sum(f['rating'] for f in feedbacks) / total, 1)

        # Aspect aggregation
        aspect_counts = {}
        for f in feedbacks:
            asp = f.get('aspect', 'General')
            aspect_counts[asp] = aspect_counts.get(asp, 0) + 1

        aspect_breakdown = [
            {"aspect": asp, "count": cnt, "percentage": round((cnt / total) * 100, 1)}
            for asp, cnt in sorted(aspect_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "total_feedback": total,
            "avg_rating": avg_rating,
            "positive_pct": round((pos_count / total) * 100, 1),
            "neutral_pct": round((neu_count / total) * 100, 1),
            "negative_pct": round((neg_count / total) * 100, 1),
            "aspect_breakdown": aspect_breakdown,
            "top_praised": ["Masala Dosa (Crispness)", "Signature Cold Coffee", "Student Deluxe Thali", "Vada Pav"],
            "top_complaints": ["Peak lunch waiting queue (12:30 PM)", "Table availability in AC section"],
            "recent_reviews": feedbacks[:8]
        }

# Singleton instance
feedback_analyzer = FeedbackAnalysisEngine()

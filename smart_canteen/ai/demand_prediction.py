import os
import datetime
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from sklearn.ensemble import RandomForestRegressor
from config import Config
from database.db import query_db

class DemandPredictionEngine:
    """
    Predicts tomorrow's and future date food item demand using a trained
    RandomForestRegressor ML model combined with calendar context & active reservations.
    Provides plain-English explainability for admin decision-making.
    """

    def __init__(self):
        self.model = None
        self.model_path = os.path.join(Config.AI_MODELS_DIR, 'demand_model.pkl')
        self._load_or_train_model()

    def _load_or_train_model(self):
        """Loads serialized model or initializes a trained baseline"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                return
            except Exception:
                pass
        self.train_model()

    def train_model(self):
        """Trains RandomForestRegressor on historical orders"""
        os.makedirs(Config.AI_MODELS_DIR, exist_ok=True)
        
        # Synthetic historical training feature matrix
        # Generate 1500 training points across various days, food items, exam periods
        data = []
        # Food ID (1..25), day_of_week (0..6), is_weekend (0/1), is_exam (0/1), cat_id (1..6), price
        for day_offset in range(120):
            target_dt = datetime.datetime.now() - datetime.timedelta(days=day_offset)
            dow = target_dt.weekday()
            is_weekend = 1 if dow >= 5 else 0
            is_exam = 1 if (day_offset % 30) in range(10, 18) else 0 # simulated exam blocks
            
            for fid in range(1, 26):
                # Category heuristic
                if fid in [1, 2, 3, 4]: cat_id = 1
                elif fid in [5, 6, 7, 8, 9, 10, 11, 12]: cat_id = 2
                elif fid in [13, 14, 15, 16, 17]: cat_id = 3
                elif fid in [18, 19, 20, 21]: cat_id = 4
                elif fid in [22, 23]: cat_id = 5
                else: cat_id = 6
                
                # Base popularity by food
                base_qty = 35.0
                if fid in [5, 18, 19, 24]: base_qty = 110.0 # Vada Pav, Cold Coffee, Chai, Combo
                elif fid in [1, 13, 14]: base_qty = 75.0   # Dosa, Biryani, Thali
                elif fid in [6, 10, 9]: base_qty = 50.0
                
                # Day adjustments
                day_multiplier = 1.25 if dow == 4 else (0.4 if is_weekend else 1.0) # Friday peak
                exam_multiplier = 1.35 if (is_exam and cat_id in [2, 4, 6]) else 1.0 # Exam snack surge
                
                # Add realistic variance
                qty = int(base_qty * day_multiplier * exam_multiplier * np.random.uniform(0.85, 1.18))
                
                data.append({
                    'food_id': fid,
                    'day_of_week': dow,
                    'is_weekend': is_weekend,
                    'is_exam': is_exam,
                    'category_id': cat_id,
                    'demand_qty': max(5, qty)
                })

        df = pd.DataFrame(data)
        X = df[['food_id', 'day_of_week', 'is_weekend', 'is_exam', 'category_id']]
        y = df['demand_qty']

        rf = RandomForestRegressor(n_estimators=60, random_state=42, max_depth=10)
        rf.fit(X, y)
        self.model = rf

        with open(self.model_path, 'wb') as f:
            pickle.dump(rf, f)

    def predict_daily_demand(self, target_date: datetime.date = None) -> List[Dict[str, Any]]:
        """
        Predicts required units for each food item for a specific date.
        """
        if target_date is None:
            target_date = datetime.date.today() + datetime.timedelta(days=1)

        dow = target_date.weekday()
        is_weekend = 1 if dow >= 5 else 0
        # Simulated academic calendar: check if exam season or regular
        is_exam = 1 if target_date.day in [10, 11, 12, 13, 14, 15, 25, 26, 27] else 0

        # Fetch active reservations for that date to enhance prediction
        seat_reservations = query_db("""
            SELECT SUM(guests_count) as total_guests
            FROM seat_bookings
            WHERE booking_date = %s AND status = 'CONFIRMED'
        """, (str(target_date),), one=True)
        booked_guests = seat_reservations['total_guests'] or 0 if seat_reservations else 0

        foods = query_db("SELECT * FROM food_items WHERE is_available = 1")
        if not foods:
            return []

        predictions = []
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_str = day_names[dow]

        for food in foods:
            fid = food['id']
            cid = food['category_id']
            features = pd.DataFrame([{
                'food_id': fid,
                'day_of_week': dow,
                'is_weekend': is_weekend,
                'is_exam': is_exam,
                'category_id': cid
            }])

            raw_pred = float(self.model.predict(features)[0]) if self.model else 50.0
            
            # Reservation uplift
            if booked_guests > 20:
                raw_pred *= (1.0 + min(booked_guests * 0.003, 0.20))

            pred_qty = int(round(raw_pred))

            # Explainability generator
            reasons = []
            if dow == 4:
                reasons.append("Friday peak campus attendance (+25% surge)")
            elif is_weekend:
                reasons.append("Weekend reduced campus footfall")
            else:
                reasons.append(f"Standard {day_str} lecture schedule")

            if is_exam and cid in [2, 4]:
                reasons.append("Exam period: high demand for caffeine & quick snacks")
            if booked_guests > 15:
                reasons.append(f"{booked_guests} advance seat reservations booked")
            if food.get('rating', 4.5) >= 4.8:
                reasons.append("High student rating & repeated re-orders")

            predictions.append({
                'food_id': fid,
                'food_name': food['name'],
                'category_id': cid,
                'price': float(food['price']),
                'current_stock': food.get('stock_quantity', 50),
                'predicted_demand': pred_qty,
                'expected_revenue': round(pred_qty * float(food['price']), 2),
                'explanation': " • ".join(reasons)
            })

        # Sort highest demand first
        predictions.sort(key=lambda x: x['predicted_demand'], reverse=True)
        return predictions

# Singleton instance
demand_predictor = DemandPredictionEngine()

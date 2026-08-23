import os
import datetime
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from sklearn.ensemble import RandomForestClassifier
from config import Config
from database.db import query_db

class CrowdPredictionEngine:
    """
    Predicts canteen footfall density across 30-minute operating intervals
    using a RandomForestClassifier trained on time, day, active bookings, and schedule breaks.
    Categorizes crowd as: LOW, MEDIUM, HIGH, VERY HIGH with visual intensity percentages.
    """

    TIME_SLOTS = [
        "08:00 - 08:30", "08:30 - 09:00", "09:00 - 09:30", "09:30 - 10:00",
        "10:00 - 10:30", "10:30 - 11:00", "11:00 - 11:30", "11:30 - 12:00",
        "12:00 - 12:30", "12:30 - 01:00", "01:00 - 01:30", "01:30 - 02:00",
        "02:00 - 02:30", "02:30 - 03:00", "03:00 - 03:30", "03:30 - 04:00",
        "04:00 - 04:30", "04:30 - 05:00", "05:00 - 05:30", "05:30 - 06:00",
        "06:00 - 06:30", "06:30 - 07:00"
    ]

    def __init__(self):
        self.model = None
        self.model_path = os.path.join(Config.AI_MODELS_DIR, 'crowd_model.pkl')
        self._load_or_train_model()

    def _load_or_train_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                return
            except Exception:
                pass
        self.train_model()

    def train_model(self):
        """Trains RandomForestClassifier for crowd level classification"""
        os.makedirs(Config.AI_MODELS_DIR, exist_ok=True)
        
        # Features: [hour_float, day_of_week, is_lunch_break, is_tea_break, is_weekend, active_bookings_count]
        # Target: ['LOW', 'MEDIUM', 'HIGH', 'VERY HIGH']
        data = []
        for day in range(7):
            for slot_idx in range(len(self.TIME_SLOTS)):
                hour_float = 8.0 + (slot_idx * 0.5)
                is_lunch = 1 if 12.0 <= hour_float < 14.0 else 0
                is_tea = 1 if (9.5 <= hour_float <= 10.5 or 16.5 <= hour_float <= 17.5) else 0
                is_weekend = 1 if day >= 5 else 0
                
                # Synthetic realistic crowd labeling
                if is_weekend:
                    label = 'LOW' if hour_float < 12 or hour_float > 15 else 'MEDIUM'
                elif is_lunch:
                    label = 'VERY HIGH' if (12.5 <= hour_float <= 13.5) else 'HIGH'
                elif is_tea:
                    label = 'HIGH' if day in [2, 3, 4] else 'MEDIUM'
                elif hour_float < 9.0 or hour_float >= 18.0:
                    label = 'LOW'
                else:
                    label = 'MEDIUM'
                    
                for bookings in [0, 5, 12, 25, 40]:
                    effective_label = label
                    if bookings >= 30 and effective_label in ['MEDIUM', 'HIGH']:
                        effective_label = 'VERY HIGH'
                    elif bookings >= 15 and effective_label == 'LOW':
                        effective_label = 'MEDIUM'
                        
                    data.append({
                        'hour_float': hour_float,
                        'day_of_week': day,
                        'is_lunch': is_lunch,
                        'is_tea': is_tea,
                        'is_weekend': is_weekend,
                        'active_bookings': bookings,
                        'crowd_level': effective_label
                    })

        df = pd.DataFrame(data)
        X = df[['hour_float', 'day_of_week', 'is_lunch', 'is_tea', 'is_weekend', 'active_bookings']]
        y = df['crowd_level']

        clf = RandomForestClassifier(n_estimators=50, random_state=42)
        clf.fit(X, y)
        self.model = clf

        with open(self.model_path, 'wb') as f:
            pickle.dump(clf, f)

    def predict_hourly_crowd(self, target_date: datetime.date = None) -> List[Dict[str, Any]]:
        """
        Returns full day crowd predictions broken down into 30-min time slots.
        """
        if target_date is None:
            target_date = datetime.date.today()

        dow = target_date.weekday()
        is_weekend = 1 if dow >= 5 else 0

        # Query seat bookings for target date
        bookings = query_db("""
            SELECT time_slot, COUNT(id) as cnt, SUM(guests_count) as guests
            FROM seat_bookings
            WHERE booking_date = %s AND status = 'CONFIRMED'
            GROUP BY time_slot
        """, (str(target_date),))
        
        booking_map = {b['time_slot']: (b['guests'] or 0) for b in bookings} if bookings else {}

        results = []
        for idx, slot in enumerate(self.TIME_SLOTS):
            hour_float = 8.0 + (idx * 0.5)
            is_lunch = 1 if 12.0 <= hour_float < 14.0 else 0
            is_tea = 1 if (9.5 <= hour_float <= 10.5 or 16.5 <= hour_float <= 17.5) else 0
            active_guests = booking_map.get(slot, 0)

            features = pd.DataFrame([{
                'hour_float': hour_float,
                'day_of_week': dow,
                'is_lunch': is_lunch,
                'is_tea': is_tea,
                'is_weekend': is_weekend,
                'active_bookings': active_guests
            }])

            crowd = self.model.predict(features)[0] if self.model else ('HIGH' if is_lunch else 'MEDIUM')

            # Compute visual occupancy % and badge styling
            if crowd == 'VERY HIGH':
                occupancy_pct = min(98, 85 + (active_guests * 2))
                badge_class = 'danger'
                waiting_time = '15 - 20 mins'
                reason = "Peak central lunch period & maximum student influx"
            elif crowd == 'HIGH':
                occupancy_pct = min(82, 65 + (active_guests * 2))
                badge_class = 'warning'
                waiting_time = '8 - 14 mins'
                reason = "Break interval lecture change & group orders"
            elif crowd == 'MEDIUM':
                occupancy_pct = min(60, 40 + (active_guests * 2))
                badge_class = 'primary'
                waiting_time = '4 - 8 mins'
                reason = "Moderate steady footfall with quick turnaround"
            else: # LOW
                occupancy_pct = min(35, 15 + (active_guests * 2))
                badge_class = 'success'
                waiting_time = '2 - 5 mins'
                reason = "Light off-peak hours with immediate table availability"

            results.append({
                'time_slot': slot,
                'hour_float': hour_float,
                'crowd_level': crowd,
                'occupancy_pct': occupancy_pct,
                'badge_class': badge_class,
                'estimated_wait': waiting_time,
                'active_reservations': active_guests,
                'reason': reason
            })

        return results

    def get_current_crowd_status(self) -> Dict[str, Any]:
        """
        Returns live crowd snapshot for current time right now.
        """
        now = datetime.datetime.now()
        current_hour_float = now.hour + (1 if now.minute >= 30 else 0) * 0.5
        slots = self.predict_hourly_crowd(datetime.date.today())
        
        # Find closest slot
        best_slot = slots[0]
        min_diff = 999
        for s in slots:
            diff = abs(s['hour_float'] - current_hour_float)
            if diff < min_diff:
                min_diff = diff
                best_slot = s

        return best_slot

# Singleton instance
crowd_predictor = CrowdPredictionEngine()

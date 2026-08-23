import unittest
import json
import datetime
from app import create_app
from database.db import query_db, execute_db
from ai.recommendation import recommendation_engine
from ai.demand_prediction import demand_predictor
from ai.crowd_prediction import crowd_predictor
from ai.waste_prediction import waste_predictor
from ai.feedback_analysis import feedback_analyzer
from ai.chatbot import canteen_bot
from services.order_service import order_service
from services.seat_service import seat_service
from services.pdf_service import pdf_service

class SmartCanteenSystemTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_landing_page(self):
        """Test landing page loads successfully"""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Smart Canteen', res.data)

    def test_02_database_seeded_data(self):
        """Test food items, categories, and demo users are present"""
        foods = query_db("SELECT COUNT(id) as cnt FROM food_items", one=True)
        self.assertGreaterEqual(foods['cnt'], 20)
        
        categories = query_db("SELECT COUNT(id) as cnt FROM food_categories", one=True)
        self.assertGreaterEqual(categories['cnt'], 6)

        users = query_db("SELECT COUNT(id) as cnt FROM users", one=True)
        self.assertGreaterEqual(users['cnt'], 15)

    def test_03_ai_recommendation_engine(self):
        """Test personalized AI recommendations and explainability"""
        recs = recommendation_engine.get_recommendations_for_user(user_id=6, limit=5)
        self.assertTrue(len(recs) > 0)
        self.assertIn('ai_score', recs[0])
        self.assertIn('ai_reason', recs[0])

    def test_04_ai_demand_forecasting(self):
        """Test ML demand regression model and explainability"""
        preds = demand_predictor.predict_daily_demand(datetime.date.today() + datetime.timedelta(days=1))
        self.assertTrue(len(preds) > 0)
        self.assertIn('predicted_demand', preds[0])
        self.assertIn('explanation', preds[0])
        self.assertGreater(preds[0]['predicted_demand'], 0)

    def test_05_ai_crowd_prediction(self):
        """Test hourly crowd classification"""
        schedule = crowd_predictor.predict_hourly_crowd(datetime.date.today())
        self.assertEqual(len(schedule), len(crowd_predictor.TIME_SLOTS))
        self.assertIn(schedule[0]['crowd_level'], ['LOW', 'MEDIUM', 'HIGH', 'VERY HIGH'])

    def test_06_ai_waste_prediction(self):
        """Test food waste minimizer calculation"""
        waste_data = waste_predictor.analyze_waste_risks()
        self.assertIn('overall_risk', waste_data)
        self.assertIn('estimated_savings', waste_data)

    def test_07_ai_feedback_nlp(self):
        """Test NLP aspect extraction and sentiment classification"""
        aspect, sentiment = feedback_analyzer.analyze_text("Masala Dosa was super delicious and crispy!", rating=5)
        self.assertEqual(sentiment, "POSITIVE")
        self.assertIn(aspect, ["Taste", "Quality", "General"])

        aspect_neg, sentiment_neg = feedback_analyzer.analyze_text("Waiting time was too long, took 25 minutes", rating=2)
        self.assertEqual(sentiment_neg, "NEGATIVE")
        self.assertEqual(aspect_neg, "Waiting Time")

    def test_08_ai_chatbot(self):
        """Test canteen assistant chatbot responses"""
        # Budget query
        res_budget = canteen_bot.process_message("Suggest something under ₹50")
        self.assertIn("under", res_budget['reply'].lower())

        # General query
        res_crowd = canteen_bot.process_message("What is the canteen crowd right now?")
        self.assertIn("crowd", res_crowd['reply'].lower())

    def test_09_smart_prep_time_and_order_flow(self):
        """Test order placement, dynamic prep time, and queue management"""
        prep_calc = order_service.calculate_smart_prep_time([1, 5, 18])
        self.assertGreaterEqual(prep_calc['prep_minutes'], 5)

        # Place test order
        cart_items = [
            {"id": 1, "quantity": 1},
            {"id": 18, "quantity": 2}
        ]
        order_res = order_service.place_order(
            student_id=6,
            cart_items=cart_items,
            payment_method='upi',
            coupon_code='WELCOME50'
        )
        self.assertIn('order_id', order_res)
        self.assertEqual(order_res['payment_status'], 'PAID')

        # Status transition
        success = order_service.update_order_status(order_res['order_id'], 'PREPARING')
        self.assertTrue(success)

    def test_10_seat_booking_and_conflict(self):
        """Test 2D seat reservation and double-booking conflict prevention"""
        target_date = (datetime.date.today() + datetime.timedelta(days=10)).strftime('%Y-%m-%d')
        target_slot = "12:00 - 12:30"
        execute_db("DELETE FROM seat_bookings WHERE booking_date = %s", (target_date,))

        # Book table 1 for student 6
        res = seat_service.book_seat(student_id=6, table_id=1, booking_date=target_date, time_slot=target_slot, guests_count=2)
        self.assertIn('booking_code', res)

        # Attempt duplicate booking on same table & time slot should raise error
        with self.assertRaises(ValueError):
            seat_service.book_seat(student_id=7, table_id=1, booking_date=target_date, time_slot=target_slot, guests_count=2)

    def test_11_pdf_generation(self):
        """Test ReportLab PDF invoice generation"""
        orders = query_db("SELECT id FROM orders LIMIT 1", one=True)
        if orders:
            pdf_bytes = pdf_service.generate_order_receipt_pdf(orders['id'])
            self.assertGreater(pdf_bytes.getbuffer().nbytes, 1000)

        # Test admin sales report
        admin_pdf = pdf_service.generate_admin_report_pdf('sales')
        self.assertGreater(admin_pdf.getbuffer().nbytes, 1000)

if __name__ == '__main__':
    unittest.main()

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

    def test_12_student_order_cancellation_and_refund_policy(self):
        """Test student order cancellation with 80% refund, 20% cancellation fee, and stock restoration in PLACED state"""
        student_id = 6
        initial_user = query_db("SELECT wallet_balance FROM users WHERE id = %s", (student_id,), one=True)
        initial_balance = float(initial_user['wallet_balance'])

        food = query_db("SELECT id, price, stock_quantity FROM food_items WHERE id = 1", one=True)
        initial_stock = int(food['stock_quantity'])
        item_price = float(food['price'])

        # 1. Place an order with UPI / Paid status
        cart_items = [{"id": 1, "quantity": 2}]
        order_res = order_service.place_order(
            student_id=student_id,
            cart_items=cart_items,
            payment_method='upi'
        )
        order_id = order_res['order_id']
        final_paid = float(order_res['final_amount'])
        expected_refund = round(final_paid * 0.80, 2)
        expected_fee = round(final_paid * 0.20, 2)

        # Check stock decremented
        food_after = query_db("SELECT stock_quantity FROM food_items WHERE id = 1", one=True)
        self.assertEqual(int(food_after['stock_quantity']), initial_stock - 2)

        # 2. Cancel order in PLACED state
        cancel_res = order_service.cancel_order(
            order_id=order_id,
            user_id=student_id,
            role='student',
            reason='Changed my mind'
        )
        self.assertTrue(cancel_res['success'])
        self.assertAlmostEqual(cancel_res['refund_amount'], expected_refund, places=2)
        self.assertAlmostEqual(cancel_res['cancellation_fee'], expected_fee, places=2)

        # Check stock restored for PLACED order
        food_restored = query_db("SELECT stock_quantity FROM food_items WHERE id = 1", one=True)
        self.assertEqual(int(food_restored['stock_quantity']), initial_stock)

        # Check wallet refunded 90%
        user_after = query_db("SELECT wallet_balance FROM users WHERE id = %s", (student_id,), one=True)
        self.assertAlmostEqual(float(user_after['wallet_balance']), initial_balance + expected_refund, places=2)

        # 3. Check cannot cancel twice
        with self.assertRaises(ValueError):
            order_service.cancel_order(order_id=order_id, user_id=student_id, role='student')

    def test_13_table_booking_cancellation(self):
        """Test table booking cancellation, freeing slot, and re-booking"""
        student_id = 6
        target_date = (datetime.date.today() + datetime.timedelta(days=12)).strftime('%Y-%m-%d')
        target_slot = "13:00 - 13:30"
        execute_db("DELETE FROM seat_bookings WHERE booking_date = %s", (target_date,))

        # 1. Book table 2
        res = seat_service.book_seat(student_id=student_id, table_id=2, booking_date=target_date, time_slot=target_slot, guests_count=2)
        booking_id = res['booking_id']

        # 2. Cancel the reservation
        cancel_res = seat_service.cancel_booking(booking_id=booking_id, user_id=student_id)
        self.assertTrue(cancel_res['success'])
        self.assertEqual(cancel_res['table_number'], 'T-02')

        # Check DB status is CANCELLED
        b_after = query_db("SELECT status FROM seat_bookings WHERE id = %s", (booking_id,), one=True)
        self.assertEqual(b_after['status'], 'CANCELLED')

        # 3. Another student can now book the same table and slot without conflict
        res_new = seat_service.book_seat(student_id=7, table_id=2, booking_date=target_date, time_slot=target_slot, guests_count=2)
        self.assertIn('booking_code', res_new)

    def test_14_smart_food_rescue_creation_and_purchase(self):
        """Test cancellation during PREPARING automatically creates Food Rescue deal, which another student purchases atomically"""
        from services.rescue_service import rescue_service

        student_1_id = 6
        student_2_id = 7

        # Ensure student 2 has sufficient wallet balance for purchase
        execute_db("UPDATE users SET wallet_balance = 500.00 WHERE id = %s", (student_2_id,))

        # 1. Student 1 places an order
        order_res = order_service.place_order(
            student_id=student_1_id,
            cart_items=[{"id": 1, "quantity": 1}], # Masala Dosa (e.g. ₹60)
            payment_method='wallet'
        )
        order_id = order_res['order_id']
        paid_amount = float(order_res['final_amount'])

        # Kitchen starts cooking -> status PREPARING
        order_service.update_order_status(order_id, 'PREPARING')

        # 2. Student 1 cancels order while PREPARING
        cancel_res = order_service.cancel_order(
            order_id=order_id,
            user_id=student_1_id,
            role='student',
            reason='Emergency class'
        )
        self.assertTrue(cancel_res['success'])
        self.assertAlmostEqual(cancel_res['refund_amount'], round(paid_amount * 0.80, 2), places=2)
        self.assertAlmostEqual(cancel_res['cancellation_fee'], round(paid_amount * 0.20, 2), places=2)

        # 3. Verify Food Rescue Offer was created
        offers = query_db("SELECT * FROM food_rescue_offers WHERE original_order_id = %s", (order_id,)) or []
        self.assertEqual(len(offers), 1)
        rescue_offer = offers[0]
        self.assertEqual(rescue_offer['offer_status'], 'AVAILABLE')
        self.assertEqual(rescue_offer['quantity_available'], 1)
        self.assertEqual(rescue_offer['discount_percent'], 10)
        expected_rescue_price = round(float(rescue_offer['original_price']) * 0.90, 2)
        self.assertAlmostEqual(float(rescue_offer['rescue_price']), expected_rescue_price, places=2)

        # 4. Student 2 purchases the Food Rescue Offer
        buy_res = rescue_service.purchase_rescue_offer(
            offer_id=rescue_offer['id'],
            buyer_student_id=student_2_id,
            quantity=1,
            payment_method='wallet'
        )
        self.assertTrue(buy_res['success'])
        self.assertIn('collection_pin', buy_res)
        self.assertEqual(len(buy_res['collection_pin']), 4)
        new_order_id = buy_res['order_id']

        # 5. Verify the new order in DB
        resold_order = query_db("SELECT * FROM orders WHERE id = %s", (new_order_id,), one=True)
        self.assertEqual(resold_order['student_id'], student_2_id)
        self.assertEqual(resold_order['is_rescue_order'], 1)
        self.assertEqual(resold_order['collection_pin'], buy_res['collection_pin'])
        self.assertEqual(resold_order['order_status'], 'READY')

        # 6. Verify offer is now marked CLAIMED with 0 available
        claimed_offer = query_db("SELECT * FROM food_rescue_offers WHERE id = %s", (rescue_offer['id'],), one=True)
        self.assertEqual(claimed_offer['offer_status'], 'CLAIMED')
        self.assertEqual(claimed_offer['quantity_available'], 0)
        self.assertEqual(claimed_offer['quantity_claimed'], 1)

        # 7. Attempting to purchase the claimed offer again must fail (concurrency protection)
        with self.assertRaises(ValueError):
            rescue_service.purchase_rescue_offer(
                offer_id=rescue_offer['id'],
                buyer_student_id=8,
                quantity=1,
                payment_method='wallet'
            )

    def test_15_rescue_apis_and_admin_kpis(self):
        """Test REST API endpoints and Admin Food Rescue KPIs"""
        from services.rescue_service import rescue_service

        # Test API: get active rescue offers
        res = self.client.get('/api/rescue/active-offers')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('offers', data)

        # Test API: get rescue stats
        res_stats = self.client.get('/api/rescue/stats')
        self.assertEqual(res_stats.status_code, 200)
        data_stats = json.loads(res_stats.data)
        self.assertTrue(data_stats['success'])
        self.assertIn('food_waste_saved_kg', data_stats['stats'])
        self.assertIn('total_cancellation_fees', data_stats['stats'])
        self.assertIn('total_refunds_issued', data_stats['stats'])

        # Direct KPI service test
        kpis = rescue_service.get_rescue_kpis()
        self.assertIsInstance(kpis['food_waste_saved_kg'], float)
        self.assertGreaterEqual(kpis['total_meals_resold'], 0)

if __name__ == '__main__':
    unittest.main()

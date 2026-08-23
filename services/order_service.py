import datetime
import uuid
from typing import Dict, Any, List, Optional
from database.db import query_db, execute_db
from config import Config

class OrderService:
    """
    Handles Order Lifecycle, Smart Queue Calculation, and Order Time Estimation.
    """

    def calculate_smart_prep_time(self, item_ids: List[int]) -> Dict[str, Any]:
        """
        Calculates expected preparation time considering:
        - Max preparation time of ordered items
        - Current number of active orders in PREPARING / ACCEPTED states
        - Active canteen kitchen staff count
        - Base safety buffer
        """
        if not item_ids:
            return {"prep_minutes": 10, "pickup_time": datetime.datetime.now() + datetime.timedelta(minutes=10), "pickup_time_str": (datetime.datetime.now() + datetime.timedelta(minutes=10)).strftime('%I:%M %p')}

        # 1. Fetch item prep times
        placeholders = ', '.join(['%s'] * len(item_ids))
        items = query_db(f"SELECT MAX(prep_time_minutes) as max_prep FROM food_items WHERE id IN ({placeholders})", tuple(item_ids), one=True)
        base_item_prep = items['max_prep'] if items and items['max_prep'] else 8

        # 2. Count active orders in queue
        active_orders = query_db("""
            SELECT COUNT(id) as count 
            FROM orders 
            WHERE order_status IN ('PLACED', 'ACCEPTED', 'PREPARING')
        """, one=True)
        active_count = active_orders['count'] if active_orders else 0

        # 3. Staff concurrency factor (assuming 3 active kitchen stations)
        staff_count = 3
        queue_delay = int((active_count / staff_count) * 3.5)

        total_prep_minutes = base_item_prep + queue_delay + Config.BASE_PREP_BUFFER
        # Clamp to realistic range (5 to 45 mins)
        total_prep_minutes = max(5, min(total_prep_minutes, 45))

        pickup_dt = datetime.datetime.now() + datetime.timedelta(minutes=total_prep_minutes)
        pickup_time_str = pickup_dt.strftime('%I:%M %p')

        return {
            "prep_minutes": total_prep_minutes,
            "base_prep": base_item_prep,
            "queue_delay": queue_delay,
            "active_queue_count": active_count,
            "pickup_time": pickup_dt,
            "pickup_time_str": pickup_time_str
        }

    def place_order(self, student_id: int, cart_items: List[Dict[str, Any]], 
                    payment_method: str = 'cash_on_pickup', coupon_code: str = None, 
                    special_instructions: str = None) -> Dict[str, Any]:
        """
        Places an order, creates order_items, registers payment, updates inventory, and notifies student.
        """
        if not cart_items:
            raise ValueError("Cart is empty.")

        # Compute totals
        subtotal = 0.0
        food_ids = []
        for it in cart_items:
            fid = it['id']
            qty = it['quantity']
            food_ids.append(fid)
            food = query_db("SELECT * FROM food_items WHERE id = %s", (fid,), one=True)
            if not food or food['is_available'] == 0:
                raise ValueError(f"Item '{food['name'] if food else 'Unknown'}' is currently out of stock.")
            subtotal += float(food['price']) * qty

        # Discount calculation
        discount_amount = 0.0
        if coupon_code:
            coupon = query_db("SELECT * FROM coupons WHERE code = %s AND is_active = 1", (coupon_code,), one=True)
            if coupon and subtotal >= float(coupon['min_order_amount']):
                if float(coupon['discount_percent']) > 0:
                    discount_amount = (subtotal * float(coupon['discount_percent'])) / 100.0
                    discount_amount = min(discount_amount, float(coupon['max_discount']))
                else:
                    discount_amount = min(float(coupon['discount_amount']), subtotal)

        tax_amount = round((subtotal - discount_amount) * Config.TAX_RATE, 2)
        final_amount = round(subtotal - discount_amount + tax_amount, 2)

        # Calculate prep & pickup time
        prep_calc = self.calculate_smart_prep_time(food_ids)
        order_num = f"ORD-{datetime.datetime.now().strftime('%m%d')}-{random_str(4).upper()}"

        # Payment Status
        payment_status = 'PAID' if payment_method in ['upi', 'card', 'wallet'] else 'PENDING'

        # Insert Order
        order_id = execute_db("""
            INSERT INTO orders (
                order_number, student_id, total_amount, discount_amount, tax_amount,
                final_amount, payment_method, payment_status, order_status,
                estimated_prep_time, pickup_time, special_instructions, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            order_num, student_id, subtotal, discount_amount, tax_amount,
            final_amount, payment_method, payment_status, 'PLACED',
            prep_calc['prep_minutes'], prep_calc['pickup_time'].strftime('%Y-%m-%d %H:%M:%S'),
            special_instructions
        ))

        # Insert Order Items & Update stock / total orders
        for it in cart_items:
            fid = it['id']
            qty = it['quantity']
            food = query_db("SELECT * FROM food_items WHERE id = %s", (fid,), one=True)
            unit_price = float(food['price'])
            item_subtotal = round(unit_price * qty, 2)

            execute_db("""
                INSERT INTO order_items (order_id, food_id, quantity, unit_price, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, fid, qty, unit_price, item_subtotal))

            # Increment item total orders & decrement stock
            execute_db("""
                UPDATE food_items 
                SET total_orders = total_orders + %s, stock_quantity = MAX(0, stock_quantity - %s)
                WHERE id = %s
            """, (qty, qty, fid))

        # Record Payment
        tx_ref = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        execute_db("""
            INSERT INTO payments (order_id, student_id, amount, payment_method, payment_status, transaction_ref, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (order_id, student_id, final_amount, payment_method, payment_status, tx_ref))

        # Create Student Notification
        execute_db("""
            INSERT INTO notifications (user_id, title, message, type, link, created_at)
            VALUES (%s, %s, %s, 'order', %s, NOW())
        """, (
            student_id,
            f"Order Placed #{order_num}",
            f"Your order #{order_num} for ₹{final_amount} is placed! Estimated ready at {prep_calc['pickup_time_str']}.",
            f"/student/order-track/{order_id}"
        ))

        return {
            "order_id": order_id,
            "order_number": order_num,
            "final_amount": final_amount,
            "prep_calc": prep_calc,
            "payment_status": payment_status
        }

    def update_order_status(self, order_id: int, new_status: str) -> bool:
        """
        Transitions order status (PLACED -> ACCEPTED -> PREPARING -> READY -> COMPLETED / CANCELLED)
        and sends contextual notifications to student.
        """
        valid_statuses = ['PLACED', 'ACCEPTED', 'PREPARING', 'READY', 'COMPLETED', 'CANCELLED']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid order status: {new_status}")

        order = query_db("SELECT * FROM orders WHERE id = %s", (order_id,), one=True)
        if not order:
            return False

        execute_db("""
            UPDATE orders SET order_status = %s, updated_at = NOW() WHERE id = %s
        """, (new_status, order_id))

        # If marking ready, also update payment if cash on pickup
        if new_status == 'COMPLETED' and order['payment_method'] == 'cash_on_pickup':
            execute_db("UPDATE orders SET payment_status = 'PAID' WHERE id = %s", (order_id,))
            execute_db("UPDATE payments SET payment_status = 'SUCCESS' WHERE order_id = %s", (order_id,))

        # Send push notification to student
        messages = {
            'ACCEPTED': f"Chef has accepted your order #{order['order_number']}. Preparing soon!",
            'PREPARING': f"Order #{order['order_number']} is now sizzling on the stove!",
            'READY': f"🔔 ORDER READY! Please collect #{order['order_number']} at the Canteen Counter.",
            'COMPLETED': f"Enjoy your meal! Order #{order['order_number']} completed. Please leave a review.",
            'CANCELLED': f"Order #{order['order_number']} was cancelled."
        }

        if new_status in messages:
            execute_db("""
                INSERT INTO notifications (user_id, title, message, type, link, created_at)
                VALUES (%s, %s, %s, 'order', %s, NOW())
            """, (
                order['student_id'],
                f"Order {new_status.title()} #{order['order_number']}",
                messages[new_status],
                f"/student/order-track/{order_id}"
            ))

        return True

def random_str(length=4):
    import random, string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Singleton instance
order_service = OrderService()

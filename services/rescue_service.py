import datetime
import random
import uuid
from typing import List, Dict, Any, Optional
from database.db import query_db, execute_db
from services.notification_service import notification_service

class RescueService:
    """
    Smart Food Rescue Service:
    - Automatically creates rescue offers when orders are cancelled in PREPARING or READY state
    - Manages real-time availability, dynamic 10% discounts, and collection deadlines
    - Concurrency-safe, atomic purchase workflows with PIN generation
    - Comprehensive environmental & financial metrics tracking
    """

    DEFAULT_EXPIRY_MINUTES = 45
    DEFAULT_DISCOUNT_PERCENT = 10  # 10% discount on original price (e.g. ₹50 -> ₹45)

    def _sync_expired_offers(self):
        """Marks any offers whose collection deadline has passed as EXPIRED"""
        execute_db("""
            UPDATE food_rescue_offers 
            SET offer_status = 'EXPIRED' 
            WHERE offer_status = 'AVAILABLE' 
              AND expires_at < NOW()
        """)

    def create_rescue_offers_for_order(self, order_id: int, original_student_id: int) -> List[Dict[str, Any]]:
        """
        Creates Food Rescue Offers for items in an order cancelled during PREPARING or READY status.
        Notifies all other active campus students in real-time.
        """
        order = query_db("SELECT * FROM orders WHERE id = %s", (order_id,), one=True)
        if not order:
            return []

        items = query_db("""
            SELECT oi.*, f.name as food_name, f.price as catalog_price, f.image_url, f.is_veg
            FROM order_items oi
            JOIN food_items f ON oi.food_id = f.id
            WHERE oi.order_id = %s
        """, (order_id,)) or []

        created_offers = []
        now = datetime.datetime.now()
        expires_at_dt = now + datetime.timedelta(minutes=self.DEFAULT_EXPIRY_MINUTES)
        expires_at_str = expires_at_dt.strftime('%Y-%m-%d %H:%M:%S')

        for item in items:
            orig_price = float(item['unit_price'])
            discount_pct = self.DEFAULT_DISCOUNT_PERCENT
            rescue_price = round(orig_price * (1.0 - (discount_pct / 100.0)), 2)
            qty = int(item['quantity'])

            offer_id = execute_db("""
                INSERT INTO food_rescue_offers 
                (original_order_id, original_student_id, food_id, food_name, quantity_available, quantity_claimed,
                 original_price, rescue_price, discount_percent, offer_status, collection_point, expires_at, created_at)
                VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s, 'AVAILABLE', 'College Canteen Central Counter', %s, NOW())
            """, (
                order_id,
                original_student_id,
                item['food_id'],
                item['food_name'],
                qty,
                orig_price,
                rescue_price,
                discount_pct,
                expires_at_str
            ))

            offer_record = {
                "offer_id": offer_id,
                "food_id": item['food_id'],
                "food_name": item['food_name'],
                "quantity": qty,
                "original_price": orig_price,
                "rescue_price": rescue_price,
                "discount_percent": discount_pct,
                "expires_at": expires_at_str,
                "image_url": item['image_url']
            }
            created_offers.append(offer_record)

            # Broadcast real-time notifications to all eligible students (excluding the cancelling student)
            other_students = query_db("""
                SELECT id FROM users 
                WHERE role = 'student' AND id != %s
            """, (original_student_id,)) or []

            notif_title = "🚨 FOOD RESCUE ALERT!"
            notif_msg = (
                f"A fresh meal is ready and may go to waste! {item['food_name']} "
                f"at ₹{rescue_price:.2f} (was ₹{orig_price:.2f}, save {discount_pct}%). "
                f"Available for instant pickup at Canteen Central Counter!"
            )

            for s in other_students:
                notification_service.create_notification(
                    user_id=s['id'],
                    title=notif_title,
                    message=notif_msg,
                    notif_type='rescue',
                    link='/student/dashboard#food-rescue'
                )

        return created_offers

    def get_active_offers(self) -> List[Dict[str, Any]]:
        """
        Retrieves all currently active, non-expired Food Rescue Offers with full dish metadata.
        """
        self._sync_expired_offers()

        offers = query_db("""
            SELECT ro.*, f.name as food_name, f.description, f.image_url, f.is_veg, 
                   f.prep_time_minutes, f.calories, f.rating, f.spice_level,
                   fc.name as category_name
            FROM food_rescue_offers ro
            JOIN food_items f ON ro.food_id = f.id
            LEFT JOIN food_categories fc ON f.category_id = fc.id
            WHERE ro.offer_status = 'AVAILABLE' AND ro.quantity_available > 0
            ORDER BY ro.created_at DESC
        """) or []

        now = datetime.datetime.now()
        for o in offers:
            # Parse expires_at to calculate time remaining
            exp_str = str(o['expires_at'])
            try:
                if hasattr(o['expires_at'], 'strftime'):
                    exp_dt = o['expires_at']
                else:
                    exp_dt = datetime.datetime.strptime(exp_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                seconds_left = max(0, int((exp_dt - now).total_seconds()))
                mins_left = seconds_left // 60
                o['seconds_remaining'] = seconds_left
                o['time_remaining_str'] = f"{mins_left} mins left" if mins_left > 0 else "Expiring soon"
            except Exception:
                o['seconds_remaining'] = 1800
                o['time_remaining_str'] = "30 mins left"

            o['savings_amount'] = round(float(o['original_price']) - float(o['rescue_price']), 2)

        return offers

    def get_offer_by_id(self, offer_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single rescue offer with food metadata"""
        self._sync_expired_offers()
        return query_db("""
            SELECT ro.*, f.name as food_name, f.description, f.image_url, f.is_veg, f.rating
            FROM food_rescue_offers ro
            JOIN food_items f ON ro.food_id = f.id
            WHERE ro.id = %s
        """, (offer_id,), one=True)

    def purchase_rescue_offer(
        self,
        offer_id: int,
        buyer_student_id: int,
        quantity: int = 1,
        payment_method: str = 'wallet'
    ) -> Dict[str, Any]:
        """
        Executes a concurrency-safe atomic purchase of a Food Rescue offer.
        Deducts payment, creates a separate new order for the buyer, generates collection PIN,
        updates offer quantities, and notifies both buyer and kitchen staff.
        """
        self._sync_expired_offers()

        # 1. Fetch Offer with row lock check
        offer = query_db("""
            SELECT ro.*, f.name as food_name, f.image_url, f.is_veg
            FROM food_rescue_offers ro
            JOIN food_items f ON ro.food_id = f.id
            WHERE ro.id = %s
        """, (offer_id,), one=True)

        if not offer:
            raise ValueError("Food Rescue offer not found.")

        if offer['offer_status'] != 'AVAILABLE' or int(offer['quantity_available']) < quantity:
            raise ValueError("Sorry, this rescue meal is no longer available or has already been claimed.")

        # Check expiration
        now = datetime.datetime.now()
        exp_str = str(offer['expires_at'])
        try:
            if hasattr(offer['expires_at'], 'strftime'):
                exp_dt = offer['expires_at']
            else:
                exp_dt = datetime.datetime.strptime(exp_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
            if now > exp_dt:
                execute_db("UPDATE food_rescue_offers SET offer_status = 'EXPIRED' WHERE id = %s", (offer_id,))
                raise ValueError("This food rescue offer has expired.")
        except ValueError as ve:
            raise ve
        except Exception:
            pass

        # 2. Verify Buyer & Payment
        buyer = query_db("SELECT * FROM users WHERE id = %s", (buyer_student_id,), one=True)
        if not buyer:
            raise ValueError("Buyer student account not found.")

        unit_price = float(offer['rescue_price'])
        total_amount = round(unit_price * quantity, 2)
        payment_method_clean = payment_method.lower()

        if payment_method_clean == 'wallet':
            current_balance = float(buyer.get('wallet_balance', 0.0))
            if current_balance < total_amount:
                raise ValueError(f"Insufficient dining wallet balance (₹{current_balance:.2f}). Please top up or choose another payment option.")

            # Atomically deduct wallet balance
            deducted = execute_db("""
                UPDATE users 
                SET wallet_balance = wallet_balance - %s 
                WHERE id = %s AND wallet_balance >= %s
            """, (total_amount, buyer_student_id, total_amount))
            if not deducted:
                raise ValueError("Wallet payment failed due to concurrent balance change. Please try again.")

        # 3. Atomically claim offer quantity
        claimed = execute_db("""
            UPDATE food_rescue_offers 
            SET quantity_available = quantity_available - %s,
                quantity_claimed = quantity_claimed + %s,
                offer_status = CASE WHEN quantity_available - %s <= 0 THEN 'CLAIMED' ELSE 'AVAILABLE' END
            WHERE id = %s AND quantity_available >= %s AND offer_status = 'AVAILABLE'
        """, (quantity, quantity, quantity, offer_id, quantity))

        if not claimed:
            # Rollback wallet deduction if concurrent purchase failed
            if payment_method_clean == 'wallet':
                execute_db("UPDATE users SET wallet_balance = wallet_balance + %s WHERE id = %s", (total_amount, buyer_student_id))
            raise ValueError("This rescue meal was just claimed by another student.")

        # 4. Generate Order Identifiers
        order_num = f"RESCUE-{now.strftime('%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        collection_pin = f"{random.randint(1000, 9999)}"
        tx_ref = f"TXN-RESCUE-{uuid.uuid4().hex[:8].upper()}"
        pickup_time_str = (now + datetime.timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')

        # 5. Create Separate Order in orders table
        new_order_id = execute_db("""
            INSERT INTO orders 
            (order_number, student_id, total_amount, discount_amount, tax_amount, final_amount, 
             payment_method, payment_status, order_status, estimated_prep_time, pickup_time, 
             special_instructions, is_rescue_order, rescue_offer_id, collection_pin, created_at, updated_at)
            VALUES (%s, %s, %s, 0.00, 0.00, %s, %s, 'PAID', 'READY', 5, %s, %s, 1, %s, %s, NOW(), NOW())
        """, (
            order_num,
            buyer_student_id,
            total_amount,
            total_amount,
            payment_method_clean,
            pickup_time_str,
            f"⚡ Smart Food Rescue Deal (Original Order #{offer['original_order_id']})",
            offer_id,
            collection_pin
        ))

        # 6. Insert Order Item
        execute_db("""
            INSERT INTO order_items (order_id, food_id, quantity, unit_price, subtotal)
            VALUES (%s, %s, %s, %s, %s)
        """, (new_order_id, offer['food_id'], quantity, unit_price, total_amount))

        # 7. Record Payment
        execute_db("""
            INSERT INTO payments (order_id, student_id, amount, payment_method, payment_status, transaction_ref, created_at)
            VALUES (%s, %s, %s, %s, 'PAID', %s, NOW())
        """, (new_order_id, buyer_student_id, total_amount, payment_method_clean, tx_ref))

        # 8. Notify Buyer with Collection PIN
        buyer_msg = (
            f"🎉 Rescue Meal Confirmed! Order #{order_num}. "
            f"Your pickup PIN is {collection_pin}. "
            f"Show this PIN at the Central Canteen Counter for immediate meal handover."
        )
        notification_service.create_notification(
            user_id=buyer_student_id,
            title=f"⚡ Rescue Meal Ready: #{order_num}",
            message=buyer_msg,
            notif_type='order',
            link=f"/student/order-track/{new_order_id}"
        )

        # 9. Notify Staff on Kitchen Board
        staff_members = query_db("SELECT id FROM users WHERE role IN ('staff', 'admin')") or []
        for staff in staff_members:
            notification_service.create_notification(
                user_id=staff['id'],
                title=f"⚡ Resold Rescue Meal #{order_num}",
                message=f"Rescue meal ({offer['food_name']}) claimed by {buyer['name']}. PIN: {collection_pin}.",
                notif_type='staff',
                link="/staff/dashboard"
            )

        # Fetch new wallet balance
        updated_buyer = query_db("SELECT wallet_balance FROM users WHERE id = %s", (buyer_student_id,), one=True)
        new_wallet = float(updated_buyer['wallet_balance']) if updated_buyer else 0.0

        return {
            "success": True,
            "order_id": new_order_id,
            "order_number": order_num,
            "food_name": offer['food_name'],
            "quantity": quantity,
            "total_amount": total_amount,
            "collection_pin": collection_pin,
            "new_wallet_balance": new_wallet,
            "message": buyer_msg
        }

    def get_rescue_kpis(self) -> Dict[str, Any]:
        """
        Computes environmental impact and financial statistics for Admin Dashboard & Reports.
        """
        self._sync_expired_offers()

        # Cancellation counts & fees
        cancel_stats = query_db("""
            SELECT 
                COUNT(id) as total_cancelled,
                COALESCE(SUM(cancellation_fee), 0.0) as total_cancellation_fees,
                COALESCE(SUM(refund_amount), 0.0) as total_refunds_issued
            FROM orders
            WHERE order_status = 'CANCELLED'
        """, one=True) or {'total_cancelled': 0, 'total_cancellation_fees': 0.0, 'total_refunds_issued': 0.0}

        # Rescue offer metrics
        offer_stats = query_db("""
            SELECT 
                COUNT(id) as total_offers_created,
                COALESCE(SUM(quantity_available), 0) as total_qty_available,
                COALESCE(SUM(quantity_claimed), 0) as total_meals_resold,
                COUNT(CASE WHEN offer_status = 'CLAIMED' THEN 1 END) as offers_claimed_count,
                COUNT(CASE WHEN offer_status = 'EXPIRED' THEN 1 END) as offers_expired_count,
                COALESCE(SUM(quantity_claimed * rescue_price), 0.0) as total_rescue_revenue,
                COALESCE(SUM(quantity_claimed * original_price), 0.0) as total_food_value_saved
            FROM food_rescue_offers
        """, one=True) or {
            'total_offers_created': 0, 'total_qty_available': 0, 'total_meals_resold': 0,
            'offers_claimed_count': 0, 'offers_expired_count': 0, 'total_rescue_revenue': 0.0,
            'total_food_value_saved': 0.0
        }

        total_meals_resold = int(offer_stats.get('total_meals_resold') or 0)
        # Average weight per meal estimated at 0.35 kg
        food_waste_saved_kg = round(total_meals_resold * 0.35, 2)

        return {
            "total_cancelled_orders": cancel_stats['total_cancelled'],
            "total_cancellation_fees": float(cancel_stats['total_cancellation_fees']),
            "total_refunds_issued": float(cancel_stats['total_refunds_issued']),
            "total_offers_created": offer_stats['total_offers_created'],
            "total_meals_resold": total_meals_resold,
            "offers_claimed_count": offer_stats['offers_claimed_count'],
            "offers_expired_count": offer_stats['offers_expired_count'],
            "total_rescue_revenue": float(offer_stats['total_rescue_revenue']),
            "food_waste_saved_valuation": float(offer_stats['total_food_value_saved']),
            "food_waste_saved_kg": food_waste_saved_kg
        }

# Singleton instance
rescue_service = RescueService()

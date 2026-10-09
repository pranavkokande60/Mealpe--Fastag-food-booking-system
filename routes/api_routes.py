import datetime
from flask import Blueprint, request, jsonify, session
from database.db import query_db, execute_db
from ai.chatbot import canteen_bot
from services.order_service import order_service
from services.seat_service import seat_service
from services.notification_service import notification_service
from config import Config

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/chat', methods=['POST'])
def chat():
    """AI Chatbot message handler"""
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({"reply": "Please ask me something about the menu, orders, or canteen seats!"})

    user_id = session.get('user_id')
    response_data = canteen_bot.process_message(message, user_id=user_id)
    return jsonify(response_data)

@api_bp.route('/cart/prep-time', methods=['POST'])
def get_cart_prep_time():
    """Calculates live estimated prep time for items in cart"""
    data = request.get_json() or {}
    item_ids = data.get('item_ids', [])
    prep_info = order_service.calculate_smart_prep_time(item_ids)
    return jsonify({
        "prep_minutes": prep_info['prep_minutes'],
        "pickup_time_str": prep_info['pickup_time_str'],
        "active_queue": prep_info['active_queue_count']
    })

@api_bp.route('/cart/validate-coupon', methods=['POST'])
def validate_coupon():
    """Validates coupon and calculates discount"""
    data = request.get_json() or {}
    code = data.get('code', '').strip().upper()
    subtotal = float(data.get('subtotal', 0))

    coupon = query_db("SELECT * FROM coupons WHERE code = %s AND is_active = 1", (code,), one=True)
    if not coupon:
        return jsonify({"valid": False, "message": "Invalid or expired coupon code."})

    min_order = float(coupon['min_order_amount'])
    if subtotal < min_order:
        return jsonify({"valid": False, "message": f"Coupon requires minimum order of ₹{int(min_order)}."})

    if float(coupon['discount_percent']) > 0:
        discount = (subtotal * float(coupon['discount_percent'])) / 100.0
        discount = min(discount, float(coupon['max_discount']))
    else:
        discount = min(float(coupon['discount_amount']), subtotal)

    return jsonify({
        "valid": True,
        "code": code,
        "discount_amount": round(discount, 2),
        "message": f"Coupon applied! You saved ₹{int(discount)}."
    })

@api_bp.route('/order/status/<int:order_id>')
def get_order_status(order_id):
    """Returns real-time status of an order for live tracking polling"""
    order = query_db("SELECT id, order_number, order_status, estimated_prep_time, pickup_time, updated_at FROM orders WHERE id = %s", (order_id,), one=True)
    if not order:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "order_id": order['id'],
        "order_number": order['order_number'],
        "status": order['order_status'],
        "prep_time": order['estimated_prep_time'],
        "pickup_time": order['pickup_time']
    })

@api_bp.route('/order/<int:order_id>/cancel', methods=['POST'])
def cancel_order_api(order_id):
    """Cancels order via API if student owns it and order is in PLACED/ACCEPTED state"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "Authentication required"}), 401

    data = request.get_json(silent=True) or {}
    reason = data.get('reason') or request.form.get('reason')
    role = session.get('user_role', 'student')

    try:
        res = order_service.cancel_order(order_id=order_id, user_id=user_id, role=role, reason=reason)
        if res.get('refund_amount', 0) > 0:
            session['wallet_balance'] = res['new_wallet_balance']
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@api_bp.route('/seats/availability')
def check_seat_availability():
    """Returns 2D seat map data for selected date and slot"""
    booking_date = request.args.get('date', datetime.date.today().strftime('%Y-%m-%d'))
    time_slot = request.args.get('slot', '12:00 - 12:30')
    user_id = session.get('user_id')

    layout = seat_service.get_table_layout_with_status(booking_date, time_slot, current_user_id=user_id)
    return jsonify(layout)

@api_bp.route('/notifications/unread-count')
def unread_notifications():
    """Returns unread notification count for active student"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"count": 0, "notifications": []})

    count = notification_service.get_unread_count(user_id)
    notifs = notification_service.get_user_notifications(user_id, limit=5)
    return jsonify({"count": count, "notifications": notifs})

@api_bp.route('/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    user_id = session.get('user_id')
    if user_id:
        notification_service.mark_all_read(user_id)
    return jsonify({"success": True})

@api_bp.route('/kitchen/live-orders')
def kitchen_live_orders():
    """Returns live JSON list of active kitchen orders for KDS polling"""
    orders = query_db("""
        SELECT o.id, o.order_number, o.order_status, o.created_at, o.estimated_prep_time,
               o.special_instructions, o.is_rescue_order, o.collection_pin, u.name as student_name,
               GROUP_CONCAT(CONCAT(oi.quantity, 'x ', f.name) SEPARATOR ', ') as items_summary
        FROM orders o
        JOIN users u ON o.student_id = u.id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN food_items f ON oi.food_id = f.id
        WHERE o.order_status IN ('PLACED', 'ACCEPTED', 'PREPARING', 'READY')
        GROUP BY o.id
        ORDER BY o.created_at ASC
    """) or []
    return jsonify({"orders": orders})

@api_bp.route('/rescue/active-offers')
def get_active_rescue_offers():
    """Returns real-time list of active, non-expired Food Rescue deals for student dashboard polling"""
    from services.rescue_service import rescue_service
    offers = rescue_service.get_active_offers()
    return jsonify({
        "success": True,
        "count": len(offers),
        "offers": offers
    })

@api_bp.route('/rescue/buy', methods=['POST'])
def purchase_rescue_offer_api():
    """API endpoint to atomically purchase a Food Rescue meal"""
    from services.rescue_service import rescue_service

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "Please log in to purchase rescue meals."}), 401

    data = request.get_json() or {}
    offer_id = data.get('offer_id') or request.form.get('offer_id', type=int)
    quantity = int(data.get('quantity') or request.form.get('quantity', 1) or 1)
    payment_method = (data.get('payment_method') or request.form.get('payment_method', 'wallet')).lower()

    if not offer_id:
        return jsonify({"success": False, "error": "Offer ID is required."}), 400

    try:
        res = rescue_service.purchase_rescue_offer(
            offer_id=int(offer_id),
            buyer_student_id=user_id,
            quantity=quantity,
            payment_method=payment_method
        )
        session['wallet_balance'] = res['new_wallet_balance']
        return jsonify(res)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@api_bp.route('/rescue/stats')
def get_rescue_stats_api():
    """Returns environmental impact and financial statistics for Food Rescue"""
    from services.rescue_service import rescue_service
    stats = rescue_service.get_rescue_kpis()
    return jsonify({"success": True, "stats": stats})

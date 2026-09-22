import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file, g
from database.db import query_db, execute_db
from routes.auth_routes import login_required, role_required
from ai.recommendation import recommendation_engine
from ai.crowd_prediction import crowd_predictor
from ai.feedback_analysis import feedback_analyzer
from services.order_service import order_service
from services.seat_service import seat_service
from services.pdf_service import pdf_service
from services.notification_service import notification_service
from config import Config

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    
    # 1. Categories
    categories = query_db("SELECT * FROM food_categories ORDER BY display_order ASC") or []
    
    # 2. AI Recommended Items
    ai_picks = recommendation_engine.get_recommendations_for_user(user_id, limit=6)
    
    # 3. Trending / Bestsellers
    popular_items = recommendation_engine.get_trending_items(limit=6)
    
    # 4. Active Orders
    active_orders = query_db("""
        SELECT o.*, GROUP_CONCAT(CONCAT(oi.quantity, 'x ', f.name) SEPARATOR ', ') as item_summary
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN food_items f ON oi.food_id = f.id
        WHERE o.student_id = %s AND o.order_status IN ('PLACED', 'ACCEPTED', 'PREPARING', 'READY')
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """, (user_id,)) or []
    
    # 5. Upcoming Seat Bookings
    upcoming_seats = query_db("""
        SELECT b.*, t.table_number, t.section
        FROM seat_bookings b
        JOIN seat_tables t ON b.table_id = t.id
        WHERE b.student_id = %s AND b.booking_date >= CURDATE() AND b.status = 'CONFIRMED'
        ORDER BY b.booking_date ASC, b.time_slot ASC
    """, (user_id,)) or []
    
    # 6. Current Crowd Status
    crowd_status = crowd_predictor.get_current_crowd_status()
    
    return render_template(
        'student/dashboard.html',
        user=user,
        categories=categories,
        ai_picks=ai_picks,
        popular_items=popular_items,
        active_orders=active_orders,
        upcoming_seats=upcoming_seats,
        crowd_status=crowd_status,
        now=datetime.datetime.now()
    )

@student_bp.route('/menu')
def menu():
    # Filtering parameters
    category_id = request.args.get('category', type=int)
    search_q = request.args.get('q', '').strip()
    veg_only = request.args.get('veg', type=int)
    sort_by = request.args.get('sort', 'popular') # popular, price_asc, price_desc, rating, prep_time
    max_price = request.args.get('max_price', type=float)

    query = "SELECT * FROM food_items WHERE is_available = 1"
    params = []

    if category_id:
        query += " AND category_id = %s"
        params.append(category_id)

    if search_q:
        query += " AND (name LIKE %s OR ingredients LIKE %s OR description LIKE %s)"
        params.extend([f"%{search_q}%", f"%{search_q}%", f"%{search_q}%"])

    if veg_only:
        query += " AND is_veg = 1"

    if max_price:
        query += " AND price <= %s"
        params.append(max_price)

    # Sorting
    if sort_by == 'price_asc':
        query += " ORDER BY price ASC"
    elif sort_by == 'price_desc':
        query += " ORDER BY price DESC"
    elif sort_by == 'rating':
        query += " ORDER BY rating DESC"
    elif sort_by == 'prep_time':
        query += " ORDER BY prep_time_minutes ASC"
    else: # popular
        query += " ORDER BY total_orders DESC, rating DESC"

    foods = query_db(query, tuple(params)) or []
    categories = query_db("SELECT * FROM food_categories ORDER BY display_order ASC") or []

    # Selected category object
    current_category = None
    if category_id:
        current_category = query_db("SELECT * FROM food_categories WHERE id = %s", (category_id,), one=True)

    return render_template(
        'student/menu.html',
        foods=foods,
        categories=categories,
        current_category=current_category,
        selected_category_id=category_id,
        search_q=search_q,
        veg_only=veg_only,
        sort_by=sort_by,
        max_price=max_price
    )

@student_bp.route('/cart')
def cart():
    coupons = query_db("SELECT * FROM coupons WHERE is_active = 1") or []
    return render_template('student/cart.html', coupons=coupons)

@student_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    user = query_db("SELECT * FROM users WHERE id = %s", (session['user_id'],), one=True)

    if request.method == 'POST':
        import json
        cart_data_raw = request.form.get('cart_data', '[]')
        payment_method = request.form.get('payment_method', 'cash_on_pickup')
        coupon_code = request.form.get('coupon_code', '').strip().upper()
        special_instructions = request.form.get('special_instructions', '').strip()

        try:
            cart_items = json.loads(cart_data_raw)
        except Exception:
            flash('Invalid cart contents.', 'danger')
            return redirect(url_for('student.cart'))

        if not cart_items:
            flash('Your cart is empty. Please add delicious items first!', 'warning')
            return redirect(url_for('student.menu'))

        try:
            res = order_service.place_order(
                student_id=session['user_id'],
                cart_items=cart_items,
                payment_method=payment_method,
                coupon_code=coupon_code if coupon_code else None,
                special_instructions=special_instructions if special_instructions else None
            )
            flash(f"Order #{res['order_number']} placed successfully!", 'success')
            return redirect(url_for('student.order_track', order_id=res['order_id']))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('student.cart'))

    return render_template('student/checkout.html', user=user)

@student_bp.route('/order-track/<int:order_id>')
@login_required
def order_track(order_id):
    order = query_db("""
        SELECT o.*, u.name as student_name, u.phone as student_phone
        FROM orders o
        JOIN users u ON o.student_id = u.id
        WHERE o.id = %s
    """, (order_id,), one=True)

    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('student.dashboard'))

    # Security check
    if order['student_id'] != session['user_id'] and session.get('user_role') not in ['admin', 'staff']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('student.dashboard'))

    items = query_db("""
        SELECT oi.*, f.name as food_name, f.image_url, f.is_veg
        FROM order_items oi
        JOIN food_items f ON oi.food_id = f.id
        WHERE oi.order_id = %s
    """, (order_id,)) or []

    # Map status to progress index
    status_steps = ['PLACED', 'ACCEPTED', 'PREPARING', 'READY', 'COMPLETED']
    current_step_idx = status_steps.index(order['order_status']) if order['order_status'] in status_steps else 0

    return render_template(
        'student/order_track.html',
        order=order,
        items=items,
        status_steps=status_steps,
        current_step_idx=current_step_idx
    )


@student_bp.route('/order/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    reason = request.form.get('reason', '').strip()
    try:
        res = order_service.cancel_order(
            order_id=order_id,
            user_id=session['user_id'],
            role=session.get('user_role', 'student'),
            reason=reason if reason else None
        )
        if res.get('refund_amount', 0) > 0:
            session['wallet_balance'] = res['new_wallet_balance']
            flash(f"Order #{res['order_number']} has been cancelled. ₹{res['refund_amount']:.2f} refunded to your dining wallet!", 'success')
        else:
            flash(f"Order #{res['order_number']} has been cancelled successfully.", 'info')
    except Exception as e:
        flash(str(e), 'danger')

    redirect_to = request.form.get('redirect_to')
    if redirect_to == 'history':
        return redirect(url_for('student.order_history'))
    return redirect(url_for('student.order_track', order_id=order_id))

@student_bp.route('/receipt/<int:order_id>')
@login_required
def download_receipt(order_id):
    order = query_db("SELECT * FROM orders WHERE id = %s", (order_id,), one=True)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('student.dashboard'))

    if order['student_id'] != session['user_id'] and session.get('user_role') not in ['admin', 'staff']:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('student.dashboard'))

    pdf_buffer = pdf_service.generate_order_receipt_pdf(order_id)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"SmartCanteen_Receipt_{order['order_number']}.pdf"
    )

@student_bp.route('/order-history')
@login_required
def order_history():
    user_id = session['user_id']
    orders = query_db("""
        SELECT o.*, GROUP_CONCAT(CONCAT(oi.quantity, 'x ', f.name) SEPARATOR ', ') as item_summary
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN food_items f ON oi.food_id = f.id
        WHERE o.student_id = %s
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """, (user_id,)) or []

    return render_template('student/order_history.html', orders=orders)

@student_bp.route('/seat-booking', methods=['GET', 'POST'])
@login_required
def seat_booking():
    user_id = session['user_id']
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    
    selected_date = request.args.get('date', today_str)
    selected_slot = request.args.get('slot', '12:00 - 12:30')

    if request.method == 'POST':
        table_id = request.form.get('table_id', type=int)
        booking_date = request.form.get('booking_date', today_str)
        time_slot = request.form.get('time_slot', '12:00 - 12:30')
        guests_count = request.form.get('guests_count', type=int, default=1)

        try:
            res = seat_service.book_seat(user_id, table_id, booking_date, time_slot, guests_count)
            flash(f"Seat Confirmed! Table {res['table_number']} reserved for {time_slot}.", 'success')
            return redirect(url_for('student.seat_booking', date=booking_date, slot=time_slot))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('student.seat_booking', date=booking_date, slot=time_slot))

    # Fetch 2D layout with status
    layout_data = seat_service.get_table_layout_with_status(selected_date, selected_slot, current_user_id=user_id)

    # Student active bookings
    my_bookings = query_db("""
        SELECT b.*, t.table_number, t.section, t.capacity
        FROM seat_bookings b
        JOIN seat_tables t ON b.table_id = t.id
        WHERE b.student_id = %s AND b.status = 'CONFIRMED'
        ORDER BY b.booking_date DESC, b.time_slot ASC
    """, (user_id,)) or []

    return render_template(
        'student/seat_booking.html',
        layout=layout_data,
        selected_date=selected_date,
        selected_slot=selected_slot,
        my_bookings=my_bookings,
        today=today_str
    )

@student_bp.route('/cancel-seat/<int:booking_id>', methods=['POST'])
@login_required
def cancel_seat(booking_id):
    try:
        res = seat_service.cancel_booking(booking_id, session['user_id'], is_admin=(session.get('user_role') == 'admin'))
        flash(f"Table {res['table_number']} reservation on {res['booking_date']} at {res['time_slot']} has been cancelled.", 'info')
    except Exception as e:
        flash(str(e), 'danger')

    redirect_to = request.form.get('redirect_to')
    if redirect_to == 'dashboard':
        return redirect(url_for('student.dashboard'))
    return redirect(url_for('student.seat_booking'))

@student_bp.route('/insights')
@login_required
def insights():
    user_id = session['user_id']
    
    # Aggregated student metrics
    stats = query_db("""
        SELECT 
            COUNT(id) as total_orders,
            COALESCE(SUM(final_amount), 0.0) as total_spent,
            COALESCE(AVG(final_amount), 0.0) as avg_order_value
        FROM orders
        WHERE student_id = %s AND order_status != 'CANCELLED'
    """, (user_id,), one=True)

    # Top food item
    fav_food = query_db("""
        SELECT f.name, f.image_url, COUNT(oi.id) as freq
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN food_items f ON oi.food_id = f.id
        WHERE o.student_id = %s AND o.order_status != 'CANCELLED'
        GROUP BY f.id
        ORDER BY freq DESC LIMIT 1
    """, (user_id,), one=True)

    # Category breakdown
    cat_breakdown = query_db("""
        SELECT c.name as category, COUNT(oi.id) as count, SUM(oi.subtotal) as spent
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN food_items f ON oi.food_id = f.id
        JOIN food_categories c ON f.category_id = c.id
        WHERE o.student_id = %s AND o.order_status != 'CANCELLED'
        GROUP BY c.id
        ORDER BY count DESC
    """, (user_id,)) or []

    # Monthly spending
    monthly_spending = query_db("""
        SELECT strftime('%Y-%m', created_at) as month_label, SUM(final_amount) as total
        FROM orders
        WHERE student_id = %s AND order_status != 'CANCELLED'
        GROUP BY month_label
        ORDER BY month_label DESC LIMIT 6
    """, (user_id,)) or []

    return render_template(
        'student/insights.html',
        stats=stats,
        fav_food=fav_food,
        cat_breakdown=cat_breakdown,
        monthly_spending=monthly_spending
    )

@student_bp.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    user_id = session['user_id']

    if request.method == 'POST':
        order_id = request.form.get('order_id', type=int)
        rating = request.form.get('rating', type=int, default=5)
        comment = request.form.get('comment', '').strip()

        if not comment:
            flash('Please write a brief feedback comment.', 'warning')
            return redirect(url_for('student.feedback'))

        # NLP Aspect & Sentiment Analysis
        aspect, sentiment = feedback_analyzer.analyze_text(comment, rating)

        execute_db("""
            INSERT INTO feedback (student_id, order_id, rating, aspect, sentiment, comment, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (user_id, order_id if order_id else None, rating, aspect, sentiment, comment))

        flash('Thank you for your valuable feedback! Our kitchen team appreciates it.', 'success')
        return redirect(url_for('student.feedback'))

    # Query student recent orders to link feedback
    recent_orders = query_db("""
        SELECT id, order_number, created_at FROM orders 
        WHERE student_id = %s ORDER BY created_at DESC LIMIT 5
    """, (user_id,)) or []

    # Past feedback given
    my_feedbacks = query_db("""
        SELECT * FROM feedback WHERE student_id = %s ORDER BY created_at DESC
    """, (user_id,)) or []

    return render_template('student/feedback.html', recent_orders=recent_orders, my_feedbacks=my_feedbacks)

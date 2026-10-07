import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from database.db import query_db, execute_db
from routes.auth_routes import login_required, role_required
from services.order_service import order_service
from ai.demand_prediction import demand_predictor

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/dashboard')
@role_required(['staff', 'admin'])
def dashboard():
    # Fetch active kitchen orders grouped by status
    orders = query_db("""
        SELECT o.*, u.name as student_name, u.phone as student_phone,
               GROUP_CONCAT(CONCAT(oi.quantity, 'x ', f.name) SEPARATOR '||') as items_raw
        FROM orders o
        JOIN users u ON o.student_id = u.id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN food_items f ON oi.food_id = f.id
        WHERE o.order_status IN ('PLACED', 'ACCEPTED', 'PREPARING', 'READY')
        GROUP BY o.id, u.name, u.phone
        ORDER BY o.created_at ASC
    """) or []

    # Parse items list
    for o in orders:
        o['items_list'] = o['items_raw'].split('||') if o['items_raw'] else []

    # Status counts for kitchen scoreboard
    placed_count = sum(1 for o in orders if o['order_status'] == 'PLACED')
    prep_count = sum(1 for o in orders if o['order_status'] in ['ACCEPTED', 'PREPARING'])
    ready_count = sum(1 for o in orders if o['order_status'] == 'READY')

    return render_template(
        'staff/dashboard.html',
        orders=orders,
        placed_count=placed_count,
        prep_count=prep_count,
        ready_count=ready_count,
        now=datetime.datetime.now()
    )

@staff_bp.route('/update-status/<int:order_id>/<string:new_status>', methods=['POST', 'GET'])
@role_required(['staff', 'admin'])
def update_status(order_id, new_status):
    try:
        order_service.update_order_status(order_id, new_status.upper())
        flash(f"Order #{order_id} updated to {new_status.upper()}.", 'success')
    except Exception as e:
        flash(str(e), 'danger')

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True, "order_id": order_id, "new_status": new_status.upper()})

    return redirect(url_for('staff.dashboard'))

@staff_bp.route('/daily-demand')
@role_required(['staff', 'admin'])
def daily_demand():
    predictions = demand_predictor.predict_daily_demand(datetime.date.today())
    return render_template('staff/daily_demand.html', predictions=predictions, today=datetime.date.today())

@staff_bp.route('/inventory-quick', methods=['GET', 'POST'])
@role_required(['staff', 'admin'])
def inventory_quick():
    if request.method == 'POST':
        food_id = int(request.form.get('food_id'))
        stock_qty = int(request.form.get('stock_quantity', 50))
        is_avail = 1 if stock_qty > 0 else 0

        execute_db("""
            UPDATE food_items 
            SET stock_quantity = %s, is_available = %s 
            WHERE id = %s
        """, (stock_qty, is_avail, food_id))

        flash('Stock updated instantly for kitchen counter.', 'success')
        return redirect(url_for('staff.inventory_quick'))

    foods = query_db("""
        SELECT f.*, c.name as category_name 
        FROM food_items f 
        JOIN food_categories c ON f.category_id = c.id 
        ORDER BY f.category_id, f.name
    """) or []

    return render_template('staff/inventory_quick.html', foods=foods)

import os
import datetime
import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file, Response
from database.db import query_db, execute_db
from routes.auth_routes import login_required, role_required
from ai.demand_prediction import demand_predictor
from ai.crowd_prediction import crowd_predictor
from ai.waste_prediction import waste_predictor
from ai.feedback_analysis import feedback_analyzer
from services.inventory_service import inventory_service
from services.seat_service import seat_service
from services.pdf_service import pdf_service
from config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@role_required(['admin'])
def dashboard():
    today_str = datetime.date.today().strftime('%Y-%m-%d')

    # Metric Cards
    total_students = query_db("SELECT COUNT(id) as cnt FROM users WHERE role = 'student'", one=True)['cnt']
    
    today_orders = query_db("""
        SELECT COUNT(id) as cnt, COALESCE(SUM(final_amount), 0.0) as revenue
        FROM orders 
        WHERE DATE(created_at) = DATE('now', 'localtime') AND order_status != 'CANCELLED'
    """, one=True)
    
    active_orders_cnt = query_db("""
        SELECT COUNT(id) as cnt FROM orders 
        WHERE order_status IN ('PLACED', 'ACCEPTED', 'PREPARING')
    """, one=True)['cnt']

    inv_summary = inventory_service.get_all_inventory_with_ai_insights()
    crowd_now = crowd_predictor.get_current_crowd_status()

    # AI Predictions for Tomorrow
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_demand = demand_predictor.predict_daily_demand(tomorrow)
    expected_orders = sum(p['predicted_demand'] for p in tomorrow_demand)
    expected_revenue = sum(p['expected_revenue'] for p in tomorrow_demand)

    # 1. Daily Revenue Chart Data (Last 7 Days)
    rev_chart = query_db("""
        SELECT DATE(created_at) as order_date, SUM(final_amount) as total_rev, COUNT(id) as count
        FROM orders
        WHERE order_status != 'CANCELLED'
        GROUP BY DATE(created_at)
        ORDER BY order_date DESC LIMIT 7
    """) or []
    rev_chart.reverse()

    # 2. Category Sales Distribution
    cat_sales = query_db("""
        SELECT c.name as category, COUNT(oi.id) as total_sold, SUM(oi.subtotal) as total_amount
        FROM order_items oi
        JOIN food_items f ON oi.food_id = f.id
        JOIN food_categories c ON f.category_id = c.id
        GROUP BY c.id, c.name
        ORDER BY total_amount DESC
    """) or []

    # 3. Top 5 Popular Food Items
    top_foods = query_db("""
        SELECT name, total_orders, rating, price, image_url 
        FROM food_items 
        ORDER BY total_orders DESC LIMIT 5
    """) or []

    # 4. Recent Active Orders
    recent_orders = query_db("""
        SELECT o.*, u.name as student_name,
               GROUP_CONCAT(CONCAT(oi.quantity, 'x ', f.name) SEPARATOR ', ') as items_summary
        FROM orders o
        JOIN users u ON o.student_id = u.id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN food_items f ON oi.food_id = f.id
        GROUP BY o.id, u.name
        ORDER BY o.created_at DESC LIMIT 8
    """) or []

    # 5. Food Rescue & Waste Prevention KPIs
    from services.rescue_service import rescue_service
    rescue_kpis = rescue_service.get_rescue_kpis()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        today_orders=today_orders['cnt'] if today_orders else 0,
        today_revenue=today_orders['revenue'] if today_orders else 0.0,
        active_orders_cnt=active_orders_cnt,
        low_stock_cnt=inv_summary['low_stock_count'],
        expected_orders=expected_orders,
        expected_revenue=expected_revenue,
        crowd_now=crowd_now,
        rev_chart=rev_chart,
        cat_sales=cat_sales,
        top_foods=top_foods,
        recent_orders=recent_orders,
        rescue_kpis=rescue_kpis
    )

@admin_bp.route('/ai-control-center')
@role_required(['admin'])
def ai_control_center():
    target_date_str = request.args.get('date', (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
    try:
        target_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d').date()
    except Exception:
        target_date = datetime.date.today() + datetime.timedelta(days=1)

    # 1. AI Demand Forecast
    demand_predictions = demand_predictor.predict_daily_demand(target_date)
    total_pred_units = sum(p['predicted_demand'] for p in demand_predictions)
    total_pred_revenue = sum(p['expected_revenue'] for p in demand_predictions)

    # 2. AI Crowd Predictions for 30-min time slots
    crowd_schedule = crowd_predictor.predict_hourly_crowd(target_date)

    # 3. AI Food Waste Analysis & Recommendations
    waste_analysis = waste_predictor.analyze_waste_risks()

    # 4. Inventory Alerts
    inv_data = inventory_service.get_all_inventory_with_ai_insights()

    # 5. Food Rescue Impact KPIs
    from services.rescue_service import rescue_service
    rescue_kpis = rescue_service.get_rescue_kpis()

    # AI High-Level Strategic Decisions
    top_demanded_item = demand_predictions[0] if demand_predictions else None
    
    return render_template(
        'admin/ai_control_center.html',
        target_date=target_date.strftime('%Y-%m-%d'),
        demand_predictions=demand_predictions,
        total_pred_units=total_pred_units,
        total_pred_revenue=total_pred_revenue,
        crowd_schedule=crowd_schedule,
        waste_analysis=waste_analysis,
        inv_data=inv_data,
        rescue_kpis=rescue_kpis,
        top_demanded_item=top_demanded_item
    )

@admin_bp.route('/menu', methods=['GET', 'POST'])
@role_required(['admin'])
def menu_manage():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_food':
            name = request.form.get('name')
            category_id = int(request.form.get('category_id'))
            price = float(request.form.get('price'))
            description = request.form.get('description')
            ingredients = request.form.get('ingredients')
            image_url = request.form.get('image_url') or 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500'
            is_veg = 1 if request.form.get('is_veg') == '1' else 0
            prep_time = int(request.form.get('prep_time_minutes', 10))
            calories = int(request.form.get('calories', 250))
            spice_level = request.form.get('spice_level', 'Medium')
            stock_qty = int(request.form.get('stock_quantity', 50))

            execute_db("""
                INSERT INTO food_items (name, category_id, price, description, ingredients, image_url, is_veg, prep_time_minutes, calories, spice_level, stock_quantity, is_available, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW())
            """, (name, category_id, price, description, ingredients, image_url, is_veg, prep_time, calories, spice_level, stock_qty))
            flash(f"Food item '{name}' added successfully!", 'success')

        elif action == 'edit_food':
            food_id = int(request.form.get('food_id'))
            name = request.form.get('name')
            category_id = int(request.form.get('category_id'))
            price = float(request.form.get('price'))
            description = request.form.get('description')
            ingredients = request.form.get('ingredients')
            image_url = request.form.get('image_url')
            is_veg = 1 if request.form.get('is_veg') == '1' else 0
            prep_time = int(request.form.get('prep_time_minutes', 10))
            calories = int(request.form.get('calories', 250))
            spice_level = request.form.get('spice_level', 'Medium')
            stock_qty = int(request.form.get('stock_quantity', 50))

            execute_db("""
                UPDATE food_items 
                SET name = %s, category_id = %s, price = %s, description = %s, ingredients = %s,
                    image_url = %s, is_veg = %s, prep_time_minutes = %s, calories = %s,
                    spice_level = %s, stock_quantity = %s
                WHERE id = %s
            """, (name, category_id, price, description, ingredients, image_url, is_veg, prep_time, calories, spice_level, stock_qty, food_id))
            flash(f"Food item '{name}' updated.", 'success')

        elif action == 'toggle_availability':
            food_id = int(request.form.get('food_id'))
            execute_db("UPDATE food_items SET is_available = CASE WHEN is_available = 1 THEN 0 ELSE 1 END WHERE id = %s", (food_id,))
            flash("Item availability updated.", 'info')

        elif action == 'delete_food':
            food_id = int(request.form.get('food_id'))
            execute_db("DELETE FROM food_items WHERE id = %s", (food_id,))
            flash("Food item deleted from catalog.", 'warning')

        return redirect(url_for('admin.menu_manage'))

    foods = query_db("""
        SELECT f.*, c.name as category_name
        FROM food_items f
        JOIN food_categories c ON f.category_id = c.id
        ORDER BY f.category_id ASC, f.name ASC
    """) or []
    categories = query_db("SELECT * FROM food_categories ORDER BY display_order ASC") or []

    return render_template('admin/menu_manage.html', foods=foods, categories=categories)

@admin_bp.route('/inventory', methods=['GET', 'POST'])
@role_required(['admin'])
def inventory_manage():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'restock':
            item_id = int(request.form.get('item_id'))
            qty = float(request.form.get('quantity'))
            notes = request.form.get('notes', '')
            inventory_service.restock_item(item_id, qty, notes=notes)
            flash('Inventory restocked successfully.', 'success')

        elif action == 'log_waste':
            item_id = int(request.form.get('item_id'))
            qty = float(request.form.get('quantity'))
            notes = request.form.get('notes', '')
            inventory_service.log_usage_or_waste(item_id, 'WASTED', qty, notes=notes)
            flash('Wastage logged and stock adjusted.', 'warning')

        elif action == 'add_item':
            item_name = request.form.get('item_name')
            category = request.form.get('category')
            stock = float(request.form.get('current_stock'))
            unit = request.form.get('unit')
            min_th = float(request.form.get('min_threshold'))
            max_cap = float(request.form.get('max_capacity'))
            cost = float(request.form.get('cost_per_unit'))
            expiry = int(request.form.get('expiry_days', 7))

            execute_db("""
                INSERT INTO inventory (item_name, category, current_stock, unit, min_threshold, max_capacity, cost_per_unit, expiry_days, status, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'IN_STOCK', NOW())
            """, (item_name, category, stock, unit, min_th, max_cap, cost, expiry))
            flash(f"Material '{item_name}' added to inventory.", 'success')

        return redirect(url_for('admin.inventory_manage'))

    inv_data = inventory_service.get_all_inventory_with_ai_insights()
    transactions = query_db("""
        SELECT t.*, i.item_name, i.unit
        FROM inventory_transactions t
        JOIN inventory i ON t.inventory_id = i.id
        ORDER BY t.created_at DESC LIMIT 15
    """) or []

    return render_template('admin/inventory.html', inv=inv_data, transactions=transactions)

@admin_bp.route('/orders')
@role_required(['admin'])
def orders_manage():
    status_filter = request.args.get('status', 'ALL')
    search_q = request.args.get('q', '').strip()

    query = """
        SELECT o.*, u.name as student_name, u.phone as student_phone,
               GROUP_CONCAT(CONCAT(oi.quantity, 'x ', f.name) SEPARATOR ', ') as items_summary
        FROM orders o
        JOIN users u ON o.student_id = u.id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN food_items f ON oi.food_id = f.id
        WHERE 1=1
    """
    params = []

    if status_filter != 'ALL':
        query += " AND o.order_status = %s"
        params.append(status_filter)

    if search_q:
        query += " AND (o.order_number LIKE %s OR u.name LIKE %s)"
        params.extend([f"%{search_q}%", f"%{search_q}%"])

    query += " GROUP BY o.id, u.name, u.phone ORDER BY o.created_at DESC"
    orders = query_db(query, tuple(params)) or []

    return render_template('admin/orders.html', orders=orders, status_filter=status_filter, search_q=search_q)

@admin_bp.route('/seats')
@role_required(['admin'])
def seats_manage():
    tables = query_db("SELECT * FROM seat_tables ORDER BY section, table_number") or []
    bookings = query_db("""
        SELECT b.*, t.table_number, t.section, u.name as student_name, u.phone as student_phone
        FROM seat_bookings b
        JOIN seat_tables t ON b.table_id = t.id
        JOIN users u ON b.student_id = u.id
        ORDER BY b.booking_date DESC, b.time_slot ASC LIMIT 25
    """) or []

    return render_template('admin/seats.html', tables=tables, bookings=bookings)

@admin_bp.route('/feedback-analytics')
@role_required(['admin'])
def feedback_analytics():
    analytics = feedback_analyzer.get_feedback_analytics()
    return render_template('admin/feedback_analytics.html', analytics=analytics)

@admin_bp.route('/users')
@role_required(['admin'])
def users_manage():
    students = query_db("SELECT * FROM users WHERE role = 'student' ORDER BY created_at DESC") or []
    staff_members = query_db("SELECT * FROM users WHERE role IN ('admin', 'staff') ORDER BY role ASC, name ASC") or []
    return render_template('admin/users.html', students=students, staff_members=staff_members)

@admin_bp.route('/reports', methods=['GET', 'POST'])
@role_required(['admin'])
def reports():
    if request.method == 'POST':
        report_type = request.form.get('report_type', 'sales')
        export_format = request.form.get('export_format', 'pdf')

        if export_format == 'pdf':
            pdf_bytes = pdf_service.generate_admin_report_pdf(report_type)
            return send_file(
                pdf_bytes,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"SmartCanteen_{report_type.title()}_Report_{datetime.date.today()}.pdf"
            )
        elif export_format == 'csv':
            # Export CSV
            output = io.StringIO()
            writer = csv.writer(output)

            if report_type == 'sales':
                orders = query_db("SELECT order_number, student_id, final_amount, payment_method, payment_status, order_status, created_at FROM orders") or []
                writer.writerow(["Order Number", "Student ID", "Final Amount", "Payment Method", "Payment Status", "Order Status", "Created At"])
                for o in orders:
                    writer.writerow([o['order_number'], o['student_id'], o['final_amount'], o['payment_method'], o['payment_status'], o['order_status'], o['created_at']])
            else:
                items = query_db("SELECT item_name, category, current_stock, unit, min_threshold, cost_per_unit, status FROM inventory") or []
                writer.writerow(["Item Name", "Category", "Current Stock", "Unit", "Min Reorder", "Cost Per Unit", "Status"])
                for it in items:
                    writer.writerow([it['item_name'], it['category'], it['current_stock'], it['unit'], it['min_threshold'], it['cost_per_unit'], it['status']])

            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename=SmartCanteen_{report_type}_{datetime.date.today()}.csv"}
            )

    return render_template('admin/reports.html')

import os
import sys

# Ensure current directory is in Python module search path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import datetime
from flask import Flask, render_template, session, redirect, url_for
from config import Config
from database.db import init_app, query_db
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.admin_routes import admin_bp
from routes.staff_routes import staff_bp
from routes.api_routes import api_bp
from ai.recommendation import recommendation_engine
from ai.crowd_prediction import crowd_predictor

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database hooks
    init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(api_bp)

    # Context Processors & Global Filters
    @app.context_processor
    def inject_global_context():
        now = datetime.datetime.now()
        unread_notifs = 0
        if 'user_id' in session:
            try:
                res = query_db("SELECT COUNT(id) as cnt FROM notifications WHERE user_id = %s AND is_read = 0", (session['user_id'],), one=True)
                unread_notifs = res['cnt'] if res else 0
            except Exception:
                unread_notifs = 0

        return {
            'now': now,
            'unread_notifications_count': unread_notifs,
            'current_user': {
                'id': session.get('user_id'),
                'name': session.get('user_name'),
                'email': session.get('user_email'),
                'role': session.get('user_role'),
                'student_id': session.get('student_id'),
                'wallet_balance': session.get('wallet_balance', 500.0)
            } if 'user_id' in session else None
        }

    # Custom Jinja Filters
    @app.template_filter('currency')
    def currency_filter(val):
        try:
            return f"₹{float(val):.2f}"
        except (ValueError, TypeError):
            return f"₹{val}"

    @app.template_filter('date_format')
    def date_format_filter(val, fmt='%d %b %Y, %I:%M %p'):
        if not val:
            return ''
        if isinstance(val, str):
            try:
                val = datetime.datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
            except Exception:
                return val
        return val.strftime(fmt)

    # Landing Page Route
    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('user_role', 'student')
            if role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif role == 'staff':
                return redirect(url_for('staff.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))

        # Fetch featured dishes for landing showcase
        popular_dishes = recommendation_engine.get_trending_items(limit=6)
        categories = query_db("SELECT * FROM food_categories ORDER BY display_order ASC") or []
        crowd_now = crowd_predictor.get_current_crowd_status()

        return render_template(
            'index.html',
            popular_dishes=popular_dishes,
            categories=categories,
            crowd_now=crowd_now
        )

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[*] Starting Smart Canteen AI Platform on port {port}")
    app.run(host='0.0.0.0', port=port)

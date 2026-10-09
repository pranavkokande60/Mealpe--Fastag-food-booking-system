import os
import sys

# Ensure current directory is in Python module search path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import datetime
import sqlite3
from config import Config
from ai.synthetic_data import (
    FOOD_CATEGORIES, FOOD_ITEMS, DEMO_USERS, SEAT_TABLES,
    INVENTORY_ITEMS, COUPONS, FEEDBACK_TEMPLATES, generate_synthetic_orders
)
from database.db import get_db, query_db, execute_db
from flask import Flask

# Initialize minimal Flask application context for database operations
app = Flask(__name__)
app.config.from_object(Config)

def setup_sqlite_tables(conn):
    """Creates SQLite schema if using SQLite fallback"""
    schema_sqlite = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        student_id TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        wallet_balance REAL NOT NULL DEFAULT 500.00,
        dietary_pref TEXT DEFAULT 'all',
        avatar_url TEXT DEFAULT '/static/images/default-avatar.png',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS food_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        icon TEXT DEFAULT 'fa-utensils',
        image_url TEXT,
        display_order INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS food_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category_id INTEGER NOT NULL,
        price REAL NOT NULL,
        image_url TEXT,
        ingredients TEXT,
        is_veg INTEGER NOT NULL DEFAULT 1,
        is_available INTEGER NOT NULL DEFAULT 1,
        stock_quantity INTEGER NOT NULL DEFAULT 50,
        prep_time_minutes INTEGER NOT NULL DEFAULT 10,
        calories INTEGER DEFAULT 250,
        spice_level TEXT DEFAULT 'Medium',
        rating REAL DEFAULT 4.5,
        total_orders INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES food_categories(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL UNIQUE,
        student_id INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        discount_amount REAL DEFAULT 0.00,
        tax_amount REAL DEFAULT 0.00,
        final_amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT NOT NULL DEFAULT 'PENDING',
        order_status TEXT NOT NULL DEFAULT 'PLACED',
        estimated_prep_time INTEGER NOT NULL DEFAULT 15,
        pickup_time TEXT,
        special_instructions TEXT,
        cancellation_fee REAL DEFAULT 0.00,
        refund_amount REAL DEFAULT 0.00,
        cancellation_reason TEXT,
        cancelled_at TEXT,
        is_rescue_order INTEGER DEFAULT 0,
        rescue_offer_id INTEGER,
        collection_pin TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        food_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        unit_price REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (food_id) REFERENCES food_items(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT NOT NULL,
        transaction_ref TEXT NOT NULL UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        category TEXT NOT NULL,
        current_stock REAL NOT NULL DEFAULT 0.00,
        unit TEXT NOT NULL DEFAULT 'kg',
        min_threshold REAL NOT NULL DEFAULT 10.00,
        max_capacity REAL NOT NULL DEFAULT 100.00,
        cost_per_unit REAL NOT NULL DEFAULT 20.00,
        expiry_days INTEGER DEFAULT 7,
        status TEXT DEFAULT 'IN_STOCK',
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS inventory_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inventory_id INTEGER NOT NULL,
        transaction_type TEXT NOT NULL,
        quantity REAL NOT NULL,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (inventory_id) REFERENCES inventory(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS seat_tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_number TEXT NOT NULL UNIQUE,
        capacity INTEGER NOT NULL DEFAULT 4,
        section TEXT DEFAULT 'Main Hall',
        is_active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS seat_bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_code TEXT NOT NULL UNIQUE,
        student_id INTEGER NOT NULL,
        table_id INTEGER NOT NULL,
        guests_count INTEGER NOT NULL DEFAULT 1,
        booking_date TEXT NOT NULL,
        time_slot TEXT NOT NULL,
        status TEXT DEFAULT 'CONFIRMED',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (table_id) REFERENCES seat_tables(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        order_id INTEGER,
        rating INTEGER NOT NULL DEFAULT 5,
        aspect TEXT DEFAULT 'General',
        sentiment TEXT DEFAULT 'POSITIVE',
        comment TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT DEFAULT 'info',
        is_read INTEGER DEFAULT 0,
        link TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        discount_percent REAL DEFAULT 0.00,
        discount_amount REAL DEFAULT 0.00,
        min_order_amount REAL DEFAULT 0.00,
        max_discount REAL DEFAULT 100.00,
        is_active INTEGER DEFAULT 1,
        expiry_date TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ai_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_type TEXT NOT NULL,
        target_date TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        explanation TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS food_rescue_offers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_order_id INTEGER NOT NULL,
        original_student_id INTEGER NOT NULL,
        food_id INTEGER NOT NULL,
        food_name TEXT,
        quantity_available INTEGER NOT NULL DEFAULT 1,
        quantity_claimed INTEGER NOT NULL DEFAULT 0,
        original_price REAL NOT NULL,
        rescue_price REAL NOT NULL,
        discount_percent INTEGER DEFAULT 10,
        offer_status TEXT DEFAULT 'AVAILABLE',
        collection_point TEXT DEFAULT 'College Canteen Central Counter',
        expires_at TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (original_order_id) REFERENCES orders(id) ON DELETE CASCADE,
        FOREIGN KEY (original_student_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (food_id) REFERENCES food_items(id) ON DELETE CASCADE
    );
    """
    cur = conn.cursor()
    cur.executescript(schema_sqlite)
    conn.commit()
    cur.close()

def init_database():
    """Initializes and seeds the database with all initial data and ML history"""
    print("=" * 70)
    print("[*] SMART CANTEEN INITIALIZER: Setting up Database & Training AI Models")
    print("=" * 70)

    with app.app_context():
        conn = get_db()
        from flask import g
        backend = getattr(g, 'db_backend', 'sqlite')
        print(f"[*] Database Backend detected: {backend.upper()}")

        if backend == 'sqlite':
            print("[*] Initializing SQLite database schema...")
            setup_sqlite_tables(conn)
        else:
            print("[*] MySQL connection confirmed.")

        # 1. Seed Categories
        print("[*] Seeding Food Categories...")
        for cat in FOOD_CATEGORIES:
            execute_db("""
                INSERT OR IGNORE INTO food_categories (id, name, description, icon, image_url, display_order)
                VALUES (%s, %s, %s, %s, %s, %s)
            """ if backend == 'sqlite' else """
                INSERT INTO food_categories (id, name, description, icon, image_url, display_order)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=VALUES(name)
            """, (cat["id"], cat["name"], cat["description"], cat["icon"], cat["image_url"], cat["display_order"]))

        # 2. Seed Food Items
        print("[*] Seeding 25 Food Items across 6 categories...")
        for f in FOOD_ITEMS:
            execute_db("""
                INSERT OR IGNORE INTO food_items 
                (id, name, description, category_id, price, image_url, ingredients, is_veg, is_available, stock_quantity, prep_time_minutes, calories, spice_level, rating, total_orders)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """ if backend == 'sqlite' else """
                INSERT INTO food_items 
                (id, name, description, category_id, price, image_url, ingredients, is_veg, is_available, stock_quantity, prep_time_minutes, calories, spice_level, rating, total_orders)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=VALUES(name)
            """, (
                f["id"], f["name"], f["description"], f["category_id"], f["price"],
                f["image_url"], f["ingredients"], f["is_veg"], 1, 60,
                f["prep_time_minutes"], f["calories"], f["spice_level"], f["rating"], 120
            ))

        # 3. Seed Users (Admin, Staff, Student)
        print("[*] Seeding Demo Users (Admins, Staff, Students)...")
        for u in DEMO_USERS:
            execute_db("""
                INSERT OR IGNORE INTO users (name, email, phone, student_id, password_hash, role, wallet_balance, dietary_pref)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """ if backend == 'sqlite' else """
                INSERT INTO users (name, email, phone, student_id, password_hash, role, wallet_balance, dietary_pref)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE name=VALUES(name)
            """, (u["name"], u["email"], u["phone"], u["student_id"], u["password_hash"], u["role"], u["wallet_balance"], u["dietary_pref"]))

        # 4. Seed Seat Tables
        print("[*] Seeding 15 Canteen Tables across 4 sections...")
        for t in SEAT_TABLES:
            execute_db("""
                INSERT OR IGNORE INTO seat_tables (table_number, capacity, section, is_active)
                VALUES (%s, %s, %s, 1)
            """ if backend == 'sqlite' else """
                INSERT INTO seat_tables (table_number, capacity, section, is_active)
                VALUES (%s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE capacity=VALUES(capacity)
            """, (t["table_number"], t["capacity"], t["section"]))

        # 5. Seed Inventory Items
        print("[*] Seeding Inventory raw materials...")
        for inv in INVENTORY_ITEMS:
            execute_db("""
                INSERT OR IGNORE INTO inventory (item_name, category, current_stock, unit, min_threshold, max_capacity, cost_per_unit, expiry_days, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'IN_STOCK')
            """ if backend == 'sqlite' else """
                INSERT INTO inventory (item_name, category, current_stock, unit, min_threshold, max_capacity, cost_per_unit, expiry_days, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'IN_STOCK')
                ON DUPLICATE KEY UPDATE item_name=VALUES(item_name)
            """, (
                inv["item_name"], inv["category"], inv["current_stock"], inv["unit"],
                inv["min_threshold"], inv["max_capacity"], inv["cost_per_unit"], inv["expiry_days"]
            ))

        # 6. Seed Coupons
        print("[*] Seeding Student Coupons...")
        for c in COUPONS:
            execute_db("""
                INSERT OR IGNORE INTO coupons (code, discount_percent, discount_amount, min_order_amount, max_discount, is_active, expiry_date)
                VALUES (%s, %s, %s, %s, %s, 1, %s)
            """ if backend == 'sqlite' else """
                INSERT INTO coupons (code, discount_percent, discount_amount, min_order_amount, max_discount, is_active, expiry_date)
                VALUES (%s, %s, %s, %s, %s, 1, %s)
                ON DUPLICATE KEY UPDATE code=VALUES(code)
            """, (c["code"], c["discount_percent"], c["discount_amount"], c["min_order_amount"], c["max_discount"], c["expiry_date"]))

        # 7. Seed Synthetic Orders for AI Engine
        order_count = query_db("SELECT COUNT(id) as cnt FROM orders", one=True)
        if not order_count or order_count['cnt'] < 50:
            print("[*] Generating 500+ realistic synthetic historical orders for Machine Learning training...")
            synth_orders = generate_synthetic_orders(num_orders=500)
            for o in synth_orders:
                oid = execute_db("""
                    INSERT INTO orders (order_number, student_id, total_amount, discount_amount, tax_amount, final_amount, payment_method, payment_status, order_status, estimated_prep_time, pickup_time, special_instructions, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    o["order_number"], o["student_id"], o["total_amount"], o["discount_amount"],
                    o["tax_amount"], o["final_amount"], o["payment_method"], o["payment_status"],
                    o["order_status"], o["estimated_prep_time"], str(o["pickup_time"]),
                    o["special_instructions"], o["created_at"], o["updated_at"]
                ))
                for item in o["items"]:
                    execute_db("""
                        INSERT INTO order_items (order_id, food_id, quantity, unit_price, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (oid, item["food_id"], item["quantity"], item["unit_price"], item["subtotal"]))

        # 8. Seed Feedback
        fb_count = query_db("SELECT COUNT(id) as cnt FROM feedback", one=True)
        if not fb_count or fb_count['cnt'] < 10:
            print("[*] Seeding student feedback dataset...")
            for text, rating, aspect, sentiment in FEEDBACK_TEMPLATES:
                execute_db("""
                    INSERT INTO feedback (student_id, order_id, rating, aspect, sentiment, comment, created_at)
                    VALUES (%s, NULL, %s, %s, %s, %s, NOW())
                """, (6, rating, aspect, sentiment, text))

        # 9. Train and serialize ML models
        print("[*] Training AI Models (Demand Forecaster & Crowd Classifier)...")
        from ai.demand_prediction import demand_predictor
        from ai.crowd_prediction import crowd_predictor
        demand_predictor.train_model()
        crowd_predictor.train_model()
        print("[OK] AI Models trained and serialized successfully!")

        print("\n" + "=" * 70)
        print("[OK] SMART CANTEEN SETUP COMPLETE!")
        print("=" * 70)
        print("DEMO CREDENTIALS:")
        print("  1. Student:  student@smartcanteen.com  /  Student@123")
        print("  2. Admin:    admin@smartcanteen.com    /  Admin@123")
        print("  3. Staff:    staff@smartcanteen.com    /  Staff@123")
        print("=" * 70)

if __name__ == '__main__':
    init_database()

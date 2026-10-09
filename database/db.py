import os
import sqlite3
import re
from flask import g, current_app
from config import Config

# Optional PostgreSQL imports
try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

# Optional MySQL imports
try:
    import pymysql
    import pymysql.cursors
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

try:
    import mysql.connector
    HAS_MYSQL_CONNECTOR = True
except ImportError:
    HAS_MYSQL_CONNECTOR = False

def get_db():
    """
    Returns an active database connection for the current Flask request context.
    Automatically detects PostgreSQL, MySQL, or SQLite based on configuration.
    """
    if 'db' not in g:
        db_type = Config.DB_TYPE.lower()
        
        # 1. Try PostgreSQL if configured or in auto mode
        if db_type in ['postgres', 'postgresql']:
            conn = _try_postgres_connection()
            if conn:
                g.db = conn
                g.db_backend = 'postgres'
                return g.db
            else:
                raise ConnectionError("PostgreSQL connection failed. Please verify PG_PASSWORD and that PostgreSQL service is running.")
                
        if db_type == 'auto':
            # Check postgres first
            conn = _try_postgres_connection()
            if conn:
                g.db = conn
                g.db_backend = 'postgres'
                return g.db
            # Check mysql next
            conn = _try_mysql_connection()
            if conn:
                g.db = conn
                g.db_backend = 'mysql'
                return g.db
        
        # 2. Try MySQL
        if db_type == 'mysql':
            conn = _try_mysql_connection()
            if conn:
                g.db = conn
                g.db_backend = 'mysql'
                return g.db
            else:
                raise ConnectionError("MySQL connection failed. Please ensure MySQL server is running.")
        
        # 3. Fallback to SQLite (zero-config, high performance)
        g.db = _get_sqlite_connection()
        g.db_backend = 'sqlite'
        
    return g.db

def _try_postgres_connection():
    """Attempts to establish connection to PostgreSQL / pgAdmin database"""
    if HAS_PSYCOPG2:
        try:
            conn = psycopg2.connect(
                host=Config.PG_HOST,
                port=Config.PG_PORT,
                user=Config.PG_USER,
                password=Config.PG_PASSWORD,
                dbname=Config.PG_DATABASE,
                connect_timeout=3
            )
            _migrate_database_schema(conn, 'postgres')
            return conn
        except Exception:
            pass
    return None

def _try_mysql_connection():
    """Attempts to establish connection to MySQL database"""
    if HAS_PYMYSQL:
        try:
            conn = pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                charset='utf8mb4'
            )
            _migrate_database_schema(conn, 'mysql')
            return conn
        except Exception:
            pass
            
    if HAS_MYSQL_CONNECTOR:
        try:
            conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                autocommit=False
            )
            _migrate_database_schema(conn, 'mysql')
            return conn
        except Exception:
            pass
            
    return None

def _migrate_database_schema(conn, backend):
    """Ensures food_rescue_offers table and extended order columns exist automatically"""
    try:
        if backend == 'sqlite':
            conn.execute("""
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
            """)
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(orders)")
            existing_cols = {row[1] for row in cur.fetchall()}
            columns_to_add = [
                ("cancellation_fee", "REAL DEFAULT 0.00"),
                ("refund_amount", "REAL DEFAULT 0.00"),
                ("cancellation_reason", "TEXT"),
                ("cancelled_at", "TEXT"),
                ("is_rescue_order", "INTEGER DEFAULT 0"),
                ("rescue_offer_id", "INTEGER"),
                ("collection_pin", "TEXT")
            ]
            for col_name, col_def in columns_to_add:
                if col_name not in existing_cols:
                    try:
                        conn.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_def}")
                    except Exception:
                        pass
            conn.commit()
        elif backend == 'postgres':
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS food_rescue_offers (
                    id SERIAL PRIMARY KEY,
                    original_order_id INT NOT NULL,
                    original_student_id INT NOT NULL,
                    food_id INT NOT NULL,
                    food_name VARCHAR(120),
                    quantity_available INT NOT NULL DEFAULT 1,
                    quantity_claimed INT NOT NULL DEFAULT 0,
                    original_price DECIMAL(10,2) NOT NULL,
                    rescue_price DECIMAL(10,2) NOT NULL,
                    discount_percent INT DEFAULT 10,
                    offer_status VARCHAR(30) DEFAULT 'AVAILABLE',
                    collection_point VARCHAR(120) DEFAULT 'College Canteen Central Counter',
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (original_order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (original_student_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (food_id) REFERENCES food_items(id) ON DELETE CASCADE
                );
                ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancellation_fee DECIMAL(10,2) DEFAULT 0.00;
                ALTER TABLE orders ADD COLUMN IF NOT EXISTS refund_amount DECIMAL(10,2) DEFAULT 0.00;
                ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancellation_reason TEXT;
                ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMP;
                ALTER TABLE orders ADD COLUMN IF NOT EXISTS is_rescue_order INT DEFAULT 0;
                ALTER TABLE orders ADD COLUMN IF NOT EXISTS rescue_offer_id INT;
                ALTER TABLE orders ADD COLUMN IF NOT EXISTS collection_pin VARCHAR(20);
            """)
            conn.commit()
    except Exception:
        pass

def _get_sqlite_connection():
    """Connects to local SQLite database with DictRow factory"""
    os.makedirs(os.path.dirname(Config.SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.create_function("GREATEST", -1, max)
    conn.create_function("greatest", -1, max)
    conn.create_function("LEAST", -1, min)
    conn.create_function("least", -1, min)
    _migrate_database_schema(conn, 'sqlite')
    return conn

def close_db(e=None):
    """Closes database connection at end of request"""
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass

def _normalize_query(query, backend):
    """Translates SQL syntax between PostgreSQL, MySQL, and SQLite seamlessly"""
    if backend == 'sqlite':
        query = re.sub(r'(?<!%)(%s)', '?', query)
        query = query.replace('NOW()', "datetime('now', 'localtime')")
        query = query.replace('CURRENT_TIMESTAMP', "datetime('now', 'localtime')")
        query = query.replace('CURDATE()', "date('now', 'localtime')")
        query = re.sub(r'\bGREATEST\((.*?)\)', r'MAX(\1)', query, flags=re.IGNORECASE)
        query = re.sub(r'\bLEAST\((.*?)\)', r'MIN(\1)', query, flags=re.IGNORECASE)
        
        def _repl_concat(m):
            args_str = m.group(1)
            parts = [p.strip() for p in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", args_str)]
            return "(" + " || ".join(parts) + ")"
        query = re.sub(r'\bCONCAT\((.*?)\)', _repl_concat, query, flags=re.IGNORECASE)
        query = re.sub(r'\bGROUP_CONCAT\((.*?)\s+SEPARATOR\s+([\'"].*?[\'"])\)', r'GROUP_CONCAT(\1, \2)', query, flags=re.IGNORECASE)

    elif backend == 'postgres':
        # Replace SQLite ? placeholder with %s
        query = query.replace('?', '%s')
        
        # Replace SQLite/MySQL date functions with standard PostgreSQL functions
        query = query.replace("DATE('now', 'localtime')", "CURRENT_DATE")
        query = query.replace("date('now', 'localtime')", "CURRENT_DATE")
        query = query.replace("datetime('now', 'localtime')", "CURRENT_TIMESTAMP")
        query = re.sub(r'\bCURDATE\(\)', 'CURRENT_DATE', query, flags=re.IGNORECASE)
        query = re.sub(r'\bNOW\(\)', 'CURRENT_TIMESTAMP', query, flags=re.IGNORECASE)
        
        # Translate strftime('%Y-%m', expr) -> TO_CHAR(expr, 'YYYY-MM')
        query = re.sub(r"strftime\(['\"]%Y-%m['\"],\s*([^)]+)\)", r"TO_CHAR(\1, 'YYYY-MM')", query, flags=re.IGNORECASE)
        query = re.sub(r"strftime\(['\"]%Y-%m-%d['\"],\s*([^)]+)\)", r"TO_CHAR(\1, 'YYYY-MM-DD')", query, flags=re.IGNORECASE)
        
        # Translate GROUP_CONCAT(expr SEPARATOR sep) -> STRING_AGG(CAST(expr AS TEXT), sep)
        def _repl_group_concat(m):
            expr = m.group(1).strip()
            sep = m.group(2).strip()
            return f"STRING_AGG(CAST({expr} AS TEXT), {sep})"
        query = re.sub(r'\bGROUP_CONCAT\((.*?)\s+SEPARATOR\s+([\'"].*?[\'"])\)', _repl_group_concat, query, flags=re.IGNORECASE)
        query = re.sub(r'\bGROUP_CONCAT\((.*?)\s*,\s*([\'"].*?[\'"])\)', _repl_group_concat, query, flags=re.IGNORECASE)
        query = re.sub(r'\bGROUP_CONCAT\((.*?)\)', r"STRING_AGG(CAST(\1 AS TEXT), ', ')", query, flags=re.IGNORECASE)

    elif backend == 'mysql':
        query = query.replace('?', '%s')
        
    return query

def query_db(query, args=(), one=False):
    """
    Executes a SELECT query and returns results as dictionary objects.
    """
    conn = get_db()
    backend = getattr(g, 'db_backend', 'sqlite')
    norm_query = _normalize_query(query, backend)
    
    if backend == 'sqlite':
        cur = conn.cursor()
        cur.execute(norm_query, args)
        rv = cur.fetchall()
        cur.close()
        res = [dict(row) for row in rv]
        return (res[0] if res else None) if one else res
    elif backend == 'postgres':
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(norm_query, args)
        rv = cur.fetchall()
        cur.close()
        res = [dict(row) for row in rv]
        return (res[0] if res else None) if one else res
    else:
        # MySQL
        if HAS_PYMYSQL:
            cur = conn.cursor(pymysql.cursors.DictCursor)
        elif HAS_MYSQL_CONNECTOR:
            cur = conn.cursor(dictionary=True)
        else:
            cur = conn.cursor()
        cur.execute(norm_query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv

def execute_db(query, args=(), commit=True):
    """
    Executes an INSERT / UPDATE / DELETE statement.
    Returns the last inserted row ID (if applicable) or affected rows count.
    """
    conn = get_db()
    backend = getattr(g, 'db_backend', 'sqlite')
    norm_query = _normalize_query(query, backend)
    
    if backend == 'sqlite':
        cur = conn.cursor()
        cur.execute(norm_query, args)
        last_id = cur.lastrowid
        row_count = cur.rowcount
        if commit:
            conn.commit()
        cur.close()
        return last_id if last_id else row_count
    elif backend == 'postgres':
        # If insert and no returning id, add RETURNING id to get lastrowid
        is_insert = norm_query.strip().upper().startswith('INSERT')
        if is_insert and 'RETURNING' not in norm_query.upper():
            norm_query = norm_query.rstrip('; ') + ' RETURNING id;'
            
        cur = conn.cursor()
        cur.execute(norm_query, args)
        last_id = None
        if is_insert:
            try:
                row = cur.fetchone()
                if row:
                    last_id = row[0]
            except Exception:
                pass
        row_count = cur.rowcount
        if commit:
            conn.commit()
        cur.close()
        return last_id if last_id is not None else row_count
    else:
        # MySQL
        if HAS_PYMYSQL:
            cur = conn.cursor(pymysql.cursors.DictCursor)
        elif HAS_MYSQL_CONNECTOR:
            cur = conn.cursor(dictionary=True)
        else:
            cur = conn.cursor()
        cur.execute(norm_query, args)
        last_id = cur.lastrowid
        row_count = cur.rowcount
        if commit:
            conn.commit()
        cur.close()
        return last_id if last_id else row_count

def init_app(app):
    """Registers database teardown hooks with Flask app"""
    app.teardown_appcontext(close_db)

import os
import sqlite3
import re
from flask import g, current_app
from config import Config

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
    Automatically detects MySQL or SQLite based on configuration and availability.
    """
    if 'db' not in g:
        db_type = Config.DB_TYPE
        
        # If user configured MySQL or 'auto', try MySQL first
        if db_type in ['mysql', 'auto']:
            conn = _try_mysql_connection()
            if conn:
                g.db = conn
                g.db_backend = 'mysql'
                return g.db
            elif db_type == 'mysql':
                raise ConnectionError("MySQL connection failed. Please ensure MySQL server is running or set DB_TYPE='sqlite' in .env")
        
        # Fallback to SQLite (zero-config, high performance)
        g.db = _get_sqlite_connection()
        g.db_backend = 'sqlite'
        
    return g.db

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
            return conn
        except Exception:
            pass
            
    return None

def _get_sqlite_connection():
    """Connects to local SQLite database with DictRow factory"""
    os.makedirs(os.path.dirname(Config.SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
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
    """Translates SQL syntax between MySQL and SQLite seamlessly"""
    if backend == 'sqlite':
        # Replace MySQL %s placeholder with SQLite ? placeholder
        query = re.sub(r'(?<!%)(%s)', '?', query)
        query = query.replace('NOW()', "datetime('now', 'localtime')")
        query = query.replace('CURRENT_TIMESTAMP', "datetime('now', 'localtime')")
        query = query.replace('CURDATE()', "date('now', 'localtime')")
        
        # Translate MySQL CONCAT(a, b, c) -> (a || b || c)
        def _repl_concat(m):
            args_str = m.group(1)
            parts = [p.strip() for p in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", args_str)]
            return "(" + " || ".join(parts) + ")"
        query = re.sub(r'\bCONCAT\((.*?)\)', _repl_concat, query, flags=re.IGNORECASE)

        # Translate MySQL GROUP_CONCAT(expr SEPARATOR 'sep') -> GROUP_CONCAT(expr, 'sep')
        query = re.sub(r'\bGROUP_CONCAT\((.*?)\s+SEPARATOR\s+([\'"].*?[\'"])\)', r'GROUP_CONCAT(\1, \2)', query, flags=re.IGNORECASE)

    elif backend == 'mysql':
        # Replace SQLite ? placeholder with MySQL %s
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

import os
import sys
from config import Config
from database.db import _try_postgres_connection

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def test():
    print("Testing connection to PostgreSQL (pgAdmin)...")
    print(f"Host: {Config.PG_HOST}:{Config.PG_PORT}")
    print(f"Database: {Config.PG_DATABASE}")
    print(f"User: {Config.PG_USER}")
    print(f"Password configured: {'*' * len(Config.PG_PASSWORD)}")
    
    conn = _try_postgres_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users;")
        count = cur.fetchone()[0]
        print(f"\n✅ SUCCESS! Connected to pgAdmin PostgreSQL!")
        print(f"Found {count} users in 'users' table.")
        conn.close()
    else:
        print("\n❌ Could not connect to PostgreSQL.")
        print("Please check your PostgreSQL password in .env or run:")
        print("  python test_pg_connection.py <your_password>")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        Config.PG_PASSWORD = sys.argv[1]
    test()

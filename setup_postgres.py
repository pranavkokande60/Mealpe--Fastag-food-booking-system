import os
import sys
import psycopg2

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def setup():
    print("=" * 60)
    print("   CONNECT SMART CANTEEN TO PGADMIN (POSTGRESQL)")
    print("=" * 60)
    print("PostgreSQL Service is RUNNING on port 5432.\n")
    
    password = ""
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = input("Enter your pgAdmin / PostgreSQL password: ").strip()
        
    print(f"\nTesting connection with user 'postgres' and database 'smart_canteen'...")
    
    # Try connecting to smart_canteen database
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password=password,
            dbname='smart_canteen',
            connect_timeout=5
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users;")
        user_count = cur.fetchone()[0]
        conn.close()
        
        print("\n" + "=" * 60)
        print("  SUCCESS! Connected to pgAdmin PostgreSQL!")
        print(f"  Verified database 'smart_canteen' (Found {user_count} users).")
        print("=" * 60)
        
        # Save to .env
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        env_content = f"""# Database Mode: postgres
DB_TYPE=postgres
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD={password}
PG_DATABASE=smart_canteen
SECRET_KEY=smart-canteen-super-secret-key-2026-xyz987
"""
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)
            
        print(f"\nConfiguration saved to {env_path}!")
        print("Now, every time you start 'python app.py', it will connect to pgAdmin directly.")
        return
        
    except psycopg2.OperationalError as e:
        err_msg = str(e)
        if "password authentication failed" in err_msg:
            print("\n❌ Error: Incorrect password for user 'postgres'.")
            print("Please re-run 'python setup_postgres.py' and enter the exact password you use when opening pgAdmin.")
        elif 'database "smart_canteen" does not exist' in err_msg:
            print("\n❌ Error: Database 'smart_canteen' was not found in PostgreSQL.")
            print("Please open pgAdmin, right-click 'Databases' -> 'Create' -> 'Database...', and name it 'smart_canteen'.")
        else:
            print(f"\n❌ Connection error: {err_msg}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    setup()

import os
import sys
import sqlite3

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "smart_canteen.db")

def list_all_tables():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence' ORDER BY name;")
    tables = cur.fetchall()
    
    print("\n" + "=" * 60)
    print(" [DATABASE] SMART CANTEEN DATABASE TABLES OVERVIEW")
    print("=" * 60)
    print(f"Database File: {os.path.abspath(DB_PATH)}\n")
    print(f"{'#':<4} {'Table Name':<28} {'Total Rows':<12}")
    print("-" * 50)
    
    for idx, (tbl_name,) in enumerate(tables, 1):
        cur.execute(f"SELECT COUNT(*) FROM {tbl_name};")
        count = cur.fetchone()[0]
        print(f"{idx:<4} {tbl_name:<28} {count:<12}")
    
    print("-" * 50)
    print("\nHow to view table rows:")
    print("  python view_db.py <table_name>   (e.g., python view_db.py users)")
    print("  python view_db.py food_items")
    print("  python view_db.py orders")
    print("  python view_db.py all\n")
    conn.close()

def view_table(table_name, limit=15):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    try:
        cur.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
        rows = cur.fetchall()
        
        if not rows:
            print(f"\nTable '{table_name}' is currently empty.\n")
            return
            
        columns = rows[0].keys()
        
        print("\n" + "=" * 80)
        print(f" TABLE: {table_name.upper()} (Showing first {min(len(rows), limit)} rows)")
        print("=" * 80)
        
        # Calculate max width for each column
        col_widths = {}
        for col in columns:
            col_widths[col] = max(len(col), max((len(str(r[col])) for r in rows), default=0))
            col_widths[col] = min(col_widths[col], 30) # cap width
            
        header_str = " | ".join(f"{col:<{col_widths[col]}}" for col in columns)
        print(header_str)
        print("-" * len(header_str))
        
        for r in rows:
            row_str = " | ".join(f"{str(r[col])[:30]:<{col_widths[col]}}" for col in columns)
            print(row_str)
            
        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        total_count = cur.fetchone()[0]
        print("-" * len(header_str))
        print(f"Total rows in '{table_name}': {total_count}\n")
    except Exception as e:
        print(f"Error accessing table '{table_name}': {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip().lower()
        if arg == "all":
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence' ORDER BY name;")
            tables = [t[0] for t in cur.fetchall()]
            conn.close()
            for tbl in tables:
                view_table(tbl, limit=5)
        else:
            view_table(arg)
    else:
        list_all_tables()

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "smart_canteen.db")
SQL_DUMP_PATH = os.path.join(os.path.dirname(__file__), "database", "smart_canteen_dump.sql")
DESKTOP_DUMP_PATH = r"C:\Users\prana\OneDrive\Desktop\smart_canteen\database\smart_canteen_dump.sql"

def dump_to_sql():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    with open(SQL_DUMP_PATH, 'w', encoding='utf-8') as f:
        f.write("-- Smart Canteen Database Full SQL Dump\n")
        f.write("-- For use in pgAdmin (PostgreSQL), phpMyAdmin (MySQL), or DBeaver\n\n")
        
        for line in conn.iterdump():
            f.write(f"{line}\n")
            
    print(f"Generated complete SQL dump at: {SQL_DUMP_PATH}")
    
    # Also sync to Desktop folder
    try:
        os.makedirs(os.path.dirname(DESKTOP_DUMP_PATH), exist_ok=True)
        with open(DESKTOP_DUMP_PATH, 'w', encoding='utf-8') as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
        print(f"Synced dump to: {DESKTOP_DUMP_PATH}")
    except Exception as e:
        print(f"Desktop sync notice: {e}")
        
    conn.close()

if __name__ == "__main__":
    dump_to_sql()

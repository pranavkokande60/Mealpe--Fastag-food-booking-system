import os
import sys
import sqlite3

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "smart_canteen.db")

def run_sql_query(query, conn):
    query = query.strip()
    if not query:
        return
    try:
        cur = conn.cursor()
        cur.execute(query)
        if query.lower().startswith("select") or query.lower().startswith("pragma"):
            rows = cur.fetchall()
            if not rows:
                print(" Query executed successfully. (0 rows returned)\n")
                return
            columns = [desc[0] for desc in cur.description]
            col_widths = {col: max(len(col), max((len(str(r[i])) for r in rows), default=0)) for i, col in enumerate(columns)}
            # Cap column widths for clean display
            for col in col_widths:
                col_widths[col] = min(col_widths[col], 35)
                
            header = " | ".join(f"{col:<{col_widths[col]}}" for col in columns)
            divider = "-" * len(header)
            print("\n" + divider)
            print(header)
            print(divider)
            for r in rows:
                row_str = " | ".join(f"{str(val)[:35]:<{col_widths[columns[i]]}}" for i, val in enumerate(r))
                print(row_str)
            print(divider)
            print(f"Total: {len(rows)} row(s)\n")
        else:
            conn.commit()
            print(f" Query executed successfully. ({cur.rowcount} row(s) affected)\n")
    except Exception as e:
        print(f" SQL Error: {e}\n")

def interactive_shell():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    print("=" * 70)
    print("  SMART CANTEEN SQL CONSOLE")
    print("=" * 70)
    print(f"Connected to: {os.path.abspath(DB_PATH)}")
    print("Type any SQL query (e.g. SELECT * FROM users;) and press Enter.")
    print("Special commands: 'tables' to list tables, 'exit' or 'quit' to exit.\n")
    
    while True:
        try:
            query = input("SQL> ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print("Exiting SQL console. Goodbye!")
                break
            if query.lower() in ["tables", "show tables", "show tables;"]:
                query = "SELECT name AS Table_Name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';"
            elif query.lower().startswith("desc ") or query.lower().startswith("describe "):
                tbl = query.split()[1].replace(";", "")
                query = f"PRAGMA table_info({tbl});"
            run_sql_query(query, conn)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting SQL console. Goodbye!")
            break
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        custom_query = " ".join(sys.argv[1:])
        conn = sqlite3.connect(DB_PATH)
        run_sql_query(custom_query, conn)
        conn.close()
    else:
        interactive_shell()

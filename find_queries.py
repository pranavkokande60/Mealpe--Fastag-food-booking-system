import os
import re

base_dir = r"C:\Users\prana\OneDrive\Desktop\smart_canteen"
for root, dirs, files in os.walk(base_dir):
    if '.git' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8') as fp:
                content = fp.read()
                # Find all SQL queries inside query_db or execute_db
                calls = re.findall(r'(?:query_db|execute_db)\s*\(\s*["\']+(.*?)["\']+', content, flags=re.DOTALL)
                for q in calls:
                    if 'GROUP BY' in q.upper() or 'STRFTIME' in q.upper() or 'DATE_FORMAT' in q.upper() or 'COUNT(' in q.upper():
                        print(f"File: {f}")
                        print(f"Query: {q.strip()[:200]}")
                        print("-" * 50)

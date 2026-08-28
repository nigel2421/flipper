import sqlite3
import os

def check_db(db_path):
    if not os.path.exists(db_path):
        print(f"{db_path} does not exist")
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"=== {db_path} ({os.path.getsize(db_path)/1024:.1f} KB) ===")
    print("Tables:", len(tables))
    for t in ['auth_user', 'publications_magazine', 'publications_article']:
        if t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t};")
            print(f"  {t}: {cursor.fetchone()[0]}")
    conn.close()

if __name__ == "__main__":
    check_db("db.sqlite3")
    check_db("hostpinnaclrdb.sqlite3")

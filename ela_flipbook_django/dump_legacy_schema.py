import sqlite3

def dump_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = [
        'publications_magazine', 
        'publications_article', 
        'publications_author', 
        'publications_tag',
        'publications_event',
        'publications_profile',
        'publications_contributor',
        'publications_rating',
        'publications_comment',
        'publications_commentreport',
        'publications_comment_liked_by',
        'publications_whatsappupdate' # Checking if it exists
    ]
    
    for table in tables:
        try:
            cursor.execute(f"PRAGMA table_info({table});")
            cols = cursor.fetchall()
            if not cols:
                print(f"--- Table {table} does not exist ---")
                continue
            print(f"--- {table} ---")
            for col in cols:
                print(f"  {col[1]} ({col[2]})")
        except Exception as e:
            print(f"Error checking {table}: {e}")
            
    conn.close()

if __name__ == "__main__":
    dump_schema('hostpinnaclrdb.sqlite3')

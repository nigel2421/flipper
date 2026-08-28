import sqlite3

def fix_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check publications_event columns
    cursor.execute("PRAGMA table_info(publications_event);")
    cols = [c[1] for c in cursor.fetchall()]
    print("publications_event columns:", cols)
    
    if 'date' not in cols:
        print("Adding column 'date' to publications_event...")
        cursor.execute("ALTER TABLE publications_event ADD COLUMN date datetime;")
        if 'event_date' in cols:
            cursor.execute("UPDATE publications_event SET date = event_date;")
        conn.commit()

    if 'image' not in cols:
        print("Adding column 'image' to publications_event...")
        cursor.execute("ALTER TABLE publications_event ADD COLUMN image varchar(255);")
        if 'poster' in cols:
            cursor.execute("UPDATE publications_event SET image = poster;")
        conn.commit()

    conn.close()
    print("Schema alignment complete!")

if __name__ == "__main__":
    fix_schema("hostpinnaclrdb.sqlite3")

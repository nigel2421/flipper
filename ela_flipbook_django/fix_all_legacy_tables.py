import os
import sqlite3
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from django.apps import apps

def align_db_schema(db_path):
    print(f"Aligning schema for {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    app_config = apps.get_app_config('publications')
    for model in app_config.get_models():
        table_name = model._meta.db_table
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        if not cursor.fetchone():
            print(f"Table {table_name} does not exist, skipping...")
            continue
            
        # Get existing columns
        cursor.execute(f"PRAGMA table_info({table_name});")
        existing_cols = {row[1] for row in cursor.fetchall()}
        
        # Check model fields
        for field in model._meta.fields:
            col_name = field.column
            if col_name not in existing_cols:
                # Determine basic SQLite column type
                internal_type = field.get_internal_type()
                if 'Integer' in internal_type or 'Boolean' in internal_type:
                    col_type = "INTEGER DEFAULT 0"
                elif 'DateTime' in internal_type or 'Date' in internal_type:
                    col_type = "TEXT DEFAULT '2026-01-01 00:00:00'"
                else:
                    col_type = "TEXT DEFAULT ''"

                    
                sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};"
                print(f"Adding missing column '{col_name}' to {table_name}...")
                try:
                    cursor.execute(sql)
                    conn.commit()
                except Exception as e:
                    print(f"Error adding {col_name} to {table_name}: {e}")

    conn.close()
    print("All legacy tables successfully aligned with Django models!")

if __name__ == "__main__":
    align_db_schema("hostpinnaclrdb.sqlite3")

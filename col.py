import sqlite3

DB_PATH = "backend/foot_data.db"  # Replace with your database path

def print_column_names(table_name):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"Columns in {table_name}:")
            for column in columns:
                # print(f" - {column[1]} (Type: {column[2]})")
                print(f"'{column[1]}'")
    except Exception as e:
        print(f"Error fetching columns for {table_name}: {e}")

# Check columns for both tables
print_column_names("LeftFootData")
print_column_names("RightFootData")
import sqlite3

# Path to your SQLite database
DATABASE_PATH = 'feedback.db'

def clear_tables():
    try:
        # Connect to the SQLite database
        with sqlite3.connect(DATABASE_PATH) as conn:
            c = conn.cursor()
            
            # List of tables to clear
            tables = ['feedback', 'user']
            
            # Execute deletion queries for each table
            for table in tables:
                c.execute(f"DELETE FROM {table}")
                print(f"Cleared data from {table} table.")
            
            # Commit the changes (not strictly necessary as we're using 'with' context)
            conn.commit()
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    clear_tables()

import sqlite3
class database:
    db_file = "gateway.db"
    def __init__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.initialize_db()

    def initialize_db(self):
        
        # Create a table if it doesn't exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS gateway (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            eui TEXT NOT NULL,
            address TEXT NOT NULL,
            sim_number TEXT,
            UNIQUE(name, eui)
        )
        """)
        self.conn.commit()
    
    # Fetch location from the database
    def fetch_location(self, eui):
        self.cursor.execute("""
        SELECT address FROM gateway
        WHERE eui = ?
        """, (eui,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    # Save location to the database
    def save_to_db(self, name, eui, address, sim_number):
        try:
            self.cursor.execute("""
            INSERT OR IGNORE INTO gateway (name, eui, address, sim_number)
            VALUES (?, ?, ?, ?)
            """, (name, eui, address, sim_number))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving to DB: {e}")

    def gateway_query(self):
        try:
            self.cursor.execute("""
            SELECT * FROM gateway
            """)
            result = self.cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(f"Error retrieving from DB: {e}")

    # Destroyer method to close the connection
    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("Database connection closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

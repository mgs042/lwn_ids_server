import sqlite3
class database:
    db_file = "location_cache.db"
    def __init__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.initialize_db()

    def initialize_db(self):
        
        # Create a table if it doesn't exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS location_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            address TEXT NOT NULL,
            UNIQUE(latitude, longitude)
        )
        """)
        self.conn.commit()
    
    # Fetch location from the database
    def fetch_from_db(self, latitude, longitude):
        self.cursor.execute("""
        SELECT address FROM location_cache
        WHERE latitude = ? AND longitude = ?
        """, (latitude, longitude))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    # Save location to the database
    def save_to_db(self, latitude, longitude, address):
        try:
            self.cursor.execute("""
            INSERT OR IGNORE INTO location_cache (latitude, longitude, address)
            VALUES (?, ?, ?)
            """, (latitude, longitude, address))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving to DB: {e}")

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

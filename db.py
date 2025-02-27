import sqlite3
class gateway_database:
    db_file = "gateway.db"
    def __init__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.initialize_gateway_db()

    def initialize_gateway_db(self):
        
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
    
    # Fetch gateway_location from the database
    def fetch_gateway_location(self, eui):
        self.cursor.execute("""
        SELECT address FROM gateway
        WHERE eui = ?
        """, (eui,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    # Fetch gateway_name from the database
    def fetch_gateway_name(self, eui):
        self.cursor.execute("""
        SELECT name FROM gateway
        WHERE eui = ?
        """, (eui,))
        result = self.cursor.fetchone()
        return result[0] if result else "Unknown"
    
    # Check if Gateway is the database
    def check_gateway_registered(self, eui):
        self.cursor.execute("""
        SELECT name FROM gateway
        WHERE eui = ?
        """, (eui,))
        result = len(self.cursor.fetchall())
        return result
    
    # Save gateway to the database
    def gateway_write(self, name, eui, address, sim_number):
        check=self.check_gateway_registered(eui)
        if check== 0:
            try:
                self.cursor.execute("""
                INSERT OR IGNORE INTO gateway (name, eui, address, sim_number)
                VALUES (?, ?, ?, ?)
                """, (name, eui, address, sim_number))
                self.conn.commit()
                return "Gateway Registered"
            except sqlite3.Error as e:
                print(f"Error saving to DB: {e}")
        else:
            return "Gateway Already Registered"

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
            print("Gateway Database connection closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()



class device_database:
    db_file = "device.db"
    def __init__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.initialize_device_db()

    def initialize_device_db(self):
        
        # Create a table if it doesn't exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS device (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            eui TEXT NOT NULL,
            gw_name TEXT,
            dev_addr TEXT,
            uplink_interval INTEGER NOT NULL,
            UNIQUE(name, eui)
        )
        """)
        self.conn.commit()
    
    
    # Check if Device is the database
    def check_device_registered(self, eui):
        self.cursor.execute("""
        SELECT name FROM device
        WHERE eui = ?
        """, (eui,))
        result = len(self.cursor.fetchall())
        return result
    
    # Check if Device address is the database
    def check_device_addr(self, eui):
        self.cursor.execute("""
        SELECT dev_addr FROM device
        WHERE eui = ?
        """, (eui,))
        result = self.cursor.fetchone()
        return result[0] != "Unknown"


    
    #Set Dev_addr
    def set_dev_addr(self, eui, dev_addr):
        try:
            self.cursor.execute("""
            UPDATE device
            SET dev_addr = ?
            WHERE eui = ?
            """, (dev_addr, eui)) 
            self.conn.commit()  # Commit the changes to the database
        except sqlite3.Error as e:
            print(f"Error saving to DB: {e}")

    # Check if Device gateway is the database
    def check_device_gw(self, eui):
        self.cursor.execute("""
        SELECT gw_name FROM device
        WHERE eui = ?
        """, (eui,))
        result = self.cursor.fetchone()
        return result[0] != "Unknown"


    
    #Set Dev gateway
    def set_dev_gw(self, eui, gw_name):
        try:
            self.cursor.execute("""
            UPDATE device
            SET gw_name = ?
            WHERE eui = ?
            """, (gw_name, eui)) 
            self.conn.commit()  # Commit the changes to the database
        except sqlite3.Error as e:
            print(f"Error saving to DB: {e}")

    #Get Device gateway
    def get_dev_gw(self, eui):
        try:
            self.cursor.execute("""
            SELECT gw_name from device
            WHERE eui = ?
            """, (eui,))
            result = self.cursor.fetchone()
            if result is not None:
                return result[0]
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error retrieving from DB: {e}")

    
    # Save device to the database
    def device_write(self, name, eui, gw_name, dev_addr, uplink_interval):
        check=self.check_device_registered(eui)
        if check == 0:
            try:
                self.cursor.execute("""
                INSERT OR IGNORE INTO device (name, eui, gw_name, dev_addr, uplink_interval)
                VALUES (?, ?, ?, ?, ?)
                """, (name, eui, gw_name, dev_addr, uplink_interval))
                self.conn.commit()
                return "Device Registered"
            except sqlite3.Error as e:
                print(f"Error saving to DB: {e}")
        else:
            return "Device Already Registered"

    def device_query(self):
        try:
            self.cursor.execute("""
            SELECT * FROM device
            """)
            result = self.cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(f"Error retrieving from DB: {e}")
    
    def device_up_int_query(self):
        try:
            self.cursor.execute("""
            SELECT name, eui, uplink_interval FROM device
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
            print("Device Database connection closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

class alert_database:
    db_file = "alert.db"
    def __init__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.initialize_alert_db()

    def initialize_alert_db(self):    
        # Create a table if it doesn't exist
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            eui TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """)
        self.conn.commit()

    # Check if Alert is the database
    def check_alert_registered(self, eui, message):
        self.cursor.execute("""
        SELECT name FROM alert
        WHERE eui = ? AND message = ?
        """, (eui, message,))
        result = self.cursor.fetchone()
        return result is not None

     # Save alert to the database
    def alert_write(self, name, eui, message):
        
        if not self.check_alert_registered(eui, message):
            try:
                self.cursor.execute("""
                INSERT OR IGNORE INTO alert (name, eui, message)
                VALUES (?, ?, ?)
                """, (name, eui, message))
                self.conn.commit()
                return f"Alert Registered - {name} - {message}"
            except sqlite3.Error as e:
                print(f"Error saving to DB: {e}")
        else:
            return f"Alert Already Registered - {name} - {message}"
    
    def query_alert(self, eui = None):
        if eui is not None:
            try:
                self.cursor.execute("""
                SELECT * FROM alert
                WHERE eui = ?
                """, (eui,))
                result = self.cursor.fetchall()
                return result
            except sqlite3.Error as e:
                print(f"Error retrieving from DB: {e}")
        else:
            try:
                self.cursor.execute("""
                SELECT * FROM alert
                """)
                result = self.cursor.fetchall()
                return result
            except sqlite3.Error as e:
                print(f"Error retrieving from DB: {e}")




    def remove_alert(self, eui, message):
        try:
            self.cursor.execute("""
            DELETE FROM alert WHERE eui = ? AND message = ?
            """, (eui, message))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return "Alert Removed"
            else:
                return "Alert Not Found"
        except sqlite3.Error as e:
            print(f"Error removing from DB: {e}")
            return "Error occurred"

        # Destroyer method to close the connection
    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("Alert Database connection closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
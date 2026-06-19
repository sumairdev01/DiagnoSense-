import mysql.connector
import sys

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "port": 3306,
    "connect_timeout": 5
}

def test():
    print("--- MySQL Connection Test ---")
    print(f"Attempting to connect to {DB_CONFIG['host']} on port {DB_CONFIG['port']}...")
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        print("[SUCCESS] Connected to MySQL!")

        cursor = db.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"MySQL Version: {version[0]}")

        cursor.close()
        db.close()
        print("--- Test Completed Successfully ---")
    except Exception as e:
        print("[FAILED] Could not connect to MySQL.")
        print(f"Error details: {e}")
        print("\nPossible solutions:")
        print("1. Check if XAMPP MySQL is running.")
        print("2. Check if port 3306 is correct.")
        print("3. Check if your root user has a password (if yes, update it in DB_CONFIG).")

if __name__ == "__main__":
    test()

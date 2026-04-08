import psycopg2
import sys

try:
    print("Attempting connection with timeout...")
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="polymarket",
        password="polymarket_secret",
        dbname="polymarket_detector",
        connect_timeout=5
    )
    print("Connected!")
    
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM wallets")
    count = cur.fetchone()[0]
    print(f"Wallets in DB: {count}")
    
    cur.close()
    conn.close()
    print("Done!")
except psycopg2.OperationalError as e:
    print(f"Connection error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

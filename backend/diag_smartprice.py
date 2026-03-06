import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

params = {
    'dbname': os.getenv('DB_NAME', 'smartprice'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

print(f"Attempting connection with: {params}")

try:
    conn = psycopg2.connect(**params)
    print("Success!")
    conn.close()
except Exception as e:
    print(f"Error caught: {type(e).__name__}: {e}")
    try:
        # Try to see if we can get more info
        import traceback
        traceback.print_exc()
    except:
        pass

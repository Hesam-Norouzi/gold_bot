import mysql.connector
from decouple import config

def get_db_connection():
    conn = None  # Initialize conn locally
    cur = None   # Initialize cur locally
    try:
        conn = mysql.connector.connect(
            host=config('host'),
            user=config('user'),
            password=config('password'),
            database=config('dbname'),
            port=int(config('port'))
        )
        cur = conn.cursor()
        print("Database connection established.") # Connection message moved inside function

        return conn, cur # Return both connection and cursor

    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL database in get_db_connection: {err}")
        if conn: # Ensure connection is closed even if cursor creation fails
            conn.close()
        return None, None # Return None for both on error

def close_db_connection(conn, cur):
    if conn and conn.is_connected():
        cur.close()
        conn.close()
        print("Database connection closed.")
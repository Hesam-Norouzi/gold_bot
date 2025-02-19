import asyncio
import requests
#from bs4 import BeautifulSoup
import telegram
from decouple import config
import mysql.connector
import json

def get_db_connection():
    conn = None  # Initialize conn locally
    cur = None   # Initialize cur locally
    try:
        conn = mysql.connector.connect(
            host=config('host'),
            user=config('user'),
            password=config('password'),
            database=config('dbname'),
            port=int(config('port')),
            auth_plugin='mysql_native_password'
        )
        cur = conn.cursor()
        print("Database connection established.")  # Connection message moved inside function
        return conn, cur  # Return both connection and cursor

    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL database in get_db_connection: {err}")
        if conn:  # Ensure connection is closed even if cursor creation fails
            conn.close()
        return None, None  # Return None for both on error

def close_db_connection(conn, cur):
    if conn and conn.is_connected():
        cur.close()
        conn.close()
        print("Database connection closed.")



# Configuration
tk = config('token_gold')
url = config('source_api_url')
bot = telegram.Bot(token=tk)
CHANNEL_ID = config("CHANNEL_ID")

async def send_gold_price():

    conn = None  # Initialize conn LOCALLY within send_gold_price
    cur = None   # Initialize cur LOCALLY within send_gold_price
    try:
        conn, cur = get_db_connection()  # Get local conn and cur using the function defined above

        if not conn or not cur:
            print("Failed to get database connection in send_gold_price.")
            return
            
        response = requests.get(url)
        response.raise_for_status()

        if response.status_code == 200:
            data = json.loads(response.text)

            for item in data['gold']:
                if item['name'] == 'مثقال طلا':
                    mesghal = item['price']

                if item['name'] == 'انس جهانی طلا':
                    ounce = item['price']

                if item['name'] == 'گرم طلای 18 عیار':
                    gold18 = item['price']

            for item in data['currency']:
                if item['name'] == 'دلار':
                    dollar = item['price']
                    r2d = 1/dollar/10

            indx = mesghal - (ounce * dollar / 9.5742)

            # Insert data into PostgreSQL
            query = """
                INSERT INTO gold.gold_prices (date, time, gold_price_world, dollar_price, gold_mesghal, gold18_price_iran)
                VALUES (CURRENT_DATE, CURRENT_TIME, %s, %s, %s, %s)
            """
            
            values = (ounce, dollar, mesghal, gold18)
            
            cur.execute(query, values)  # Use the LOCAL 'cur' variable here
            conn.commit()  # Use the LOCAL 'conn' variable here
            print(f"Gold price saved to database.")
                
            message = f"\nانس جهانی: {ounce}\nدلار: {dollar}\nگرم طلای 18 عیار: {gold18}\nریال ایران به دلار: {r2d:.10f}"
            if indx > 500000:
                print("sell")
                await bot.send_message(chat_id=CHANNEL_ID, text=f"🔴Sell 🥇Gold" + message) 
            elif indx < 100000:
                print("buy")
                await bot.send_message(chat_id=CHANNEL_ID, text=f"🟢Buy 🥇Gold" + message) 
            else:
                print("do nothing")
                await bot.send_message(chat_id=CHANNEL_ID, text=f"🕳Do nothing" + message)

    except mysql.connector.Error as e:  # Use 'mysql.connector.Error'
        print(f"MySQL Error in send_gold_price: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Request Error in send_gold_price: {e}")

    except Exception as e:
        print(f"General Error in send_gold_price: {e}")

    finally:
        close_db_connection(conn, cur)  # Use the LOCAL 'conn' and 'cur' and call the function directly

# --- Main Function (from original gold.py) ---
async def main():
    #while True:
    await send_gold_price()
    #await asyncio.sleep(60)  # Check every minute

if __name__ == "__main__":
    asyncio.run(main())
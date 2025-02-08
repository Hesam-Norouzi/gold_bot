import requests
import json
import telegram
from decouple import config
import time
import asyncio
import database

# Configuration
tk = config('token_gold')
url = config('source_api_url')
bot = telegram.Bot(token=tk)
CHANNEL_ID = config("CHANNEL_ID")

async def send_gold_price():
    try:
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

            indx = mesghal - (ounce * dollar / 9.5742)

            # Insert data into PostgreSQL
            database.cur.execute("""
                INSERT INTO gold.gold_prices (date, time, gold_price_world, dollar_price, gold_mesghal, gold18_price_iran)
                VALUES (CURRENT_DATE, CURRENT_TIME, %s, %s, %s, %s)
            """, (ounce, dollar, mesghal, gold18))
            database.conn.commit()

            if indx > 500000:
                print("sell")
                await bot.send_message(chat_id=CHANNEL_ID, text=f"🔴Sell 🥇Gold\nانس جهانی: {ounce}\nدلار: {dollar}\nگرم طلای 18 عیار: {gold18}\n") 
            elif indx < 100000:
                print("buy")
                await bot.send_message(chat_id=CHANNEL_ID, text=f"🟢Buy 🥇Gold\nانس جهانی: {ounce}\nدلار: {dollar}\nگرم طلای 18 عیار: {gold18}\n") 
            else:
                print("do nothing")
                await bot.send_message(chat_id=CHANNEL_ID, text=f"🕳Do nothing\nانس جهانی: {ounce}\nدلار: {dollar}\nگرم طلای 18 عیار: {gold18}\n")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
    except telegram.error.TelegramError as e:
        print(f"Error sending Telegram message: {e}")
    except psycopg2.Error as e:
        print(f"Error interacting with PostgreSQL: {e}")

async def main():
    while True:
        await send_gold_price()
        await asyncio.sleep(1800)

asyncio.run(main())

# Close the database connection when done
database.cur.close()
database.conn.close()

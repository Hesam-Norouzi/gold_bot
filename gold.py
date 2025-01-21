import requests
import json
import telegram
from decouple import config
import time
import asyncio
tk = config('token_gold')

# API url
url = "https://brsapi.ir/FreeTsetmcBourseApi/Api_Free_Gold_Currency.json"
# url = "https://brsapi.ir/FreeTsetmcBourseApi/Api_Free_Gold_Currency_v2.json"

bot = telegram.Bot(token=tk)

CHANNEL_ID = "@goldhelph"

async def send_gold_price():
    try:
        response = requests.get(url)
        response.raise_for_status()

        if response.status_code == 200:
            data = json.loads(response.text)
        #   print(data['currency'])

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

async def main():
    while True:
        await send_gold_price()
        await asyncio.sleep(600)

asyncio.run(main())
import logging
import requests
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'  # <<< OVDJE UBACI SVOJ TELEGRAM TOKEN
API_FOOTBALL_KEY = 'db82cf4e416995c1c91d954b32810510'
API_FOOTBALL_HOST = 'https://v3.football.api-sports.io'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

headers = {
    'x-apisports-key': API_FOOTBALL_KEY
}

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("👋 Zdravo! Dobrodošao u Betting Bot. Pošalji /today da vidiš današnje utakmice!")

@dp.message_handler(commands=['today'])
async def today_matches(message: types.Message):
    from datetime import datetime
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"{API_FOOTBALL_HOST}/fixtures?date={today}&timezone=Europe/Belgrade"

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if 'response' not in data or not data['response']:
            await message.reply("⚠️ Nema mečeva za danas.")
            return

        reply = "⚽ Današnje utakmice:\n\n"
        for match in data['response'][:10]:  # samo prvih 10
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            league = match['league']['name']
            time = match['fixture']['date'][11:16]
            reply += f"🕒 {time} - {home} vs {away} ({league})\n"

        await message.reply(reply)

    except Exception as e:
        await message.reply("❌ Greška pri dohvaćanju mečeva.")
        logging.error(f"API Error: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

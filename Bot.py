import logging
import requests
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime

API_TOKEN = 'OVDE_STAVI_TVOJ_TELEGRAM_TOKEN'  # ZAMENI OVIM TVOJ TOKEN
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
    today = datetime.today().strftime("%Y-%m-%d")
    url = f"{API_FOOTBALL_HOST}/fixtures?date={today}&timezone=Europe/Belgrade"

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if 'response' not in data or not data['response']:
            await message.reply("⚠️ Nema podataka za danas.")
            return

        reply = "📅 Današnje utakmice:\n\n"
        for match in data['response'][:10]:  # ograniči na 10
            time = match['fixture']['time']['elapsed']
            league = match['league']['name']
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            reply += f"⚽ {home} vs {away} ({league})\n"

        await message.reply(reply)

    except Exception as e:
        await message.reply("⚠️ Došlo je do greške pri dohvatanju utakmica.")

@dp.message_handler(commands=['analiza'])
async def analyze_match(message: types.Message):
    try:
        user_input = message.text.replace('/analiza', '').strip().lower()

        url = f"{API_FOOTBALL_HOST}/fixtures?next=100&timezone=Europe/Belgrade"
        response = requests.get(url, headers=headers)
        data = response.json()

        match_found = None

        for match in data['response']:
            home = match['teams']['home']['name'].lower()
            away = match['teams']['away']['name'].lower()
            if user_input in f"{home} vs {away}".lower():
                match_found = match
                break

        if not match_found:
            await message.reply("⚠️ Nije pronađena utakmica sa tim imenom.")
            return

        home = match_found['teams']['home']['name']
        away = match_found['teams']['away']['name']
        time = match_found['fixture']['date']

        # Ovo možeš proširiti sa pravim podacima kad se povežeš na stats endpoint
        analysis = (
            f"📊 *Analiza utakmice:*\n"
            f"• Utakmica: {home} vs {away}\n"
            f"• Vreme: {time}\n\n"
            f"• GG (oba daju gol): Moguće\n"
            f"• Preko 2.5 gola: Verovatno\n"
            f"• GG 1. poluvreme: Nije pouzdano\n"
            f"• 1. poluvreme 1.5+: Potencijalno\n"
        )

        await message.reply(analysis, parse_mode="Markdown")

    except Exception as e:
        await message.reply(f"⚠️ Došlo je do greške u analizi: {e}")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)

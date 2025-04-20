import logging
import requests
import os
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime

API_TOKEN = os.getenv("API_TOKEN")
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
    await message.reply("👋 Zdravo! Dobrodošao u Betting Bot. Pošalji /today da vidiš današnje utakmice ili /analiza ime utakmice za detaljnu analizu.")

@dp.message_handler(commands=['today'])
async def today_matches(message: types.Message):
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"{API_FOOTBALL_HOST}/fixtures?date={today}&timezone=Europe/Belgrade"

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if 'response' not in data or not data['response']:
            await message.reply("⚠️ Nema mečeva za danas.")
            return

        reply = "📅 Današnje utakmice:\n\n"
        for match in data['response'][:10]:  # prikazuje prvih 10
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            league = match['league']['name']
            time = match['fixture']['date'][11:16]
            reply += f"🔘 {time} - {home} vs {away} ({league})\n"

        await message.reply(reply)

    except Exception as e:
        await message.reply("❌ Greška pri dohvaćanju mečeva.")
        logging.error(f"API Error: {e}")

@dp.message_handler(commands=["analiza"])
async def analyze_match(message: types.Message):
    match_name = message.text.replace("/analiza", "").strip().lower()

    today = datetime.today().strftime("%Y-%m-%d")
    url = f"{API_FOOTBALL_HOST}/fixtures?date={today}&timezone=Europe/Belgrade"
    response = requests.get(url, headers=headers)
    data = response.json()

    fixture_id = None
    for fixture in data["response"]:
        home = fixture["teams"]["home"]["name"].lower()
        away = fixture["teams"]["away"]["name"].lower()
        combined_name = f"{home} vs {away}"
        if match_name in combined_name:
            fixture_id = fixture["fixture"]["id"]
            break

    if not fixture_id:
        await message.reply("❌ Nije pronađena utakmica.")
        return

    prediction_url = f"{API_FOOTBALL_HOST}/predictions?fixture={fixture_id}"
    prediction_res = requests.get(prediction_url, headers=headers)
    prediction_data = prediction_res.json()

    try:
        pred = prediction_data["response"][0]["predictions"]

        btts = pred["goals"]["both"]["yes"]
        over25 = pred["goals"]["over_25"]["percentage"]
        winner = pred["winner"]["name"]

        reply = f"📊 *Analiza meča:*\n"
        reply += f"🏟 {match_name.title()}\n"
        reply += f"✅ Predikcija: *{winner}*\n"
        reply += f"💡 GG (oba tima daju gol): *{'Da' if btts > 60 else 'Ne'}*\n"
        reply += f"📈 Over 2.5 golova: *{'Da' if over25 > 60 else 'Ne'}*\n"
        reply += f"\n🧪 Dodatna analiza 1. poluvremena još u izradi."

        await message.reply(reply, parse_mode="Markdown")
    except:
        await message.reply("⚠️ Došlo je do greške u analizi.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

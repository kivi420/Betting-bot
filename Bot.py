import logging
import requests
import os
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime

# Uzimanje vrednosti iz okruženja (Render environment)
API_TOKEN = os.getenv("API_TOKEN")  # TELEGRAM BOT TOKEN
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")  # API-FOOTBALL KEY
API_FOOTBALL_HOST = 'https://v3.football.api-sports.io'

# Logging
logging.basicConfig(level=logging.INFO)

# Bot i dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

headers = {
    'x-apisports-key': API_FOOTBALL_KEY
}


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("👋 Zdravo! Dobrodošao u Betting Bot. Pošalji /today da vidiš današnje utakmice ili /analiza ime_utakmice za analizu.")


@dp.message_handler(commands=["today"])
async def today_matches(message: types.Message):
    today = datetime.today().strftime("%Y-%m-%d")
    url = f"{API_FOOTBALL_HOST}/fixtures?date={today}&timezone=Europe/Belgrade"

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if "response" not in data or not data["response"]:
            await message.reply("⚠️ Nema dostupnih utakmica za danas.")
            return

        fixtures = data["response"]
        reply = "📅 Današnje utakmice:\n"

        for match in fixtures[:10]:  # Ograniči na 10 mečeva
            time = match["fixture"]["time"]["elapsed"]
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            league = match["league"]["name"]
            reply += f"⚽ {home} vs {away} ({league})\n"

        await message.reply(reply)

    except Exception as e:
        await message.reply("❌ Greška pri dohvatanju utakmica.")
        print(e)


@dp.message_handler(lambda message: message.text.startswith("/analiza"))
async def analyze_match(message: types.Message):
    try:
        parts = message.text.split(" ", 1)
        if len(parts) != 2:
            await message.reply("⚠️ Koristi komandu u formatu: /analiza ime tima")
            return

        team_name = parts[1]
        today = datetime.today().strftime("%Y-%m-%d")
        url = f"{API_FOOTBALL_HOST}/fixtures?date={today}&timezone=Europe/Belgrade"

        response = requests.get(url, headers=headers)
        data = response.json()

        if "response" not in data or not data["response"]:
            await message.reply("⚠️ Nema dostupnih utakmica za analizu.")
            return

        fixtures = data["response"]
        for match in fixtures:
            home = match["teams"]["home"]["name"].lower()
            away = match["teams"]["away"]["name"].lower()

            if team_name.lower() in home or team_name.lower() in away:
                home_team = match["teams"]["home"]["name"]
                away_team = match["teams"]["away"]["name"]
                odds = "1.85 - 2.10"  # fiktivne vrednosti
                confidence = "82%"
                kickoff = match["fixture"]["date"][11:16]
                reply = (
                    f"🔎 Analiza meča: {home_team} vs {away_team}\n"
                    f"• Gol-gol (BTTS): Verovatno\n"
                    f"• 2.5+ gola: Da\n"
                    f"• GG 1. poluvreme: Moguće\n"
                    f"• 1.5+ gola 1. poluvreme: Verovatno\n"
                    f"• Kvota: {odds}\n"
                    f"• Procena: {confidence}\n"
                    f"• Početak: {kickoff}h"
                )
                await message.reply(reply)
                return

        await message.reply("⚠️ Nema utakmice sa tim timom danas.")

    except Exception as e:
        await message.reply("❌ Došlo je do greške u analizi.")
        print(e)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

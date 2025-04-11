import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Missing BOT_TOKEN environment variable")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

def get_prediction():
    return {
        "match": "Real Madrid vs Barcelona",
        "prediction": "BTTS (Both Teams To Score)",
        "confidence": 81,
        "odds": 1.92,
        "kickoff": "20:45 CET"
    }

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.reply("Welcome to BetBot! Type /today to get today's prediction.")

@dp.message_handler(commands=['today'])
async def today_cmd(message: types.Message):
    tip = get_prediction()
    response = (
        f"*Today's Pick:*\n"
        f"{tip['match']}\n"
        f"*Prediction:* {tip['prediction']}\n"
        f"*Confidence:* {tip['confidence']}%\n"
        f"*Odds:* {tip['odds']}\n"
        f"*Kickoff:* {tip['kickoff']}"
    )
    await message.answer(response, parse_mode=ParseMode.MARKDOWN)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from db import get_tips_by_age


# Загружаем .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логгинг
logging.basicConfig(level=logging.INFO)

# Правильная инициализация Bot для aiogram 3.7+
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Команда /start
@dp.message(F.text.in_({"👶 0–1 год", "🧒 1–2 года", "👦 3–6 лет", "🎒 7+ лет"}))
async def handle_age_category(message: types.Message):
    age_map = {
        "👶 0–1 год": "baby_0_1",
        "🧒 1–2 года": "baby_1_2",
        "👦 3–6 лет": "baby_3_6",
        "🎒 7+ лет": "baby_7_up"
    }

    age_key = age_map[message.text]
    tips = await get_tips_by_age(age_key)

    if tips:
        response = ""
        for tip in tips:
            response += f"📌 <b>{tip['title']}</b>\n{tip['content']}\n\n"
        await message.answer(response)
    else:
        await message.answer("Пока нет советов для этой категории. Скоро добавим!")


# Всё остальное
@dp.message()
async def fallback_handler(message: types.Message):
    await message.answer("Я тебя не понял 🙈 Нажми кнопку или используй /start.")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


import asyncio
import os
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# === Загрузка .env ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# === Инициализация логов и директорий ===
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),
    ],
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# === Инициализация бота ===
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# === Инициализация базы данных ===
DB_PATH = "db/your_database.db"

if not os.path.exists(DB_PATH):
    logging.error(f"Файл базы данных не найден: {DB_PATH}")
    raise FileNotFoundError(f"Файл базы данных не найден: {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    logging.info("📚 Успешное подключение к базе данных!")
    conn.close()
except sqlite3.Error as e:
    logging.exception(f"Ошибка подключения к базе данных: {e}")
    raise

# === Подключение роутеров ===
from handlers import (
    start, education,
    day_with_timmy, library,
    marathons, tips,
    progress, contact, admin
)

dp.include_routers(
    start.router,
    education.router,
    day_with_timmy.router,
    library.router,
    marathons.router,
    tips.router,
    progress.router,
    contact.router,
    admin.router,
)

# === Подготовка папок для материалов ===
os.makedirs("assets/pdf", exist_ok=True)
os.makedirs("assets/voices", exist_ok=True)
logging.info("📂 Папки для PDF и аудио готовы: assets/pdf, assets/voices.")

# === Основной цикл бота ===
async def main():
    logging.info("🤖 Бот запущен и готов к работе!")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.exception(f"Критическая ошибка при работе бота: {e}")
        # Обязательно сбрасываем логи на диск
        for handler in logging.getLogger().handlers:
            handler.flush()

if __name__ == "__main__":
    asyncio.run(main())

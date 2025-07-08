import asyncio
import os
import logging
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# === Загрузка переменных окружения ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env файле!")

# === Логирование: только главное ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Инициализация бота и диспетчера ===
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# === Проверка базы данных ===
DB_PATH = "db/mamabot_db.db"
if not os.path.exists(DB_PATH):
    logger.error(f"❌ Файл базы данных не найден: {DB_PATH}")
    raise FileNotFoundError(f"Файл базы данных не найден: {DB_PATH}")

try:
    sqlite3.connect(DB_PATH).close()
    logger.info("✅ База данных подключена.")
except:
    raise RuntimeError("❌ Ошибка при подключении к базе данных.")

# === Подготовка папок ===
os.makedirs("pdfs/checklists", exist_ok=True)
os.makedirs("pdfs/guides", exist_ok=True)
os.makedirs("assets/voices", exist_ok=True)
logger.info("📂 Папки созданы: pdfs/checklists, pdfs/guides, assets/voices")

# === Подключение роутеров ===
from handlers import (
    start, education, day_with_timmy,
    library, marathons, tips,
    progress, contact, admin
)

dp.include_routers(
    start.router, education.router, day_with_timmy.router,
    library.router, marathons.router, tips.router,
    progress.router, contact.router, admin.router,
)

# === Основной цикл ===
async def main():
    logger.info("🚀 Бот запущен и готов к работе!")
    await dp.start_polling(bot)
    logger.info("🧹 Поллинг завершён. Бот остановлен.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Бот остановлен вручную.")

# bot.py
import asyncio
import os
import logging
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from aiohttp import web
from handlers.payments import fondy_webhook  # aiohttp handler

# === Загрузка переменных окружения ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_DOMAIN = os.getenv("PUBLIC_DOMAIN", "").rstrip("/")  # например: https://your-app.railway.app
WEBHOOK_PATH = "/fondy/webhook"

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
except Exception as e:
    raise RuntimeError(f"❌ Ошибка при подключении к базе данных: {e}")

# === Подготовка папок ===
os.makedirs("pdfs/checklists", exist_ok=True)
os.makedirs("pdfs/guides", exist_ok=True)
os.makedirs("assets/voices", exist_ok=True)
logger.info("📂 Папки созданы: pdfs/checklists, pdfs/guides, assets/voices")

# === Импорт и подключение всех обработчиков ===
from handlers import (  # noqa: E402
    start,
    education,
    day_with_timmy,
    library,
    marathons,
    tips,
    progress,
    recent,
    contact,
    admin,
    global_routes,
    payments,
)

dp.include_router(global_routes.router)
dp.include_router(start.router)
dp.include_router(education.router)
dp.include_router(day_with_timmy.router)
dp.include_router(library.router)
dp.include_router(marathons.router)
dp.include_router(tips.router)
dp.include_router(progress.router)
dp.include_router(recent.router)
dp.include_router(contact.router)
dp.include_router(admin.router)
dp.include_router(payments.router)

# === AIOHTTP: локальный веб-сервер для колбэков Fondy ===
async def start_web_server() -> web.AppRunner:
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, fondy_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080"))
    )
    await site.start()

    if PUBLIC_DOMAIN:
        logger.info(f"🌐 Fondy webhook listening at: {PUBLIC_DOMAIN}{WEBHOOK_PATH}")
    else:
        logger.info(f"🌐 Fondy webhook listening at: http://localhost:{os.getenv('PORT','8080')}{WEBHOOK_PATH}")

    return runner

# === Основной цикл ===
async def main():
    logger.info("🚀 Бот запускается...")
    runner = await start_web_server()
    try:
        logger.info("🤖 Старт поллинга Telegram...")
        await dp.start_polling(bot)
    finally:
        try:
            await runner.cleanup()
        except Exception:
            pass
        logger.info("🧹 Поллинг завершён. Бот остановлен.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Бот остановлен вручную.")

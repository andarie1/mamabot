import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from aiogram.client.default import DefaultBotProperties

# Создаём папку для логов до инициализации логгера
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),
    ],
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

from handlers import (
    start, education,
    day_with_timmy, library,
    marathons, tips,
    progress, contact
)

dp.include_routers(
    start.router,
    education.router,
    day_with_timmy.router,
    library.router,
    marathons.router,
    tips.router,
    progress.router,
    contact.router
)

os.makedirs("assets/pdf", exist_ok=True)
os.makedirs("assets/voices", exist_ok=True)
logging.info("📂 Папки для PDF и аудио готовы: assets/pdf, assets/voices.")

async def main():
    logging.info("🤖 Бот запущен и готов к работе!")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.exception(f"Критическая ошибка при работе бота: {e}")
        # Важно: сразу сбрасываем логи на диск
        for handler in logging.getLogger().handlers:
            handler.flush()

if __name__ == "__main__":
    asyncio.run(main())

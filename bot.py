import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from aiogram.client.default import DefaultBotProperties

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

from handlers import (
    start, helper, education,
    day_with_timmy, library,
    marathons, tips,
    progress, contact
)

dp.include_routers(
    start.router,
    helper.router,
    education.router,
    day_with_timmy.router,
    library.router,
    marathons.router,
    tips.router,
    progress.router,
    contact.router
)

# Создаём необходимые папки для проекта
os.makedirs("logs", exist_ok=True)
os.makedirs("assets/pdf", exist_ok=True)
os.makedirs("assets/voices", exist_ok=True)
print("📂 Папки для логов, PDF и аудио подготовлены: logs/, assets/pdf, assets/voices.")

async def main():
    logging.info("🤖 Бот запущен и готов к работе!")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.exception(f"Критическая ошибка при работе бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())

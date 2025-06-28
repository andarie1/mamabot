import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

from handlers import (
    start, helper, education, newborn,
    pre_school, materials, pre_kids,
    progress, contact
)

# Подключаем все роутеры
dp.include_routers(
    start.router,
    helper.router,
    education.router,
    newborn.router,
    pre_kids.router,
    pre_school.router,
    materials.router,
    progress.router,
    contact.router
)
import os

# Создаем папку для логов, если её нет
os.makedirs("logs", exist_ok=True)
print("📂 Папка для логов 'logs/' готова — все промпты будут записываться туда.")

# Аналогично можешь сразу подготовить папки для PDF и голосовых файлов:
os.makedirs("assets/pdf", exist_ok=True)
os.makedirs("assets/voices", exist_ok=True)
print("📂 Папки для PDF и аудио созданы: 'assets/pdf', 'assets/voices'.")

async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

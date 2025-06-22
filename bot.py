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
    start, helper, education, early,
    pre_school, materials, pre_kids,
    progress, contact
)

dp.include_routers(
    start.router,
    helper.router,
    education.router,
    early.router,
    pre_kids.router,
    pre_school.router,
    materials.router,
    progress.router,
    contact.router
)

async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

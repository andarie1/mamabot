import asyncio
import logging
import os
import sqlite3

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from article_parser import parse_article_from_url

from db import (
    init_db,
    get_tips_by_age,
    get_pending_articles,
    approve_article,
    delete_article,
    article_to_pdf,
    save_article
)

# === НАСТРОЙКИ ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
init_db()

# === КНОПКИ ВОЗРАСТНЫХ КАТЕГОРИЙ ===
@dp.message(F.text.in_({"👶 0–1 год", "🧒 1–2 года", "👦 3–6 лет", "🎒 7+ лет"}))
async def handle_age_category(message: types.Message):
    age_map = {
        "👶 0–1 год": "baby_0_1",
        "🧒 1–2 года": "baby_1_2",
        "👦 3–6 лет": "baby_3_6",
        "🎒 7+ лет": "baby_7_up"
    }

    age_key = age_map[message.text]
    tips = get_tips_by_age(age_key)

    if tips:
        response = ""
        for tip in tips:
            response += f"📌 <b>{tip['title']}</b>\n{tip['content']}\n\n"
        await message.answer(response)
    else:
        await message.answer("Пока нет советов для этой категории. Скоро добавим!")

# === GET ADMIN ID ===
@dp.message(Command("get_id"))
async def get_admin_id(message: types.Message):
    await message.answer(f"Ваш ID: <code>{message.from_user.id}</code>")

# === ДОБАВЛЕНИЕ СТАТЬИ ПО ССЫЛКЕ ===
@dp.message(Command("add_article"))
async def add_article_url(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет прав для выполнения этой команды.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Используй: /add_article <ссылка>")
        return

    url = parts[1]
    try:
        title = parse_article_from_url(url)
        await message.answer(f"✅ Статья «{title}» добавлена и ждёт утверждения.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении статьи:\n{e}")

# === ПОКАЗ СТАТЕЙ НА УТВЕРЖДЕНИЕ ===
@dp.message(Command("approve_articles"))
async def approve_articles_command(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет прав для выполнения этой команды.")
        return

    pending = get_pending_articles()
    if not pending:
        await message.answer("Нет статей на утверждение.")
        return

    keyboard = [
        [InlineKeyboardButton(text=f"{title} [{article_id}]", callback_data=f"preview_{article_id}")]
        for article_id, title in pending
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.answer("📋 Выбери статью для просмотра:", reply_markup=markup)

# === ПРОСМОТР СТАТЬИ ПЕРЕД РЕШЕНИЕМ ===
@dp.callback_query(F.data.startswith("preview_"))
async def handle_preview(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return

    article_id = int(callback.data.split("_")[1])

    conn = sqlite3.connect("mamabot.db")
    cur = conn.cursor()
    cur.execute("SELECT title, content FROM articles WHERE id = ?", (article_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        await callback.message.edit_text("⚠️ Статья удалена.")
        return

    title, content = row
    preview_text = f"<b>{title}</b>\n\n{content[:1000]}..."
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Утвердить", callback_data=f"approve_{article_id}"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{article_id}")
        ]
    ])
    await callback.message.edit_text(preview_text, reply_markup=keyboard)

# === УТВЕРЖДЕНИЕ СТАТЬИ ===
@dp.callback_query(F.data.startswith("approve_"))
async def handle_approve_callback(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return

    article_id = int(callback.data.split("_")[1])
    article = approve_article(article_id, return_article=True)
    if not article:
        await callback.message.edit_text("⚠️ Не удалось утвердить статью.")
        return

    pdf_path = article_to_pdf(article['title'], article['content'])
    await bot.send_document(callback.from_user.id, types.FSInputFile(pdf_path), caption="✅ Статья утверждена и PDF отправлен.")
    await callback.message.edit_text(f"✅ Статья «{article['title']}» утверждена.")

# === УДАЛЕНИЕ СТАТЬИ ===
@dp.callback_query(F.data.startswith("delete_"))
async def handle_delete_callback(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return

    article_id = int(callback.data.split("_")[1])
    delete_article(article_id)
    await callback.message.edit_text("🗑️ Статья удалена.")

# === Fallback ===
@dp.message()
async def fallback_handler(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👶 0–1 год"), KeyboardButton(text="🧒 1–2 года")],
        [KeyboardButton(text="👦 3–6 лет"), KeyboardButton(text="🎒 7+ лет")]
    ], resize_keyboard=True)
    await message.answer("Я тебя не понял 🙈 Нажми кнопку или используй /start.", reply_markup=kb)


@dp.startup()
async def set_commands(bot: Bot):
    await bot.set_my_commands([
        types.BotCommand(command="add_article", description="Добавить статью по ссылке"),
        types.BotCommand(command="approve_articles", description="Утвердить или удалить статьи"),
    ])
# === ЗАПУСК ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

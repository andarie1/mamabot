from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from services.progress_tracker import (
    get_achievements,
    get_medal_image,
    get_week_progress
)
from services.progress_report import generate_progress_report

router = Router()

# === Главное меню прогресса ===
@router.message(lambda msg: msg.text == "📈 Мой прогресс")
async def show_progress_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏅 Мои медали"), KeyboardButton(text="📊 История заданий")],
            [KeyboardButton(text="📄 Скачать отчёт (PDF)")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "📈 Здесь ты можешь посмотреть достижения и активность своего малыша:",
        reply_markup=keyboard
    )

# === Медали ===
@router.message(lambda msg: msg.text == "🏅 Мои медали")
async def medals_handler(message: types.Message):
    result = get_achievements(message.from_user.id)
    if result:
        for medal in result:
            image_path = get_medal_image(medal["medal_name"])
            if image_path:
                await message.answer_photo(
                    FSInputFile(image_path),
                    caption=f"🏅 {medal['medal_name']}\n{medal['description']}"
                )
            else:
                await message.answer(f"🏅 {medal['medal_name']}:\n{medal['description']}")
    else:
        await message.answer("🏅 Пока нет медалей. Выполняй задания, чтобы заработать первые достижения!")

# === История заданий за неделю ===
@router.message(lambda msg: msg.text == "📊 История заданий")
async def history_handler(message: types.Message):
    last_week = get_week_progress(message.from_user.id)
    if not last_week:
        await message.answer("📭 Тимми по тебе скучает... На этой неделе ты ещё не выполнял задания.")
    else:
        text = "\n".join(last_week)
        await message.answer(f"📘 Твоя активность за последние 7 дней:\n\n{text}")

# === Скачивание PDF-отчёта ===
@router.message(lambda msg: msg.text == "📄 Скачать отчёт (PDF)")
async def download_report_handler(message: types.Message):
    path = generate_progress_report(message.from_user.id, message.from_user.first_name)
    if path:
        await message.answer_document(FSInputFile(path), caption="📄 Вот твой PDF-отчёт!")
    else:
        await message.answer("Нет данных для отчёта 😔")

# === Назад в главное меню ===
@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

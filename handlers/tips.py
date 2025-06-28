from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.start import start_handler
from services.gpt_lesson_generator import generate_ai_lesson
from services.user_profile import get_user_age

router = Router()

@router.message(lambda msg: msg.text == "📖 Советы от профи")
async def show_tips_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💡 Получить совет")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "📖 Советы от экспертов по развитию, воспитанию и уходу за ребёнком.\n\n"
        "Выберите действие 👇",
        reply_markup=keyboard
    )

@router.message(lambda msg: msg.text == "💡 Получить совет")
async def get_tip_handler(message: types.Message):
    await message.answer("⏳ Генерирую полезный совет для вас...")
    try:
        age = get_user_age(message.from_user.id) or 1
        # Используем gpt_lesson_generator с темой "совет", чтобы AI дал релевантный возрасту совет
        tip = generate_ai_lesson(user_id=message.from_user.id, age=age, topic="совет")
        await message.answer(f"🧠 Вот совет от Тимми:\n\n{tip}")
    except Exception as e:
        await message.answer("❌ Не удалось получить совет. Попробуйте позже.")
        raise e

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

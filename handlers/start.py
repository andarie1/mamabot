from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌟 Мой помощник")],
            [KeyboardButton(text="📚 Обучение")],
            [KeyboardButton(text="🍼 0–2 года"), KeyboardButton(text="👶 2–4 года")],
            [KeyboardButton(text="🧒 4–6 лет")],
            [KeyboardButton(text="🎁 Полезности и материалы")],
            [KeyboardButton(text="📈 Мой прогресс"), KeyboardButton(text="📞 Связаться с нами")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Добро пожаловать, мама! 🧸 Я — Тимми. Выбирай, с чего начнём 👇",
        reply_markup=keyboard
    )

@router.message(lambda msg: msg.text == "🎓 Урок на сегодня")
async def lesson_handler(message: types.Message):
    from services.gpt_lesson_generator import generate_ai_lesson
    from services.progress_tracker import update_progress
    from services.voice import generate_voice
    from services.pdf_generator import generate_lesson_pdf
    from aiogram.types import FSInputFile

    age = 5
    level = "начальный"
    task = generate_ai_lesson(user_id=message.from_user.id, age=age, level=level)

    pdf_path = generate_lesson_pdf(message.from_user.first_name, task, f"{message.from_user.id}_lesson.pdf")
    voice_path = generate_voice(task, f"{message.from_user.id}_lesson.mp3")

    await message.answer_document(FSInputFile(pdf_path), caption="📄 Твоё AI-задание от Тимми готово!")
    await message.answer_voice(FSInputFile(voice_path), caption="🎧 А вот голос Тимми — повторяй за ним!")
    update_progress(message.from_user.id, "AI-урок")

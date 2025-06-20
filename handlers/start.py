from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.filters import Command
from services.pdf_generator import generate_lesson_pdf
from services.voice import generate_voice
from services.checklist_generator import generate_checklist_pdf
from services.progress_tracker import update_progress
from services.gpt_lesson_generator import generate_ai_lesson
from services.progress_report import generate_progress_report

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌟 Мой помощник")],
            [KeyboardButton(text="📚 Обучение")],
            [KeyboardButton(text="🍼 До 4 лет"), KeyboardButton(text="👶 4–6 лет")],
            [KeyboardButton(text="🧠 Полезные материалы")],
            [KeyboardButton(text="🎁 Подарки и полезности")],
            [KeyboardButton(text="📈 Мой прогресс"), KeyboardButton(text="📞 Связь с нами")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Добро пожаловать, мама! 🧸 Я — Тимми. Нажми на кнопку, чтобы начать 👇",
        reply_markup=keyboard
    )

@router.message(lambda msg: msg.text == "🎓 Урок на сегодня")
async def lesson_handler(message: types.Message):
    age = 5  # позже можно будет спрашивать у мамы
    level = "начальный"
    task = generate_ai_lesson(user_id=message.from_user.id, age=age, level=level)

    pdf_path = generate_lesson_pdf(message.from_user.first_name, task, f"{message.from_user.id}_lesson.pdf")
    voice_path = generate_voice(task, f"{message.from_user.id}_lesson.mp3")

    await message.answer_document(FSInputFile(pdf_path), caption="📄 Твоё AI-задание от Тимми готово!")
    await message.answer_voice(FSInputFile(voice_path), caption="🎧 А вот голос Тимми — повторяй за ним!")

    update_progress(message.from_user.id, "AI-урок")


@router.message(lambda msg: msg.text == "📄 Чек-лист недели")
async def checklist_handler(message: types.Message):
    tasks = [
        "Сосчитай до 10 вслух",
        "Найди дома 3 красных предмета",
        "Повтори английские слова: sun, cat, tree",
        "Сделай 5 хлопков и 3 прыжка",
        "Обведи круги на бумаге"
    ]
    filename = f"{message.from_user.id}_checklist.pdf"
    pdf_path = generate_checklist_pdf(message.from_user.first_name, tasks, filename)

    await message.answer_document(FSInputFile(pdf_path), caption="📋 Вот твой чек-лист на сегодня!")
    update_progress(message.from_user.id, "Чек-лист недели")


@router.message(Command("age"))
async def ask_age(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="4"), KeyboardButton(text="5"), KeyboardButton(text="6")]
        ],
        resize_keyboard=True
    )
    await message.answer("Сколько лет твоему ребёнку? Выбери 👇", reply_markup=keyboard)


@router.message(lambda msg: msg.text in {"4", "5", "6"})
async def save_age_handler(message: types.Message):
    from services.user_profile import save_user_age
    save_user_age(message.from_user.id, int(message.text))
    await message.answer("Спасибо! Теперь я буду подбирать задания по возрасту 🧠")


@router.message(lambda msg: msg.text == "📈 Отчёт")
async def report_handler(message: types.Message):
    pdf_path = generate_progress_report(message.from_user.id, message.from_user.first_name)
    if pdf_path:
        await message.answer_document(FSInputFile(pdf_path), caption="📊 Вот твой прогресс!")
    else:
        await message.answer("Пока нет данных для отчёта 😔")


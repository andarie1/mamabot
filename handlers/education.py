from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from services.progress_report import generate_progress_report
from services.user_profile import save_user_age
from services.gpt_lesson_generator import generate_ai_lesson
from handlers.start import start_handler

router = Router()

@router.message(lambda msg: msg.text == "📚 Обучение")
async def show_education_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔢 Выбрать возраст ребёнка")],
            [KeyboardButton(text="📷 Развивающие уроки (AI)")],
            [KeyboardButton(text="📈 Прогресс")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("📋 Меню обучения. Выбери, что интересно:", reply_markup=keyboard)


@router.message(lambda msg: msg.text == "🔢 Выбрать возраст ребёнка")
async def choose_age_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="0–6 мес"), KeyboardButton(text="6–12 мес")],
            [KeyboardButton(text="1–2 года"), KeyboardButton(text="2–4 года")],
            [KeyboardButton(text="4–6 лет")],
            [KeyboardButton(text="🔙 Назад в обучение")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите возраст ребёнка кнопкой 👇", reply_markup=keyboard)


@router.message(lambda msg: msg.text in {"0–6 мес", "6–12 мес", "1–2 года", "2–4 года", "4–6 лет"})
async def save_user_age_buttons(message: types.Message):
    mapping = {
        "0–6 мес": 0,
        "6–12 мес": 0,
        "1–2 года": 1,
        "2–4 года": 2,
        "4–6 лет": 4,
    }
    selected_age = mapping.get(message.text)
    save_user_age(message.from_user.id, selected_age)
    await message.answer(f"✅ Возраст сохранён: {message.text}. Теперь задания будут адаптированы! 🧠")


@router.message(lambda msg: msg.text == "📷 Развивающие уроки (AI)")
async def ai_lessons_handler(message: types.Message):
    await message.answer("⏳ Генерирую AI-задание... Подожди немного, Тимми работает 🧠")
    try:
        task = generate_ai_lesson(user_id=message.from_user.id)
        await message.answer(f"🧸 Вот твоё AI-задание:\n\n{task}")
    except Exception as e:
        await message.answer("❌ Упс! Что-то пошло не так с генерацией задания. Попробуй позже.")
        raise e


@router.message(lambda msg: msg.text == "📈 Прогресс")
async def progress_shortcut_handler(message: types.Message):
    pdf_path = generate_progress_report(message.from_user.id, message.from_user.first_name)
    if pdf_path:
        await message.answer_document(FSInputFile(pdf_path), caption="📊 Вот твой прогресс!")
    else:
        await message.answer("Пока нет данных для отчёта 😔")


@router.message(lambda msg: msg.text == "🔙 Назад в обучение")
async def back_to_education_menu(message: types.Message):
    await show_education_menu(message)


@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

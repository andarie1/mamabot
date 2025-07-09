from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

from services.ai_generator import generate_ai_lesson
from services.progress_report import generate_progress_report
from services.user_profile import get_trial_status, get_user_age_range

from handlers.start import start_handler

router = Router()

# === Вспомогательная функция для проверки подписки ===
async def check_trial_and_inform(message: types.Message) -> bool:
    status = get_trial_status(message.from_user.id)
    if status == "almost_over":
        await message.answer(
            "⏳ Ваш пробный период заканчивается завтра! Чтобы и дальше получать задания, откройте подписку 💳."
        )
    if status == "expired":
        await message.answer(
            "🚫 Ваш пробный период завершён. Доступ к обучению закрыт. Чтобы продолжить — активируйте подписку."
        )
        return False
    return True

# === Главное меню обучения ===
@router.message(lambda msg: msg.text == "📚 Обучение")
async def show_education_menu(message: types.Message):
    if not await check_trial_and_inform(message):
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔢 Выбрать возраст ребёнка")],
            [KeyboardButton(text="📘 Темы и уровень сложности")],
            [KeyboardButton(text="📷 Развивающие уроки (AI)")],
            [KeyboardButton(text="📈 Прогресс")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("📋 Меню обучения. Выбери, что интересно:", reply_markup=keyboard)

# === Меню выбора возраста ===
@router.message(lambda msg: msg.text == "🔢 Выбрать возраст ребёнка")
async def choose_age_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="0–2 года"), KeyboardButton(text="2–4 года"), KeyboardButton(text="4–6 лет")],
            [KeyboardButton(text="🔙 Назад в обучение")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите возраст ребёнка кнопкой 👇", reply_markup=keyboard)

# === Подтверждение возраста ===
@router.message(lambda msg: msg.text in {"0–2 года", "2–4 года", "4–6 лет"})
async def confirm_user_age_buttons(message: types.Message):
    from services.user_profile import save_user_age_range
    save_user_age_range(message.from_user.id, message.text)
    await message.answer(f"✅ Возраст выбран: {message.text}. Теперь задания будут адаптированы! 🧠")

# === Меню выбора темы и уровня ===
@router.message(lambda msg: msg.text == "📘 Темы и уровень сложности")
async def choose_topic_and_level(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 Арт"), KeyboardButton(text="🧩 Логика")],
            [KeyboardButton(text="🔤 Английский"), KeyboardButton(text="🎧 Слушаем")],
            [KeyboardButton(text="🎲 Игры"), KeyboardButton(text="🌈 Общие")],
            [KeyboardButton(text="⭐ Лёгкий"), KeyboardButton(text="🔥 Сложный")],
            [KeyboardButton(text="🔙 Назад в обучение")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите тему и уровень сложности:", reply_markup=keyboard)

# === Обработка развивающих уроков ===
@router.message(lambda msg: msg.text == "📷 Развивающие уроки (AI)")
async def ai_lessons_handler(message: types.Message):
    if not await check_trial_and_inform(message):
        return

    from services.user_profile import get_user_age_range
    from aiogram.fsm.context import FSMContext

    age_range = get_user_age_range(message.from_user.id) or "2–4 года"
    # Для MVP по умолчанию: тема "общие", уровень "начальный"
    topic = "общие"
    level = "начальный"

    await message.answer("⏳ Генерирую AI-задание... Подожди немного, Тимми работает 🧠")
    try:
        task = generate_ai_lesson(user_id=message.from_user.id, age_range=age_range, level=level, topic=topic)
        await message.answer(f"🧸 Вот твоё AI-задание:{task}")
    except Exception as e:
        await message.answer("❌ Упс! Что-то пошло не так с генерацией задания. Попробуй позже.")
        raise e

# === Отчёт о прогрессе ===
@router.message(lambda msg: msg.text == "📈 Прогресс")
async def progress_shortcut_handler(message: types.Message):
    pdf_path = generate_progress_report(message.from_user.id, message.from_user.first_name)
    if pdf_path:
        await message.answer_document(FSInputFile(pdf_path), caption="📊 Вот твой прогресс!")
    else:
        await message.answer("Пока нет данных для отчёта 😔")

# === Назад ===
@router.message(lambda msg: msg.text == "🔙 Назад в обучение")
async def back_to_education_menu(message: types.Message):
    await show_education_menu(message)

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

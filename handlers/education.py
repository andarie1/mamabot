from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

from services.ai_generator import generate_ai_lesson
from services.progress_report import generate_progress_report
from services.user_profile import get_trial_status, get_user_age_range, save_user_age_range

from handlers.start import start_handler

router = Router()

AGE_CHOICES = ["0–2 года", "2–4 года", "4–6 лет"]

async def check_trial_and_inform(message: types.Message) -> bool:
    """Проверка пробного периода перед доступом к разделу"""
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

@router.message(lambda msg: msg.text == "📚 Обучение")
async def show_education_menu(message: types.Message):
    if not await check_trial_and_inform(message):
        return

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
        keyboard=[[KeyboardButton(text=age)] for age in AGE_CHOICES] + [[KeyboardButton(text="🔙 Назад в обучение")]],
        resize_keyboard=True
    )
    await message.answer("Выберите возраст ребёнка кнопкой 👇", reply_markup=keyboard)

@router.message(lambda msg: msg.text in AGE_CHOICES)
async def confirm_user_age_buttons(message: types.Message):
    save_user_age_range(message.from_user.id, message.text)
    await message.answer(f"✅ Возраст выбран: {message.text}. Теперь задания будут адаптированы! 🧠")

@router.message(lambda msg: msg.text == "📷 Развивающие уроки (AI)")
async def ai_lessons_handler(message: types.Message):
    if not await check_trial_and_inform(message):
        return

    age_range = get_user_age_range(message.from_user.id) or "2–4 года"

    await message.answer("⏳ Генерирую AI-задание... Подожди немного, Тимми работает 🧠")
    try:
        task = generate_ai_lesson(user_id=message.from_user.id, age_range=age_range)
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

from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from services.ai_generator import generate_ai_lesson
from services.user_profile import (
    get_user_age_range,
    save_user_age_range,
    has_trial_or_full_access,
    get_trial_status
)

router = Router()

AGE_CHOICES = ["0–2 года", "2–4 года", "4–6 лет"]

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

    await message.answer("📋 Меню обучения. Выбери опцию:", reply_markup=get_education_keyboard())

def get_education_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔢 Выбрать возраст ребёнка")],
            [KeyboardButton(text="📷 Развивающие уроки (AI)")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )

# === Меню выбора возраста ===
@router.message(lambda msg: msg.text == "🔢 Выбрать возраст ребёнка")
async def choose_age_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="0–2 года"), KeyboardButton(text="2–4 года"), KeyboardButton(text="4–6 лет")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите возраст ребёнка:", reply_markup=keyboard)

# === Подтверждение возраста ===
@router.message(lambda msg: msg.text in AGE_CHOICES)
async def confirm_user_age(message: types.Message):
    save_user_age_range(message.from_user.id, message.text)
    await message.answer(f"✅ Возраст выбран: {message.text}.", reply_markup=get_education_keyboard())

# === AI-задания ===
@router.message(lambda msg: msg.text == "📷 Развивающие уроки (AI)")
async def ai_lesson_handler(message: types.Message):
    user_id = message.from_user.id
    if not await check_trial_and_inform(message):
        return

    age_range = get_user_age_range(user_id) or "2–4 года"
    topic = "общие"
    level = "начальный"

    await message.answer("⏳ Генерирую AI-задание... Подожди немного, Тимми работает 🧠")
    try:
        task = generate_ai_lesson(user_id=user_id, age_range=age_range, level=level, topic=topic)
        await message.answer(f"🧸 Вот твоё задание:\n{task}")
    except Exception as e:
        await message.answer("❌ Упс! Что-то пошло не так с генерацией задания. Попробуй позже.")
        raise e

# === Назад в главное меню ===
@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)


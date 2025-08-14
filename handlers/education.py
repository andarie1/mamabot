from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from services.ai_generator import generate_ai_lesson
from services.user_profile import (
    get_user_age_range,
    save_user_age_range,
    get_trial_status,
    _read_users_data,   # используем существующий users.json
    USERS_FILE
)

from datetime import datetime
import json

router = Router()

AGE_CHOICES = ["0–2 года", "2–4 года", "4–6 лет"]


# === Суточный лимит (1 генерация/день на модуль «education_ai») ===
def _can_generate_today(user_id: int, module_name: str) -> bool:
    data = _read_users_data()
    key = str(user_id)
    today = datetime.utcnow().date().isoformat()
    field = f"{module_name}_last_gen"

    last = data.get(key, {}).get(field)
    if last == today:
        return False

    data.setdefault(key, {})[field] = today
    USERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return True


# === Мягкая проверка триала (не блокирует доступ) ===
async def check_trial_and_inform(message: types.Message) -> bool:
    status = get_trial_status(message.from_user.id)
    if status == "almost_over":
        await message.answer(
            "⏳ Ваш пробный период заканчивается завтра! Раздел «Обучение» остаётся доступным, подписку включим позже 💳."
        )
    # Даже если trial истёк — «Обучение» сейчас бесплатно; ничего не блокируем.
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


# === AI-задания (1 раз в сутки) ===
@router.message(lambda msg: msg.text == "📷 Развивающие уроки (AI)")
async def ai_lesson_handler(message: types.Message):
    if not await check_trial_and_inform(message):
        return

    user_id = message.from_user.id
    # суточный лимит
    if not _can_generate_today(user_id, "education_ai"):
        await message.answer("⏳ Сегодня задание уже было выдано. Новое — завтра!")
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

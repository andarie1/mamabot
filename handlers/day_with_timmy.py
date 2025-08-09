from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from services.ai_generator import generate_ai_lesson
from services.progress_tracker import update_progress
from services.user_profile import (
    get_user_age_range,
    has_trial_or_full_access,
    get_trial_status
)

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
            "🚫 Пробный период завершён. Доступ к разделу закрыт. Чтобы продолжить — активируйте подписку."
        )
        return False
    return True

# === Главное меню «День с Тимми» ===
@router.message(lambda msg: msg.text == "📅 День с Тимми")
async def day_with_timmy_handler(message: types.Message):
    if not await check_trial_and_inform(message):
        return

    age_range = get_user_age_range(message.from_user.id) or "2–4 года"
    await message.answer("⏳ Генерирую уникальный день для малыша... Подожди немного 🧸")

    try:
        # Генерация по темам (только русская версия с англ. словами)
        task = generate_ai_lesson(message.from_user.id, age_range=age_range, topic="общие")
        ritual = generate_ai_lesson(message.from_user.id, age_range=age_range, topic="ритуал")
        advice = generate_ai_lesson(message.from_user.id, age_range=age_range, topic="совет")

        full_message = (
            f"📅 <b>Твой День с Тимми:</b>\n\n"
            f"📌 <b>Задание:</b>\n{task}\n\n"
            f"🌙 <b>Ритуал:</b>\n{ritual}\n\n"
            f"🧠 <b>Совет:</b>\n{advice}"
        )

        await message.answer(full_message, parse_mode="HTML")
        update_progress(message.from_user.id, "День с Тимми")

    except Exception as e:
        await message.answer("❌ Упс! Не удалось сгенерировать комплект. Попробуй позже.")
        raise e

# === Назад в главное меню ===
@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

from aiogram import Router, types
from services.ai_generator import generate_ai_lesson
from services.progress_tracker import update_progress
from services.user_profile import (
    get_user_age_range,
    get_trial_status
)

# Для суточного лимита
from services.user_profile import _read_users_data, USERS_FILE  # используем существующий JSON
from datetime import datetime
import json

router = Router()


# === Вспомогательная функция: суточный лимит на генерацию ===
def _can_generate_today(user_id: int, module_name: str) -> bool:
    """
    Разрешает 1 генерацию в сутки на модуль.
    Сохраняем дату последней генерации в data/users.json:
      { "<user_id>": { "...": "...", "day_with_timmy_last_gen": "YYYY-MM-DD" } }
    """
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


# === Проверка пробного периода (но раздел бесплатный; оставляем информ-сообщения) ===
async def check_trial_and_inform(message: types.Message) -> bool:
    status = get_trial_status(message.from_user.id)
    if status == "almost_over":
        await message.answer(
            "⏳ Ваш пробный период заканчивается завтра! Продолжайте пользоваться разделом, а подписку включим позже 💳."
        )
    # Раздел сейчас открыт для всех, даже если trial истёк — поэтому не блокируем доступ
    return True


# === Главное действие «День с Тимми» (1 раз в сутки) ===
@router.message(lambda msg: msg.text == "📅 День с Тимми")
async def day_with_timmy_handler(message: types.Message):
    if not await check_trial_and_inform(message):
        return

    # суточный лимит
    if not _can_generate_today(message.from_user.id, "day_with_timmy"):
        await message.answer("⏳ Сегодня ты уже получил свой комплект в разделе «День с Тимми». Попробуй завтра!")
        return

    age_range = get_user_age_range(message.from_user.id) or "2–4 года"
    await message.answer("⏳ Генерирую уникальный день для малыша... Подожди немного 🧸")

    try:
        # Генерим 3 коротких блока (только русская версия; английские слова — в скобках с русским переводом)
        task = generate_ai_lesson(message.from_user.id, age_range=age_range, topic="общие")
        ritual = generate_ai_lesson(message.from_user.id, age_range=age_range, topic="ритуал")
        advice = generate_ai_lesson(message.from_user.id, age_range=age_range, topic="совет")

        full_message = (
            f"📅 <b>Твой День с Тимми</b>\n\n"
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

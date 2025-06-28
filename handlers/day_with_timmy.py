from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from services.user_profile import get_user_age
from services.ai_generator import generate_ai_lesson
from services.progress_tracker import update_progress

router = Router()

@router.message(lambda msg: msg.text == "📅 День с Тимми")
async def day_with_timmy_handler(message: types.Message):
    await message.answer("⏳ Генерирую уникальный комплект для твоего малыша... Подожди немного 🧸")

    try:
        age = get_user_age(message.from_user.id)
        if age is None:
            await message.answer("⚠️ Сначала выбери возраст ребёнка в разделе Обучение → 🔢 По возрастам.")
            return

        # Генерация AI-комплекта
        task = generate_ai_lesson(message.from_user.id, age=age, topic="общие")
        ritual = generate_ai_lesson(message.from_user.id, age=age, topic="ритуал")
        advice = generate_ai_lesson(message.from_user.id, age=age, topic="совет")

        # Отправка результата
        await message.answer(
            f"📅 <b>Твой День с Тимми:</b>\n\n"
            f"📝 <b>Задание:</b>\n{task}\n\n"
            f"💤 <b>Ритуал:</b>\n{ritual}\n\n"
            f"🧠 <b>Совет:</b>\n{advice}",
            parse_mode="HTML"
        )

        update_progress(message.from_user.id, "День с Тимми")
    except Exception as e:
        await message.answer("❌ Упс! Не удалось сгенерировать комплект. Попробуй позже.")
        raise e

from aiogram import Router, types
from handlers.start import start_handler
from services.progress_tracker import get_last_activities

router = Router()

@router.message(lambda msg: msg.text == "🔖 Недавно просмотренные")
async def recent_views_handler(message: types.Message):
    last_activities = get_last_activities(message.from_user.id, limit=3)
    if not last_activities:
        await message.answer("🔖 У тебя пока нет недавних просмотров. Начни с занятий или советов!")
    else:
        text = "🔖 <b>Твои последние активности:</b>\n\n"
        text += "\n".join(f"• {activity}" for activity in last_activities)
        await message.answer(text, parse_mode="HTML")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

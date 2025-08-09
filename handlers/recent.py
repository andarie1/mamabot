from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from services.progress_tracker import get_last_activities

router = Router()


# === Меню "Недавно просмотренные" ===
@router.message(lambda msg: msg.text == "🔖 Недавно просмотренные")
async def recent_views_handler(message: types.Message):
    last_activities = get_last_activities(message.from_user.id, limit=3)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Назад в главное меню")]],
        resize_keyboard=True
    )

    if not last_activities:
        await message.answer(
            "🔖 У тебя пока нет недавних действий. Начни с «Дня с Тимми» или AI-задания!",
            reply_markup=keyboard
        )
    else:
        text = "🔖 <b>Твои недавние действия:</b>\n\n"
        text += "\n".join(f"• {activity}" for activity in last_activities)
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


# === Назад в главное меню ===
@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

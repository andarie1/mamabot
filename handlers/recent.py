from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging
from services.progress_tracker import get_last_activities

router = Router()
logger = logging.getLogger(__name__)

RECENT_BTN = "🔖 Недавно просмотренные"
BACK_BTN = "🔙 Назад в главное меню"

def _back_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BACK_BTN)]],
        resize_keyboard=True
    )

# === Меню "Недавно просмотренные" ===
@router.message(F.text == RECENT_BTN)
async def recent_views_handler(message: types.Message):
    try:
        logger.info("Recent: handler triggered for user %s", message.from_user.id)
        last_activities = get_last_activities(message.from_user.id, limit=3)

        if not last_activities:
            await message.answer(
                "🔖 У тебя пока нет недавних действий. Начни с «Дня с Тимми» или AI‑задания!",
                reply_markup=_back_kb()
            )
            return

        text = "🔖 <b>Твои недавние действия:</b>\n\n" + "\n".join(f"• {a}" for a in last_activities)
        await message.answer(text, reply_markup=_back_kb(), parse_mode="HTML")
    except Exception:
        logger.exception("Recent: error for user %s", message.from_user.id)
        await message.answer("❌ Не удалось загрузить недавние действия. Попробуй позже.", reply_markup=_back_kb())

# === Назад в главное меню ===
@router.message(F.text == BACK_BTN)
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

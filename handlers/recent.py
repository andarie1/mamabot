from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.start import start_handler
from services.progress_tracker import get_progress

router = Router()

@router.message(lambda msg: msg.text == "🔖 Недавно просмотренные")
async def show_recent_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    progress = get_progress(message.from_user.id)
    if not progress:
        await message.answer(
            "🔖 У тебя пока нет недавно просмотренных материалов.\n"
            "Начни с задания или совета, и они появятся здесь!",
            reply_markup=keyboard
        )
    else:
        recent = progress[-3:]
        text = "\n".join([f"— {entry['activity']} ({entry['timestamp']})" for entry in recent])
        await message.answer(
            f"🔖 Последние активности:\n{text}",
            reply_markup=keyboard
        )

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

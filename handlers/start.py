from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(commands=["start"])
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎓 Урок на сегодня")],
            [KeyboardButton(text="📄 Чек-лист недели")],
            [KeyboardButton(text="🎁 Бесплатный подарок")],
        ],
        resize_keyboard=True
    )
    await message.answer(
        f"Привет, мама! 🧸 Я Timmy — твой AI-помощник. Что хочешь сегодня получить?",
        reply_markup=keyboard
    )

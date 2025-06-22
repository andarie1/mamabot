from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(lambda msg: msg.text == "🌟 Мой помощник")
async def show_helper_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📖 Как пользоваться ботом")],
            [KeyboardButton(text="❓ Часто задаваемые вопросы")],
            [KeyboardButton(text="🤝 Поддержка и помощь")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("🌟 Я Тимми, твой AI-помощник! Выбирай, что тебя интересует 👇", reply_markup=keyboard)

@router.message(lambda msg: msg.text == "📖 Как пользоваться ботом")
async def how_to_use_bot(message: types.Message):
    await message.answer("📖 Просто нажимай на кнопки меню, чтобы получать задания, чек-листы и помощь. Я здесь, чтобы сделать обучение весёлым и полезным!")

@router.message(lambda msg: msg.text == "❓ Часто задаваемые вопросы")
async def faq_handler(message: types.Message):
    await message.answer("❓ Часто задаваемые вопросы:\n\n1. Как часто можно проходить задания?\nОтвет: Каждый день!\n\n2. Нужно ли что-то скачивать?\nОтвет: Нет, всё работает прямо в Telegram.\n\n3. Можно ли повторить задания?\nОтвет: Да, просто нажми на нужную кнопку ещё раз.")

@router.message(lambda msg: msg.text == "🤝 Поддержка и помощь")
async def support_handler(message: types.Message):
    await message.answer("🤝 Если у тебя возникли вопросы или трудности — напиши нам, и мы обязательно поможем!")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

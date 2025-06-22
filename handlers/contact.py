from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(lambda msg: msg.text == "📞 Связаться с нами")
async def show_contact_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💬 Задать вопрос")],
            [KeyboardButton(text="💡 Предложить тему")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("📢 Мы всегда на связи! Выберите, чем можем помочь:", reply_markup=keyboard)


@router.message(lambda msg: msg.text == "💬 Задать вопрос")
async def ask_question_handler(message: types.Message):
    await message.answer("💬 Напишите ваш вопрос, и наша команда ответит как можно скорее!")


@router.message(lambda msg: msg.text == "💡 Предложить тему")
async def suggest_topic_handler(message: types.Message):
    await message.answer("💡 У вас есть идея? Напишите её здесь, и мы обязательно рассмотрим!")


@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

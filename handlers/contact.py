from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(lambda msg: msg.text == "📞 Помощь и связь")
async def show_contact_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💬 Задать вопрос")],
            [KeyboardButton(text="💡 Предложить тему")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "📢 Мы всегда на связи!\n"
        "Задайте вопрос или предложите тему для новых материалов 👇",
        reply_markup=keyboard
    )

@router.message(lambda msg: msg.text == "💬 Задать вопрос")
async def ask_question_handler(message: types.Message):
    await message.answer(
        "💬 Напишите свой вопрос сюда — мы постараемся ответить как можно скорее!"
    )

@router.message(lambda msg: msg.text == "💡 Предложить тему")
async def suggest_topic_handler(message: types.Message):
    await message.answer(
        "💡 Напишите, какую тему, марафон или чек-лист вы хотели бы увидеть — нам важно ваше мнение!"
    )

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

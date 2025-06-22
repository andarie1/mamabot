from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(lambda msg: msg.text == "\ud83d\udcde Связаться с нами")
async def show_contact_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="\ud83d\udcac Задать вопрос")],
            [KeyboardButton(text="\ud83d\udca1 Предложить тему")],
            [KeyboardButton(text="\ud83d\udd19 \u041d\u0430\u0437\u0430\u0434 \u0432 \u0433\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e")]
        ],
        resize_keyboard=True
    )
    await message.answer("\ud83d\udce2 Мы всегда на связи! Выберите, чем можем помочь:", reply_markup=keyboard)


@router.message(lambda msg: msg.text == "\ud83d\udcac Задать вопрос")
async def ask_question_handler(message: types.Message):
    await message.answer("\ud83d\udcac Напишите ваш вопрос, и наша команда ответит как можно скорее!")


@router.message(lambda msg: msg.text == "\ud83d\udca1 Предложить тему")
async def suggest_topic_handler(message: types.Message):
    await message.answer("\ud83d\udca1 У вас есть идея? Напишите её здесь, и мы обязательно рассмотрим!")


@router.message(lambda msg: msg.text == "\ud83d\udd19 \u041d\u0430\u0437\u0430\u0434 \u0432 \u0433\u043b\u0430\u0432\u043d\u043e\u0435 \u043c\u0435\u043d\u044e")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

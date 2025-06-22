from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(lambda msg: msg.text == "🧒 4–6 лет")
async def show_pre_school_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔤 Английский: учим играя")],
            [KeyboardButton(text="🧠 Развиваем логику")],
            [KeyboardButton(text="🎨 Арт и креатив")],
            [KeyboardButton(text="🎧 Слушаем и реагируем")],
            [KeyboardButton(text="🧘 Игры с правилами")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("🧒 Направления для детей 4–6 лет. Выбирай, что интересно:", reply_markup=keyboard)


@router.message(lambda msg: msg.text == "🔤 Английский: учим играя")
async def english_game_handler(message: types.Message):
    await message.answer("🔤 Учим английские слова с играми: найди предмет и назови его!")


@router.message(lambda msg: msg.text == "🧠 Развиваем логику")
async def logic_handler(message: types.Message):
    await message.answer("🧠 Логическая задачка: что лишнее — яблоко, банан, стул?")


@router.message(lambda msg: msg.text == "🎨 Арт и креатив")
async def art_handler(message: types.Message):
    await message.answer("🎨 Нарисуй семью на листе бумаги. Можешь использовать наклейки!")


@router.message(lambda msg: msg.text == "🎧 Слушаем и реагируем")
async def listen_handler(message: types.Message):
    await message.answer("🎧 Внимание! Я скажу слово, а ты прыгни, если оно про еду!")


@router.message(lambda msg: msg.text == "🧘 Игры с правилами")
async def rules_game_handler(message: types.Message):
    await message.answer("🧘 Играем по правилам: 'красный — стой, зелёный — иди'. Готов?")


@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

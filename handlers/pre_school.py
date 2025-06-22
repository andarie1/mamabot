from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(lambda msg: msg.text == "👶 4–6 лет")
async def show_pre_school_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇬🇧 Английский: учим играя")],
            [KeyboardButton(text="🧠 Развиваем логику")],
            [KeyboardButton(text="🎨 Арт и креатив")],
            [KeyboardButton(text="🎧 Слушаем и реагируем")],
            [KeyboardButton(text="🎲 Игры с правилами")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("👶 Развивающие задания для 4–6 лет:", reply_markup=keyboard)

@router.message(lambda msg: msg.text == "🇬🇧 Английский: учим играя")
async def english_game_handler(message: types.Message):
    await message.answer("🇬🇧 Повторяй за Тимми: sun, dog, apple!")

@router.message(lambda msg: msg.text == "🧠 Развиваем логику")
async def logic_handler(message: types.Message):
    await message.answer("🧠 Найди, что лишнее: мяч, мяч, ложка.")

@router.message(lambda msg: msg.text == "🎨 Арт и креатив")
async def creativity_handler(message: types.Message):
    await message.answer("🎨 Нарисуй домик и назови его части!")

@router.message(lambda msg: msg.text == "🎧 Слушаем и реагируем")
async def listen_handler(message: types.Message):
    await message.answer("🎧 Скоро появится задание с аудио от Тимми!")

@router.message(lambda msg: msg.text == "🎲 Игры с правилами")
async def rule_games_handler(message: types.Message):
    await message.answer("🎲 Игра: сделай 2 хлопка, если услышишь слово «кот».")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

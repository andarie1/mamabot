from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(lambda msg: msg.text == "👶 2–4 года")
async def show_early_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Простые задания")],
            [KeyboardButton(text="🔁 Повторение слов")],
            [KeyboardButton(text="🏃 Подвижные игры")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("👶 Задания для детей 2–4 лет:", reply_markup=keyboard)

@router.message(lambda msg: msg.text == "✅ Простые задания")
async def simple_tasks_handler(message: types.Message):
    await message.answer("✅ Попроси малыша положить мяч в коробку и похвали его за выполнение!")

@router.message(lambda msg: msg.text == "🔁 Повторение слов")
async def repeat_words_handler(message: types.Message):
    await message.answer("🔁 Повторяй за Тимми: мама, котик, шарик. Молодец!")

@router.message(lambda msg: msg.text == "🏃 Подвижные игры")
async def active_games_handler(message: types.Message):
    await message.answer("🏃 Прыгай как зайчик! А теперь покрутись как волчок!")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

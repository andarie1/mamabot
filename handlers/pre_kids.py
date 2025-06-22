from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(lambda msg: msg.text == "🧒 2–4 года")
async def show_pre_kids_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧩 Простые задания")],
            [KeyboardButton(text="🔁 Повторение слов")],
            [KeyboardButton(text="🤸‍♂️ Подвижные игры")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("🧒 Выбери задание для возраста 2–4 года:", reply_markup=keyboard)

@router.message(lambda msg: msg.text == "🧩 Простые задания")
async def simple_tasks_handler(message: types.Message):
    await message.answer("🧩 Задание: найди дома предмет, который можно катать.")

@router.message(lambda msg: msg.text == "🔁 Повторение слов")
async def repeat_words_handler(message: types.Message):
    await message.answer("🔁 Повторяй за мной: ball, car, baby!")

@router.message(lambda msg: msg.text == "🤸‍♂️ Подвижные игры")
async def movement_games_handler(message: types.Message):
    await message.answer("🤸‍♂️ Прыгни 3 раза и покажи маме!")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

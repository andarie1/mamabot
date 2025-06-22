from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(lambda msg: msg.text == "🍼 0–2 года")
async def show_pre_kids_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇬🇧 Английский для малышей")],
            [KeyboardButton(text="🎯 Логика и внимание")],
            [KeyboardButton(text="🎨 Арт и креатив")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("🍼 Направления для детей 0–2 лет:", reply_markup=keyboard)

@router.message(lambda msg: msg.text == "🇬🇧 Английский для малышей")
async def english_for_babies(message: types.Message):
    await message.answer("🇬🇧 Слушаем простые слова: mama, ball, dog. Повторяй вместе с Тимми!")

@router.message(lambda msg: msg.text == "🎯 Логика и внимание")
async def logic_for_babies(message: types.Message):
    await message.answer("🎯 Игра: найди такой же предмет, как на картинке! (в разработке)")

@router.message(lambda msg: msg.text == "🎨 Арт и креатив")
async def art_for_babies(message: types.Message):
    await message.answer("🎨 Нарисуй пальчиками солнышко на тарелке с краской! Весело и полезно ☀️")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(lambda msg: msg.text == "👶 0–2 года")
async def show_early_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Английский для малышей")],
            [KeyboardButton(text="🎯 Логика и внимание")],
            [KeyboardButton(text="🎨 Арт и креатив")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("👶 Направления для малышей 0–2 лет:", reply_markup=keyboard)

@router.message(lambda msg: msg.text == "📘 Английский для малышей")
async def baby_english_handler(message: types.Message):
    await message.answer("📘 Начинаем с простых слов: мама, папа, кот!")

@router.message(lambda msg: msg.text == "🎯 Логика и внимание")
async def baby_logic_handler(message: types.Message):
    await message.answer("🎯 Поиграй с малышом в игру: найди предмет по цвету!")

@router.message(lambda msg: msg.text == "🎨 Арт и креатив")
async def baby_art_handler(message: types.Message):
    await message.answer("🎨 Рисуем пальчиком по крупе или песку!")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

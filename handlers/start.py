from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 День с Тимми")],
            [KeyboardButton(text="📚 Обучение"), KeyboardButton(text="📖 Советы от профи")],
            [KeyboardButton(text="🚀 Марафоны и интенсивы"), KeyboardButton(text="📚 Библиотека PDF")],
            [KeyboardButton(text="📈 Мой прогресс"), KeyboardButton(text="📞 Помощь и связь")],
            [KeyboardButton(text="🔖 Недавно просмотренные")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Добро пожаловать в мир Тимми! 🧸\n"
        "Я помогу тебе развивать малыша и сделаю это весело и полезно.\n"
        "Выбирай раздел 👇",
        reply_markup=keyboard
    )

@router.message(lambda msg: msg.text.isdigit())
async def save_user_age_handler(message: types.Message):
    from services.user_profile import save_user_age
    age = int(message.text)
    if 0 <= age <= 6:
        save_user_age(message.from_user.id, age)
        await message.answer(f"✅ Возраст сохранён: {age} лет. Теперь задания будут адаптированы! 🧠")
    else:
        await message.answer("❌ Введите целое число от 0 до 6 — в годах. Например: 3")

@router.message(lambda msg: msg.text == "📅 День с Тимми")
async def day_with_timmy_handler(message: types.Message):
    await message.answer("⏳ Генерирую уникальный набор: задание, ритуал и совет…")
    # Здесь будет вызов генерации через AI
    # Временно - заглушка:
    await message.answer("📅 День с Тимми готов! 🧸\n\n"
                         "📚 Задание: Найди предмет красного цвета.\n"
                         "💤 Ритуал: Перед сном обними игрушку и скажи: «Спасибо, день!»\n"
                         "🧠 Совет: Объясняй всё спокойным голосом — малыш чувствует твои эмоции.")


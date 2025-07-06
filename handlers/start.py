from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.filters import Command
from services.user_profile import save_trial_start, get_trial_status

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    try:
        gif = FSInputFile("assets/gifs/cute_raccoon_greets_2.png")
        await message.answer_photo(
            photo=gif,
            caption=(
                "Добро пожаловать в мир Тимми! 🦝\n"
                "Я помогу тебе развивать малыша и сделаю это весело и полезно."
            )
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке приветствия: {e}")

    # Сохраняем начало пробного периода при первом входе
    save_trial_start(message.from_user.id)

    # Проверка состояния пробного периода и пуш-уведомление
    status = get_trial_status(message.from_user.id)
    if status == "almost_over":
        await message.answer(
            "⏳ Ваш пробный период заканчивается завтра! Чтобы продолжить пользоваться всеми возможностями, оформите подписку 💳."
        )
    elif status == "expired":
        await message.answer(
            "🚫 Ваш пробный период завершён. Чтобы снова получить доступ к полному функционалу, пожалуйста, оформите подписку."
        )
        return  # Блокируем доступ, если пробный закончился

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 День с Тимми")],
            [KeyboardButton(text="📚 Обучение"), KeyboardButton(text="💡 Советы от профи")],
            [KeyboardButton(text="🚀 Марафоны и интенсивы"), KeyboardButton(text="📖 Библиотека PDF")],
            [KeyboardButton(text="📈 Мой прогресс"), KeyboardButton(text="📞 Помощь и связь")],
            [KeyboardButton(text="🔖 Недавно просмотренные")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Выбирай раздел 👇",
        reply_markup=keyboard
    )


    # 2) Отправляем клавиатуру с приветственным сообщением
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 День с Тимми")],
            [KeyboardButton(text="📚 Обучение"), KeyboardButton(text="💡 Советы от профи")],
            [KeyboardButton(text="🚀 Марафоны и интенсивы"), KeyboardButton(text="📖 Библиотека PDF")],
            [KeyboardButton(text="📈 Мой прогресс"), KeyboardButton(text="📞 Помощь и связь")],
            [KeyboardButton(text="🔖 Недавно просмотренные")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Выбирай раздел 👇",
        reply_markup=keyboard
    )

@router.message(lambda msg: msg.text.isdigit())
async def save_user_age_handler(message: types.Message):
    from services.user_profile import save_user_age_range
    age = int(message.text)
    if 0 <= age <= 6:
        save_user_age_range(message.from_user.id, age)
        await message.answer(f"✅ Возраст сохранён: {age} лет. Теперь задания будут адаптированы! 🦝")
    else:
        await message.answer("❌ Введите целое число от 0 до 6 — в годах. Например: 3")

@router.message(lambda msg: msg.text == "📅 День с Тимми")
async def day_with_timmy_handler(message: types.Message):
    await message.answer("⏳ Генерирую уникальный набор: задание, ритуал и совет…")
    # Временно - заглушка:
    await message.answer(
        "📅 День с Тимми готов! 🦝\n\n"
        "📚 Задание: Найди предмет красного цвета.\n"
        "💤 Ритуал: Перед сном обними игрушку и скажи: «Спасибо, день!»\n"
        "🧠 Совет: Объясняй всё спокойным голосом — малыш чувствует твои эмоции."
    )

from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.filters import Command

from services.user_profile import save_trial_start, get_trial_status, ADMIN_IDS

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    # Приветственная картинка (не критично, если файла нет)
    try:
        gif = FSInputFile("assets/gifs/cute_raccoon_greets_2.png")
        await message.answer_photo(
            photo=gif,
            caption=(
                "Добро пожаловать в мир Тимми! 🦝\n"
                "Я помогу тебе развивать малыша и сделаю это весело и полезно."
            )
        )
    except Exception:
        # Тихо игнорируем, чтобы не ломать поток
        pass

    # Запускаем (фиксируем) старт триала при первом заходе
    save_trial_start(message.from_user.id)

    # Мягкое уведомление о триале (меню показываем ВСЕГДА)
    status = get_trial_status(message.from_user.id)
    is_admin = message.from_user.id in ADMIN_IDS

    if status == "almost_over" and not is_admin:
        await message.answer(
            "⏳ Ваш пробный период заканчивается завтра. "
            "Бесплатные разделы остаются доступными. "
            "Платные (📖 Библиотека, 🚀 Марафоны) — по подписке."
        )
    elif status == "expired" and not is_admin:
        await message.answer(
            "ℹ️ Пробный период завершён. "
            "Бесплатные разделы доступны без ограничений. "
            "Платные (📖 Библиотека, 🚀 Марафоны) пока закрыты."
        )

    # Главное меню (показываем независимо от статуса)
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
    await message.answer("Выбирай раздел 👇", reply_markup=keyboard)

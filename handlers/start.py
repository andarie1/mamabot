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

    save_trial_start(message.from_user.id)
    status = get_trial_status(message.from_user.id)

    if status == "almost_over":
        await message.answer(
            "⏳ Ваш пробный период заканчивается завтра! Чтобы продолжить пользоваться всеми возможностями, оформите подписку 💳."
        )
    elif status == "expired":
        await message.answer(
            "🚫 Ваш пробный период завершён. Чтобы снова получить доступ к полному функционалу, пожалуйста, оформите подписку."
        )
        return

    await message.answer("Выбирай раздел 👇", reply_markup=get_main_keyboard())

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 День с Тимми")],
            [KeyboardButton(text="📚 Обучение"), KeyboardButton(text="💡 Советы от профи")],
            [KeyboardButton(text="🚀 Марафоны и интенсивы"), KeyboardButton(text="📖 Библиотека PDF")],
            [KeyboardButton(text="📈 Мой прогресс"), KeyboardButton(text="📞 Помощь и связь")],
            [KeyboardButton(text="🔖 Недавно просмотренные")]
        ],
        resize_keyboard=True
    )

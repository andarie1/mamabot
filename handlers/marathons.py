from aiogram import Router, types, F
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton
)
from services.user_profile import (
    has_full_access,
    get_user_age_range,
    save_user_age_range
)

router = Router()

AGE_CHOICES = ["0–2 года", "2–4 года", "4–6 лет"]

# === Клавиатура выбора возраста ===
def get_age_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=age)] for age in AGE_CHOICES],
        resize_keyboard=True
    )

# === Главное меню марафонов ===
@router.message(F.text == "🚀 Марафоны и интенсивы")
async def show_marathons_menu(message: types.Message):
    user_id = message.from_user.id
    age = get_user_age_range(user_id)
    if not age:
        await message.answer(
            "👶 Пожалуйста, выберите возраст ребёнка, чтобы подобрать материалы:",
            reply_markup=get_age_keyboard()
        )
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 Подготовка к садику"), KeyboardButton(text="✏ Подготовка к школе")],
            [KeyboardButton(text="🔓 Открыть доступ"), KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "🚀 Здесь собраны специальные программы и интенсивы.\n\n"
        "Чтобы открыть доступ, активируй подписку.\n"
        "Выбери интересующий марафон или нажми «🔓 Открыть доступ»:",
        reply_markup=keyboard
    )

# === Установка возраста через кнопку ===
@router.message(F.text.in_(AGE_CHOICES))
async def handle_age_selection(message: types.Message):
    save_user_age_range(message.from_user.id, message.text)
    await message.answer("✅ Возраст сохранён! Теперь ты можешь пользоваться платными разделами.")
    await show_marathons_menu(message)

# === Обработка марафонов ===
@router.message(F.text.in_({"🎯 Подготовка к садику", "✏ Подготовка к школе"}))
async def marathon_content_handler(message: types.Message):
    user_id = message.from_user.id
    if has_full_access(user_id):
        await message.answer(
            f"✅ Доступ открыт! 🎉\n\n"
            f"Начинай марафон: {message.text}.\n"
            f"Твои задания скоро будут доступны здесь!"
        )
    else:
        await message.answer(
            "🔒 Этот марафон доступен только после оплаты.\n\n"
            "Нажми «🔓 Открыть доступ», чтобы перейти к оплате."
        )

# === Открыть доступ ===
@router.message(F.text == "🔓 Открыть доступ")
async def open_access_handler(message: types.Message):
    await message.answer(
        "💳 Чтобы получить полный доступ, перейди по ссылке для оплаты:\n\n"
        "<b>[Ваша ссылка на оплату]</b>\n\n"
        "После успешной оплаты доступ откроется автоматически! 🎉",
        parse_mode="HTML"
    )

# === Назад в главное меню ===
@router.message(F.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

from aiogram import Router, types, F
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, FSInputFile
)
from handlers.start import start_handler
from services.user_profile import (
    has_active_subscription,
    get_user_age_range,
    save_user_age_range,
    ADMIN_IDS
)
import os

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
        await message.answer("👶 Пожалуйста, выберите возраст ребёнка, чтобы подобрать материалы:", reply_markup=get_age_keyboard())
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
        "Чтобы открыть доступ, оплатите подписку.\n"
        "Выберите интересующий марафон или нажмите « \xab🔓 Открыть доступ»\xbb:",
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
    if user_id in ADMIN_IDS or has_active_subscription(user_id):
        await message.answer(
            f"✅ Доступ открыт! 🎉\n\n"
            f"Начинай марафон: {message.text}.\n"
            f"Твои задания скоро будут доступны здесь!"
        )
    else:
        await message.answer(
            "🔒 Этот марафон доступен только после оплаты.\n\n"
            "Нажмите « \xab🔓 Открыть доступ»\xbb, чтобы перейти к оплате."
        )

# === Открыть доступ ===
@router.message(F.text == "🔓 Открыть доступ")
async def open_access_handler(message: types.Message):
    await message.answer(
        "💳 Чтобы получить полный доступ к марафонам и интенсивам, перейдите по ссылке для оплаты:\n\n"
        "<b>[Ваша ссылка на оплату]</b>\n\n"
        "После успешной оплаты доступ будет открыт автоматически! 🎉",
        parse_mode="HTML"
    )

# === Назад в главное меню ===
@router.message(F.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

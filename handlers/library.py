from aiogram import Router, types, F
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile, CallbackQuery
)
from handlers.start import start_handler
from services.user_profile import (
    has_active_subscription,
    get_user_age_range,
    save_user_age_range,
    ADMIN_IDS
)
import sqlite3
import os

router = Router()

AGE_CHOICES = ["0–2 года", "2–4 года", "4–6 лет"]

# === Клавиатура выбора возраста ===
def get_age_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=age)] for age in AGE_CHOICES],
        resize_keyboard=True
    )

# === Главное меню библиотеки ===
@router.message(F.text == "📖 Библиотека PDF")
async def show_library_menu(message: types.Message):
    user_id = message.from_user.id
    age = get_user_age_range(user_id)
    if not age:
        await message.answer("👶 Пожалуйста, выберите возраст ребёнка, чтобы подобрать материалы:", reply_markup=get_age_keyboard())
        return

    if not has_active_subscription(user_id) and user_id not in ADMIN_IDS:
        await message.answer(
            "🚫 Доступ к библиотеке закрыт.\n"
            "Чтобы открыть PDF-чек-листы и гиды, активируйте подписку 💳."
        )
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Чек-листы"), KeyboardButton(text="📘 Гиды")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("📖 Добро пожаловать в библиотеку Тимми!\n\nВыберите раздел:", reply_markup=keyboard)

# === Обработка выбора возраста ===
@router.message(F.text.in_(AGE_CHOICES))
async def handle_age_selection(message: types.Message):
    save_user_age_range(message.from_user.id, message.text)
    await message.answer("✅ Возраст сохранён! Теперь ты можешь пользоваться платными разделами.")
    await show_library_menu(message)

# === Получение записей из БД с учётом возраста ===
def get_library_items_by_type_and_age(item_type: str, age_range: str):
    conn = sqlite3.connect("db/mamabot_db.db")
    cursor = conn.cursor()
    if item_type == "checklist":
        path_filter = "checklists"
    else:
        path_filter = "guides"
    cursor.execute(
        """
        SELECT id, title, description FROM library
        WHERE file_path LIKE ? AND (age_range = ? OR age_range LIKE ?)
        """,
        (f"%{path_filter}%", age_range, f"%{age_range}%")
    )
    items = cursor.fetchall()
    conn.close()
    return items

# === Чек-листы ===
@router.message(F.text == "📋 Чек-листы")
async def show_checklists(message: types.Message):
    user_id = message.from_user.id
    age_range = get_user_age_range(user_id)
    if not has_active_subscription(user_id) and user_id not in ADMIN_IDS:
        await message.answer("🚫 У вас нет подписки.")
        return

    items = get_library_items_by_type_and_age("checklist", age_range)
    if not items:
        await message.answer("Пока нет доступных чек-листов для выбранного возраста.")
        return

    for item_id, title, description in items:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Скачать", callback_data=f"download_{item_id}")]
        ])
        await message.answer(f"<b>{title}</b>\n{description}", reply_markup=keyboard, parse_mode="HTML")

# === Гиды ===
@router.message(F.text == "📘 Гиды")
async def show_guides(message: types.Message):
    user_id = message.from_user.id
    age_range = get_user_age_range(user_id)
    if not has_active_subscription(user_id) and user_id not in ADMIN_IDS:
        await message.answer("🚫 У вас нет подписки.")
        return

    items = get_library_items_by_type_and_age("guide", age_range)
    if not items:
        await message.answer("Пока нет доступных гидов для выбранного возраста.")
        return

    for item_id, title, description in items:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Скачать", callback_data=f"download_{item_id}")]
        ])
        await message.answer(f"<b>{title}</b>\n{description}", reply_markup=keyboard, parse_mode="HTML")

# === Загрузка PDF по кнопке ===
@router.callback_query(F.data.startswith("download_"))
async def send_selected_pdf(callback: CallbackQuery):
    item_id = int(callback.data.replace("download_", ""))
    conn = sqlite3.connect("db/mamabot_db.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, file_path FROM library WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        title, file_path = result
        if os.path.exists(file_path):
            await callback.message.answer_document(
                FSInputFile(file_path),
                caption=f"📄 {title}"
            )
        else:
            await callback.message.answer("❌ Файл не найден на сервере.")
    else:
        await callback.message.answer("❌ Файл не найден в базе данных.")
    await callback.answer()

# === Назад в главное меню ===
@router.message(F.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

from aiogram import Router, types, F
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, FSInputFile
)
from services.user_profile import (
    has_full_access,
    get_user_age_range,
    save_user_age_range
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
        await message.answer(
            "👶 Пожалуйста, выберите возраст ребёнка, чтобы подобрать материалы:",
            reply_markup=get_age_keyboard()
        )
        return

    if not has_full_access(user_id):
        await message.answer(
            "❌ Доступ к библиотеке закрыт.\n"
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
    await message.answer(
        "📖 Добро пожаловать в библиотеку Тимми!\n\nВыберите раздел:",
        reply_markup=keyboard
    )

# === Обработка выбора возраста ===
@router.message(F.text.in_(AGE_CHOICES))
async def handle_age_selection(message: types.Message):
    save_user_age_range(message.from_user.id, message.text.strip())
    await message.answer("✅ Возраст сохранён! Теперь ты можешь пользоваться платными разделами.")
    await show_library_menu(message)

# === Получение записей из БД с учётом возраста ===
def get_library_items_by_type_and_age(item_type: str, age_range: str):
    conn = sqlite3.connect("db/mamabot_db.db")
    cursor = conn.cursor()

    path_filter = "checklists" if item_type == "checklist" else "guides"
    age_range = age_range.strip()

    cursor.execute("""
        SELECT age_from, age_to FROM age_ranges WHERE name = ?
    """, (age_range,))
    age_data = cursor.fetchone()

    if not age_data:
        conn.close()
        return []

    age_from, age_to = age_data

    cursor.execute("""
        SELECT l.id, l.title, l.description
        FROM library l
        JOIN age_bindings ab ON ab.content_type = 'library' AND ab.content_id = l.id
        JOIN age_ranges ar ON ar.id = ab.age_id
        WHERE ar.age_from <= ? AND ar.age_to >= ? AND l.file_path LIKE ?
        GROUP BY l.id
    """, (age_to, age_from, f"%{path_filter}%"))

    items = cursor.fetchall()
    conn.close()
    return items

# === Отображение чек-листов ===
@router.message(F.text == "📋 Чек-листы")
async def show_checklists(message: types.Message):
    user_id = message.from_user.id
    age_range = get_user_age_range(user_id).strip()

    if not has_full_access(user_id):
        await message.answer("❌ У вас нет доступа к чек-листам.")
        return

    items = get_library_items_by_type_and_age("checklist", age_range)
    if not items:
        await message.answer("Пока нет доступных чек-листов для выбранного возраста.")
        return

    for item_id, title, description in items:
        preview = description[:200] + "..." if description else "Нет описания."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📄 Читать", callback_data=f"preview_{item_id}"),
                InlineKeyboardButton(text="⬇️ Скачать", callback_data=f"download_{item_id}")
            ]
        ])
        await message.answer(f"<b>{title}</b>\n{preview}", reply_markup=keyboard, parse_mode="HTML")

# === Отображение гидов ===
@router.message(F.text == "📘 Гиды")
async def show_guides(message: types.Message):
    user_id = message.from_user.id
    age_range = get_user_age_range(user_id).strip()

    if not has_full_access(user_id):
        await message.answer("❌ У вас нет доступа к гидам.")
        return

    items = get_library_items_by_type_and_age("guide", age_range)
    if not items:
        await message.answer("Пока нет доступных гидов для выбранного возраста.")
        return

    for item_id, title, description in items:
        preview = description[:200] + "..." if description else "Нет описания."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📄 Читать", callback_data=f"preview_{item_id}"),
                InlineKeyboardButton(text="⬇️ Скачать", callback_data=f"download_{item_id}")
            ]
        ])
        await message.answer(f"<b>{title}</b>\n{preview}", reply_markup=keyboard, parse_mode="HTML")

# === Предпросмотр статьи ===
@router.callback_query(F.data.startswith("preview_"))
async def preview_selected_pdf(callback: CallbackQuery):
    item_id = int(callback.data.replace("preview_", ""))
    conn = sqlite3.connect("db/mamabot_db.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, description FROM library WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        title, description = result
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔽 Читать полностью", callback_data=f"full_{item_id}")]
        ])
        await callback.message.answer(f"📄 <b>{title}</b>\n\n{description[:200]}...", reply_markup=keyboard, parse_mode="HTML")
    else:
        await callback.message.answer("❌ Файл не найден.")
    await callback.answer()

# === Полный текст статьи ===
@router.callback_query(F.data.startswith("full_"))
async def full_description(callback: CallbackQuery):
    item_id = int(callback.data.replace("full_", ""))
    conn = sqlite3.connect("db/mamabot_db.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, description FROM library WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        title, description = result
        await callback.message.answer(f"📖 <b>{title}</b>\n\n{description}", parse_mode="HTML")
    else:
        await callback.message.answer("❌ Файл не найден.")
    await callback.answer()

# === Загрузка PDF ===
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
@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)
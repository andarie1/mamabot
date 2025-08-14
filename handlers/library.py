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
from services.payments_fondy import create_payment_link
import sqlite3
import os

router = Router()

# === Paywall текст ===
PAYWALL_MSG = (
    "🔒 Раздел «Библиотека PDF» доступен по подписке.\n\n"
    "Пока мы готовим оплату, этот раздел закрыт. "
    "Ты можешь пользоваться бесплатными разделами: «📅 День с Тимми», «📚 Обучение», "
    "«💡 Советы от профи», «📈 Мой прогресс», «🔖 Недавно просмотренные».\n\n"
    "Чтобы открыть доступ к PDF-гайдам и чек-листам, оформи подписку 👇"
)

# === Тарифы из .env ===
PLANS = {
    "month":  {"title": "1 месяц",   "amount": float(os.getenv("SUB_MONTH_EUR", "4.99"))},
    "quarter":{"title": "3 месяца",  "amount": float(os.getenv("SUB_QUARTER_EUR", "12.99"))},
    "year":   {"title": "12 месяцев","amount": float(os.getenv("SUB_YEAR_EUR", "39.99"))},
}
SUB_DESC = os.getenv("SUB_DESC", "Доступ к библиотеке PDF")

def paywall_keyboard(user_id: int) -> InlineKeyboardMarkup:
    kb_rows = []
    for key, plan in PLANS.items():
        url = create_payment_link(
            user_id=user_id,
            amount_eur=plan["amount"],
            description=f"{SUB_DESC} — {plan['title']}",
            plan_key=key
        )
        kb_rows.append([InlineKeyboardButton(text=f"💳 {plan['title']} — {plan['amount']:.2f} €", url=url)])
    return InlineKeyboardMarkup(inline_keyboard=kb_rows)

AGE_CHOICES = ["0–2 года", "2–4 года", "4–6 лет"]

# === Клавиатуры ===
def get_age_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=age)] for age in AGE_CHOICES],
        resize_keyboard=True
    )

def paywall_keyboard() -> InlineKeyboardMarkup:
    # три кнопки с тарифами
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"💳 {PLANS['month']['title']} • {PLANS['month']['amount']:.2f} €",
            callback_data="pay_sub:month"
        )],
        [InlineKeyboardButton(
            text=f"💳 {PLANS['quarter']['title']} • {PLANS['quarter']['amount']:.2f} €",
            callback_data="pay_sub:quarter"
        )],
        [InlineKeyboardButton(
            text=f"💳 {PLANS['year']['title']} • {PLANS['year']['amount']:.2f} €",
            callback_data="pay_sub:year"
        )],
    ])

def library_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Чек-листы"), KeyboardButton(text="📘 Гиды")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )

# === Утилиты (меньше дублирования) ===
async def require_age_or_keyboard(message: types.Message) -> str | None:
    """Вернёт age_range или покажет клавиатуру выбора возраста и вернёт None."""
    age = get_user_age_range(message.from_user.id)
    if not age:
        await message.answer("👶 Пожалуйста, выберите возраст ребёнка:", reply_markup=get_age_keyboard())
        return None
    return age

async def require_access_or_paywall(message: types.Message) -> bool:
    """Вернёт True если есть доступ, иначе покажет paywall и вернёт False."""
    if has_full_access(message.from_user.id):
        return True
    await message.answer(PAYWALL_MSG, reply_markup=paywall_keyboard())
    return False

def get_library_items_by_type_and_age(item_type: str, age_range: str):
    """Достаёт список (id, title) из БД по типу и возрасту."""
    conn = sqlite3.connect("db/mamabot_db.db")
    cursor = conn.cursor()

    path_filter = "checklists" if item_type == "checklist" else "guides"
    age_range = (age_range or "").strip()

    cursor.execute("SELECT age_from, age_to FROM age_ranges WHERE name = ?", (age_range,))
    age_data = cursor.fetchone()
    if not age_data:
        conn.close()
        return []

    age_from, age_to = age_data

    cursor.execute("""
        SELECT l.id, l.title
        FROM library l
        JOIN age_bindings ab ON ab.content_type = 'library' AND ab.content_id = l.id
        JOIN age_ranges ar ON ar.id = ab.age_id
        WHERE ar.age_from <= ? AND ar.age_to >= ? AND l.file_path LIKE ?
        GROUP BY l.id
        ORDER BY l.id DESC
    """, (age_to, age_from, f"%{path_filter}%"))

    items = cursor.fetchall()
    conn.close()
    return items

async def send_items_by_type(message: types.Message, item_type: str, pretty_icon: str):
    """Общий вывод списка для чек-листов/гидов."""
    if not await require_access_or_paywall(message):
        return

    age_range = await require_age_or_keyboard(message)
    if not age_range:
        return

    items = get_library_items_by_type_and_age(item_type, age_range)
    if not items:
        await message.answer("Пока нет доступных материалов для выбранного возраста.")
        return

    for item_id, title in items:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬇️ Скачать PDF", callback_data=f"download_{item_id}")]
        ])
        await message.answer(f"{pretty_icon} <b>{title}</b>", reply_markup=kb, parse_mode="HTML")

# === Хендлеры ===
@router.message(F.text == "📖 Библиотека PDF")
async def show_library_menu(message: types.Message):
    # возраст нужен только для фильтрации — если нет, попросим выбрать
    age = get_user_age_range(message.from_user.id)
    if not age:
        await message.answer("👶 Пожалуйста, выберите возраст ребёнка:", reply_markup=get_age_keyboard())
        return

    if not has_full_access(message.from_user.id):
        await message.answer(PAYWALL_MSG, reply_markup=paywall_keyboard())
        return

    await message.answer("📖 Добро пожаловать в библиотеку Тимми!\n\nВыберите раздел:", reply_markup=library_menu_keyboard())

@router.message(F.text.in_(AGE_CHOICES))
async def handle_age_selection(message: types.Message):
    save_user_age_range(message.from_user.id, message.text.strip())
    await message.answer("✅ Возраст сохранён! Теперь ты можешь пользоваться платными разделами.")
    await show_library_menu(message)

@router.message(F.text == "📋 Чек-листы")
async def show_checklists(message: types.Message):
    await send_items_by_type(message, item_type="checklist", pretty_icon="📄")

@router.message(F.text == "📘 Гиды")
async def show_guides(message: types.Message):
    await send_items_by_type(message, item_type="guide", pretty_icon="📘")

@router.callback_query(F.data.startswith("download_"))
async def send_selected_pdf(callback: CallbackQuery):
    # Paywall и права
    if not has_full_access(callback.from_user.id):
        await callback.message.answer(PAYWALL_MSG, reply_markup=paywall_keyboard())
        await callback.answer()
        return

    # Достаём файл
    item_id = int(callback.data.replace("download_", ""))
    conn = sqlite3.connect("db/mamabot_db.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, file_path FROM library WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        await callback.message.answer("❌ Файл не найден в базе данных.")
        await callback.answer()
        return

    title, file_path = result
    if not os.path.exists(file_path):
        await callback.message.answer("❌ Файл не найден на сервере.")
        await callback.answer()
        return

    await callback.message.answer_document(FSInputFile(file_path), caption=f"📄 {title}")
    await callback.answer()

# === Оплата: 3 тарифа (Fondy) ===
@router.callback_query(F.data.startswith("pay_sub:"))
async def create_payment(callback: CallbackQuery):
    plan_key = callback.data.split(":", 1)[1]
    plan = PLANS.get(plan_key)
    if not plan:
        await callback.answer("Неверный тариф", show_alert=True)
        return

    try:
        url = create_payment_link(
            user_id=callback.from_user.id,
            amount_eur=plan["amount"],
            description=f"{SUB_DESC} — {plan['title']}",
            response_url=None,
            server_callback_url=None
        )
        await callback.message.answer(
            f"💳 <b>Подписка: {plan['title']}</b>\n"
            f"Сумма: {plan['amount']:.2f} EUR\n\n"
            f"Перейдите по ссылке для оплаты:\n{url}",
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer("❌ Не удалось сформировать ссылку на оплату. Попробуйте позже.")
    finally:
        await callback.answer()

# === Назад в главное меню ===
@router.message(F.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

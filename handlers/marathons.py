from aiogram import Router, types, F
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
import os

from services.user_profile import (
    has_full_access,
    get_user_age_range,
    save_user_age_range
)
from services.payments_fondy import create_payment_link

router = Router()

# ===== Пэйволл-текст =====
PAYWALL_MSG = (
    "🔒 Раздел «Марафоны и интенсивы» доступен по подписке.\n\n"
    "Пока мы готовим оплату, этот раздел закрыт. "
    "Ты можешь пользоваться бесплатными разделами: «📅 День с Тимми», «📚 Обучение», "
    "«💡 Советы от профи», «📈 Мой прогресс», «🔖 Недавно просмотренные».\n\n"
    "Чтобы открыть доступ к марафонам, оформи подписку 👇"
)

# ===== Тарифы (EUR) из .env с дефолтами =====
SUB_MONTH_EUR   = float(os.getenv("SUB_MONTH_EUR",   "4.99"))
SUB_QUARTER_EUR = float(os.getenv("SUB_QUARTER_EUR", "12.99"))
SUB_YEAR_EUR    = float(os.getenv("SUB_YEAR_EUR",    "39.99"))
SUB_DESC        = os.getenv("SUB_DESC", "Доступ к разделу «Марафоны и интенсивы»")

PLANS = {
    "month":   {"title": "1 месяц",    "amount": SUB_MONTH_EUR},
    "quarter": {"title": "3 месяца",   "amount": SUB_QUARTER_EUR},
    "year":    {"title": "12 месяцев", "amount": SUB_YEAR_EUR},
}

AGE_CHOICES = ["0–2 года", "2–4 года", "4–6 лет"]

# ===== Клавиатуры =====
def get_age_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=age)] for age in AGE_CHOICES] + [[KeyboardButton(text="🔙 Назад в главное меню")]],
        resize_keyboard=True
    )

def get_marathon_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 Подготовка к садику"), KeyboardButton(text="✏ Подготовка к школе")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )

def paywall_keyboard() -> InlineKeyboardMarkup:
    # три inline‑кнопки тарифов
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 {PLANS['month']['title']} • {PLANS['month']['amount']:.2f} EUR",
                              callback_data="mr_pay:month")],
        [InlineKeyboardButton(text=f"💳 {PLANS['quarter']['title']} • {PLANS['quarter']['amount']:.2f} EUR",
                              callback_data="mr_pay:quarter")],
        [InlineKeyboardButton(text=f"💳 {PLANS['year']['title']} • {PLANS['year']['amount']:.2f} EUR",
                              callback_data="mr_pay:year")],
    ])

# ===== Вход в раздел =====
@router.message(F.text == "🚀 Марафоны и интенсивы")
async def show_marathons_menu(message: types.Message):
    user_id = message.from_user.id
    age = get_user_age_range(user_id)

    if not age:
        await message.answer(
            "👶 Пожалуйста, выбери возраст ребёнка, чтобы мы могли предложить подходящие программы:",
            reply_markup=get_age_keyboard()
        )
        return

    # Пэйволл: нет полного доступа — показываем заглушку + тарифы
    if not has_full_access(user_id):
        await message.answer(PAYWALL_MSG, reply_markup=paywall_keyboard())
        return

    await message.answer(
        "🚀 Здесь собраны специальные программы и интенсивы.\n\nВыбери марафон:",
        reply_markup=get_marathon_menu_keyboard()
    )

# ===== Выбор возраста =====
@router.message(F.text.in_(AGE_CHOICES))
async def handle_age_selection(message: types.Message):
    save_user_age_range(message.from_user.id, message.text)
    await message.answer("✅ Возраст сохранён!")
    await show_marathons_menu(message)

# ===== Контент марафонов (для тех, у кого доступ есть) =====
@router.message(F.text.in_({"🎯 Подготовка к садику", "✏ Подготовка к школе"}))
async def marathon_content_handler(message: types.Message):
    user_id = message.from_user.id

    if not has_full_access(user_id):
        await message.answer(PAYWALL_MSG, reply_markup=paywall_keyboard())
        return

    await message.answer(
        f"✅ Доступ открыт! 🎉\n\n"
        f"Начинай марафон: {message.text}.\n"
        f"Задания и трекер прогресса скоро будут доступны здесь."
    )

# ===== Оплата: inline‑кнопки тарифов =====
@router.callback_query(F.data.startswith("mr_pay:"))
async def handle_pay_click(callback: CallbackQuery):
    plan_key = callback.data.split(":", 1)[1]
    plan = PLANS.get(plan_key)
    if not plan:
        await callback.message.answer("❌ Неизвестный тариф. Попробуй ещё раз.")
        await callback.answer()
        return

    try:
        url = create_payment_link(
            user_id=callback.from_user.id,
            plan_key=plan_key,
            amount=plan["amount"],
            description=SUB_DESC,
            # при наличии домена можно явно прокинуть URLs:
            # response_url="https://yourapp/thanks",
            # server_callback_url="https://yourapp/fondy/webhook",
        )
        await callback.message.answer(
            f"💳 <b>Оплата подписки</b>\n"
            f"Тариф: {plan['title']}\n"
            f"Сумма: {plan['amount']:.2f} EUR\n\n"
            f"Перейди по ссылке для оплаты:\n{url}",
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.answer("❌ Не удалось сформировать ссылку на оплату. Попробуй позже.")
    finally:
        await callback.answer()

# ===== Назад в главное меню =====
@router.message(F.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

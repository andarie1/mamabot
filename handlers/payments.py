from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web
from datetime import datetime, timedelta
import os

from services.payments_fondy import (
    create_payment_link,
    verify_webhook_signature,
    parse_order_id,
)
from services.user_profile import set_subscription

router = Router()

# ==== Тарифы (в EUR) — подхватываем из .env, есть дефолты ====
SUB_MONTH_EUR   = float(os.getenv("SUB_MONTH_EUR",   "4.99"))
SUB_QUARTER_EUR = float(os.getenv("SUB_QUARTER_EUR", "12.99"))
SUB_YEAR_EUR    = float(os.getenv("SUB_YEAR_EUR",    "39.99"))
SUB_DESC        = os.getenv("SUB_DESC", "Доступ к библиотеке PDF")

PLAN_DAYS = {
    "month":   30,
    "quarter": 90,
    "year":    365,
}

def pay_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"💳 Оплата: {SUB_MONTH_EUR:.2f} EUR / 1 месяц")],
            [KeyboardButton(text=f"💳 Оплата: {SUB_QUARTER_EUR:.2f} EUR / 3 месяца")],
            [KeyboardButton(text=f"💳 Оплата: {SUB_YEAR_EUR:.2f} EUR / 12 месяцев")],
            [KeyboardButton(text="🔙 Назад в главное меню")],
        ],
        resize_keyboard=True
    )

# Показать меню оплаты по клику «Оплатить» или «Открыть доступ»
@router.message(F.text.in_({"💳 Оплатить подписку (тест)", "🔓 Открыть доступ"}))
async def show_plans(message: types.Message):
    await message.answer(
        "Выберите вариант подписки, пришлю ссылку на оплату 👇",
        reply_markup=pay_keyboard()
    )

# Три обработчика на конкретные планы
@router.message(F.text.startswith("💳 Оплата:"))
async def choose_plan(message: types.Message):
    text = message.text or ""
    user_id = message.from_user.id

    if "1 месяц" in text:
        plan_key, amount = "month", SUB_MONTH_EUR
        title = f"Подписка — 1 месяц ({amount:.2f} EUR)"
    elif "3 месяца" in text:
        plan_key, amount = "quarter", SUB_QUARTER_EUR
        title = f"Подписка — 3 месяца ({amount:.2f} EUR)"
    elif "12 месяцев" in text:
        plan_key, amount = "year", SUB_YEAR_EUR
        title = f"Подписка — 12 месяцев ({amount:.2f} EUR)"
    else:
        await message.answer("Не понял план. Выберите один из трёх вариантов на клавиатуре.")
        return

    # Генерим ссылку через сервис
    try:
        url = create_payment_link(
            user_id=user_id,
            plan_key=plan_key,
            amount=amount,
            description=SUB_DESC,
            # можно явно прокинуть response_url/server_callback_url, если уже известен домен
            # response_url="https://example.com/thanks",
            # server_callback_url="https://example.com/fondy/webhook",
        )
        await message.answer(
            f"💳 <b>{title}</b>\n\n"
            f"Перейдите по ссылке для оплаты:\n{url}\n\n"
            "Для sandbox‑платежа используйте тестовую карту: <code>4444 5555 6666 1111</code> (любая дата/CCV).",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"❌ Не удалось создать ссылку оплаты: {e}")

# ==== Вебхук Fondy ====
async def fondy_webhook(request: web.Request) -> web.Response:
    """
    Серверный колбэк от Fondy (POST, form-urlencoded).
    Обязательно должен быть доступен по публичному HTTPS‑URL.
    На проде — обязательно проверяем подпись!
    """
    form = await request.post()
    data = {k: v for k, v in form.items()}

    # 1) Проверяем подпись
    if not verify_webhook_signature(data):
        return web.Response(text="bad signature", status=400)

    order_status = data.get("order_status", "")
    order_id = data.get("order_id", "")

    # 2) Достаём user_id, план
    user_id, plan_key, _rnd = parse_order_id(order_id)
    if not user_id or not plan_key:
        return web.Response(text="bad order_id", status=400)

    # 3) Проставляем подписку только при успешной оплате
    if order_status == "approved":
        days = PLAN_DAYS.get(plan_key, 30)
        until = datetime.utcnow() + timedelta(days=days)
        set_subscription(user_id, until)
        return web.Response(text="OK")

    # Иные статусы нам не интересны
    return web.Response(text="IGNORED")

from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from services.ai_generator import generate_expert_tip
from services.user_profile import get_trial_status

router = Router()

# === Вспомогательная функция проверки подписки ===
async def check_trial_and_inform(message: types.Message) -> bool:
    status = get_trial_status(message.from_user.id)
    if status == "almost_over":
        await message.answer(
            "⏳ Ваш пробный период заканчивается завтра! Чтобы продолжить пользоваться советами экспертов, оформите подписку 💳."
        )
    if status == "expired":
        await message.answer(
            "🚫 Пробный период завершён. Доступ к советам экспертов закрыт. Оформите подписку, чтобы продолжить."
        )
        return False
    return True

# === Меню советов ===
@router.message(lambda msg: msg.text == "💡 Советы от профи")
async def show_tips_menu(message: types.Message):
    if not await check_trial_and_inform(message):
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗣 Совет логопеда"), KeyboardButton(text="🧠 Совет психолога")],
            [KeyboardButton(text="👨‍⚕️ Совет педиатра")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "📑 Полезные советы для родителей от экспертов.\n\nВыберите, что вас интересует 👇",
        reply_markup=keyboard
    )

# === Генератор совета по специалисту ===
async def send_expert_tip(message: types.Message, expert: str, emoji: str):
    if not await check_trial_and_inform(message):
        return
    await message.answer(f"⏳ Генерирую совет от {expert}а...")
    tip = generate_expert_tip(user_id=message.from_user.id, expert=expert)
    await message.answer(f"{emoji} Совет {expert}а:\n\n{tip}")

# === Логопед ===
@router.message(lambda msg: msg.text == "🗣 Совет логопеда")
async def speech_therapist_tip(message: types.Message):
    await send_expert_tip(message, "логопед", "🗣")

# === Психолог ===
@router.message(lambda msg: msg.text == "🧠 Совет психолога")
async def psychologist_tip(message: types.Message):
    await send_expert_tip(message, "психолог", "🧠")

# === Педиатр ===
@router.message(lambda msg: msg.text == "👨‍⚕️ Совет педиатра")
async def pediatrician_tip(message: types.Message):
    await send_expert_tip(message, "педиатр", "👨‍⚕️")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.start import start_handler
from services.ai_generator import generate_expert_tip
from services.user_profile import get_trial_status  # <== добавляем импорт

router = Router()

@router.message(lambda msg: msg.text == "💡 Советы от профи")
async def show_tips_menu(message: types.Message):
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

async def check_trial_and_inform(message: types.Message) -> bool:
    """Проверка пробного периода перед генерацией совета"""
    status = get_trial_status(message.from_user.id)
    if status == "almost_over":
        await message.answer(
            "⏳ Ваш пробный период заканчивается завтра! Чтобы продолжить пользоваться советами экспертов, оформите подписку 💳."
        )
    if status == "expired":
        await message.answer(
            "🚫 Ваш пробный период завершён. Доступ к советам экспертов закрыт. Для продления откройте подписку."
        )
        return False
    return True

@router.message(lambda msg: msg.text == "🗣 Совет логопеда")
async def speech_therapist_tip(message: types.Message):
    if not await check_trial_and_inform(message):
        return
    await message.answer("⏳ Генерирую совет от логопеда...")
    tip = generate_expert_tip(user_id=message.from_user.id, expert="логопед")
    await message.answer(f"🗣 Совет логопеда:\n\n{tip}")

@router.message(lambda msg: msg.text == "🧠 Совет психолога")
async def psychologist_tip(message: types.Message):
    if not await check_trial_and_inform(message):
        return
    await message.answer("⏳ Генерирую совет от детского психолога...")
    tip = generate_expert_tip(user_id=message.from_user.id, expert="психолог")
    await message.answer(f"🧠 Совет психолога:\n\n{tip}")

@router.message(lambda msg: msg.text == "👨‍⚕️ Совет педиатра")
async def pediatrician_tip(message: types.Message):
    if not await check_trial_and_inform(message):
        return
    await message.answer("⏳ Генерирую совет от педиатра...")
    tip = generate_expert_tip(user_id=message.from_user.id, expert="педиатр")
    await message.answer(f"👨‍⚕️ Совет педиатра:\n\n{tip}")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

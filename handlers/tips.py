from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.start import start_handler
from services.ai_generator import generate_ai_lesson

router = Router()

@router.message(lambda msg: msg.text == "🗂 Полезные материалы")
async def show_materials_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗣 Совет логопеда"), KeyboardButton(text="🧠 Совет психолога")],
            [KeyboardButton(text="👨‍⚕️ Совет педиатра")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "🗂 Полезные советы для родителей от экспертов.\n\n"
        "Выберите, что вас интересует 👇",
        reply_markup=keyboard
    )

@router.message(lambda msg: msg.text == "🗣 Совет логопеда")
async def speech_therapist_tip(message: types.Message):
    await message.answer("⏳ Генерирую совет от логопеда...")
    try:
        tip = generate_ai_lesson(user_id=message.from_user.id, topic="логопед")
        await message.answer(f"🗣 Совет логопеда:\n\n{tip}")
    except Exception as e:
        await message.answer("❌ Не удалось получить совет. Попробуйте позже.")
        raise e

@router.message(lambda msg: msg.text == "🧠 Совет психолога")
async def psychologist_tip(message: types.Message):
    await message.answer("⏳ Генерирую совет от детского психолога...")
    try:
        tip = generate_ai_lesson(user_id=message.from_user.id, topic="психолог")
        await message.answer(f"🧠 Совет психолога:\n\n{tip}")
    except Exception as e:
        await message.answer("❌ Не удалось получить совет. Попробуйте позже.")
        raise e

@router.message(lambda msg: msg.text == "👨‍⚕️ Совет педиатра")
async def pediatrician_tip(message: types.Message):
    await message.answer("⏳ Генерирую совет от педиатра...")
    try:
        tip = generate_ai_lesson(user_id=message.from_user.id, topic="педиатр")
        await message.answer(f"👨‍⚕️ Совет педиатра:\n\n{tip}")
    except Exception as e:
        await message.answer("❌ Не удалось получить совет. Попробуйте позже.")
        raise e

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

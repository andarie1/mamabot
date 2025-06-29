from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json
from pathlib import Path
from handlers.start import start_handler

router = Router()

QUESTIONS_FILE = Path("data/questions.json")
QUESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
if not QUESTIONS_FILE.exists():
    QUESTIONS_FILE.write_text(json.dumps({}, indent=2), encoding="utf-8")

@router.message(lambda msg: msg.text == "📞 Помощь и связь")
async def show_contact_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💬 Задать вопрос")],
            [KeyboardButton(text="💡 Предложить тему")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "📢 Мы всегда на связи!\n"
        "Задайте вопрос или предложите тему для новых материалов 👇",
        reply_markup=keyboard
    )

@router.message(lambda msg: msg.text == "💬 Задать вопрос")
async def ask_question_prompt(message: types.Message):
    await message.answer(
        "✉️ Напиши свой вопрос одним сообщением, и я его сохраню для нашей команды!"
    )

@router.message(lambda msg: msg.text == "💡 Предложить тему")
async def suggest_topic_handler(message: types.Message):
    await message.answer(
        "💡 Напишите, какую тему, марафон или чек-лист вы хотели бы увидеть — нам важно ваше мнение!"
    )

@router.message(lambda msg: msg.reply_to_message and "свой вопрос" in msg.reply_to_message.text)
async def save_question_handler(message: types.Message):
    data = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8").strip() or "{}")
    user_id = str(message.from_user.id)
    data.setdefault(user_id, []).append({
        "username": message.from_user.username,
        "question": message.text,
    })
    QUESTIONS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    await message.answer("✅ Спасибо! Вопрос принят. Мы свяжемся с вами при необходимости.")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

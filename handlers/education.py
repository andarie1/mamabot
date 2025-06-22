from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from handlers.start import lesson_handler
from services.progress_report import generate_progress_report

router = Router()

@router.message(lambda msg: msg.text == "📋 Обучение")
async def show_education_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔢 По возрастам (ведёт к выбору возраста)"),
            ],
            [
                KeyboardButton(text="📷 Развивающие уроки (AI)"),
            ],
            [
                KeyboardButton(text="📈 Прогресс"),
            ],
            [
                KeyboardButton(text="🔙 Назад в главное меню")
            ]
        ],
        resize_keyboard=True
    )
    await message.answer("📋 Меню обучения. Выбери, что интересно:", reply_markup=keyboard)


@router.message(lambda msg: msg.text == "📷 Развивающие уроки (AI)")
async def ai_lessons_handler(message: types.Message):
    await lesson_handler(message)


@router.message(lambda msg: msg.text == "📈 Прогресс")
async def progress_shortcut_handler(message: types.Message):
    pdf_path = generate_progress_report(message.from_user.id, message.from_user.first_name)
    if pdf_path:
        await message.answer_document(FSInputFile(pdf_path), caption="📊 Вот твой прогресс!")
    else:
        await message.answer("Пока нет данных для отчёта 😔")


@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

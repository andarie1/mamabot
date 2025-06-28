from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from handlers.start import start_handler

router = Router()

@router.message(lambda msg: msg.text == "📚 Библиотека PDF")
async def show_library_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Чек-листы"), KeyboardButton(text="📖 Мини-книги")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("📚 Добро пожаловать в библиотеку Тимми!\n\nВыберите раздел:", reply_markup=keyboard)

@router.message(lambda msg: msg.text == "📋 Чек-листы")
async def checklist_handler(message: types.Message):
    try:
        pdf_path = "pdfs/checklist_ru_ro.pdf"  # пример пути к PDF с текстом на русском и румынском
        await message.answer_document(FSInputFile(pdf_path), caption="📋 Вот твой PDF-чек-лист на русском и румынском языках!")
    except Exception:
        await message.answer("❌ Не удалось загрузить чек-лист. Попробуйте позже или свяжитесь с поддержкой.")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

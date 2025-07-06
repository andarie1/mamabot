from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from handlers.start import start_handler
from services.user_profile import has_active_subscription

router = Router()

@router.message(lambda msg: msg.text == "📖 Библиотека PDF")
async def show_library_menu(message: types.Message):
    if not has_active_subscription(message.from_user.id):
        await message.answer(
            "🚫 Доступ к библиотеке закрыт.\n"
            "Чтобы открыть PDF-чек-листы и мини-книги, активируйте подписку 💳."
        )
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Чек-листы"), KeyboardButton(text="📖 Гиды")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("📖 Добро пожаловать в библиотеку Тимми!\n\nВыберите раздел:", reply_markup=keyboard)

@router.message(lambda msg: msg.text == "📋 Чек-листы")
async def checklist_handler(message: types.Message):
    if not has_active_subscription(message.from_user.id):
        await message.answer("🚫 У вас нет активной подписки для доступа к чек-листам. Оформите подписку 💳.")
        return
    try:
        pdf_path = "pdfs/checklist_ru_ro.pdf"  # пример пути к PDF
        await message.answer_document(FSInputFile(pdf_path), caption="📋 Вот твой PDF-чек-лист на русском и румынском языках!")
    except Exception:
        await message.answer("❌ Не удалось загрузить чек-лист. Попробуйте позже или свяжитесь с поддержкой.")

@router.message(lambda msg: msg.text == "📖 Гиды")
async def guides_handler(message: types.Message):
    if not has_active_subscription(message.from_user.id):
        await message.answer("🚫 У вас нет активной подписки для доступа к гидам. Оформите подписку 💳.")
        return
    try:
        pdf_path = "pdfs/guide_sample.pdf"  # пример гида
        await message.answer_document(FSInputFile(pdf_path), caption="📖 Вот твой гид!")
    except Exception:
        await message.answer("❌ Не удалось загрузить гид. Попробуйте позже или свяжитесь с поддержкой.")

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

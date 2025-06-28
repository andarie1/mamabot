from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from services.progress_tracker import get_achievements, get_progress
from services.progress_report import generate_progress_report
from handlers.start import start_handler

router = Router()

@router.message(lambda msg: msg.text == "📈 Мой прогресс")
async def show_progress_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏅 Мои медали"), KeyboardButton(text="📊 История заданий")],
            [KeyboardButton(text="📄 Скачать отчёт (PDF)")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("📈 Прогресс твоего малыша — вся история и достижения здесь 👇", reply_markup=keyboard)


@router.message(lambda msg: msg.text == "🏅 Мои медали")
async def medals_handler(message: types.Message):
    result = get_achievements(message.from_user.id)
    if result:
        await message.answer(result)
    else:
        await message.answer("Пока нет медалей. Выполняй уроки с Тимми!")


@router.message(lambda msg: msg.text == "📊 История заданий")
async def history_handler(message: types.Message):
    progress = get_progress(message.from_user.id)
    if not progress:
        await message.answer("История пока пуста. Выполни своё первое задание!")
    else:
        text = "\n".join([f"— {entry['activity']} ({entry['timestamp']})" for entry in progress])
        await message.answer(f"📘 Вот твои задания:\n\n{text}")


@router.message(lambda msg: msg.text == "📄 Скачать отчёт (PDF)")
async def download_report_handler(message: types.Message):
    path = generate_progress_report(message.from_user.id, message.from_user.first_name)
    if path:
        await message.answer_document(FSInputFile(path), caption="📄 Вот твой PDF-отчёт!")
    else:
        await message.answer("Нет данных для отчёта 😔")


@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

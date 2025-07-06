from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from handlers.start import start_handler
from services.user_profile import has_active_subscription

router = Router()

@router.message(lambda msg: msg.text == "🚀 Марафоны и интенсивы")
async def show_marathons_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎯 Подготовка к садику"), KeyboardButton(text="✏ Подготовка к школе")],
            [KeyboardButton(text="🔓 Открыть доступ"), KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "🚀 Здесь собраны специальные программы и интенсивы.\n\n"
        "Чтобы открыть доступ, оплатите подписку.\n"
        "Выберите интересующий марафон или нажмите «🔓 Открыть доступ»:",
        reply_markup=keyboard
    )

@router.message(lambda msg: msg.text in {"🎯 Подготовка к садику", "✏ Подготовка к школе"})
async def marathon_content_handler(message: types.Message):
    if has_active_subscription(message.from_user.id):
        await message.answer(
            f"✅ Доступ открыт! 🎉\n\n"
            f"Начинай марафон: {message.text}.\n"
            f"Твои задания скоро будут доступны здесь!"
        )
    else:
        await message.answer(
            "🔒 Этот марафон доступен только после оплаты.\n\n"
            "Нажмите «🔓 Открыть доступ», чтобы перейти к оплате."
        )

@router.message(lambda msg: msg.text == "🔓 Открыть доступ")
async def open_access_handler(message: types.Message):
    await message.answer(
        "💳 Чтобы получить полный доступ к марафонам и интенсивам, перейдите по ссылке для оплаты:\n\n"
        "<b>[Ваша ссылка на оплату]</b>\n\n"
        "После успешной оплаты доступ будет открыт автоматически! 🎉",
        parse_mode="HTML"
    )

@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    await start_handler(message)

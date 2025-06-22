from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

@router.message(lambda msg: msg.text == "🎁 Полезности и материалы")
async def show_materials_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Чек-листы"), KeyboardButton(text="🎉 Сюрпризы и подарки")],
            [KeyboardButton(text="📄 Статьи и советы"), KeyboardButton(text="🧩 Игры для дома")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("📚 Здесь ты найдешь полезные материалы и сюрпризы для занятий с ребёнком 👇", reply_markup=keyboard)


@router.message(lambda msg: msg.text == "📋 Чек-листы")
async def checklists_handler(message: types.Message):
    await message.answer("📋 Скоро появятся тематические чек-листы на каждый день!")


@router.message(lambda msg: msg.text == "🎉 Сюрпризы и подарки")
async def gifts_handler(message: types.Message):
    await message.answer("🎉 Небольшие PDF-подарки и бонусы от Тимми — в пути!")


@router.message(lambda msg: msg.text == "📄 Статьи и советы")
async def articles_handler(message: types.Message):
    await message.answer("📄 Советы от логопеда, игры и методы развития — будут доступны в этом разделе.")


@router.message(lambda msg: msg.text == "🧩 Игры для дома")
async def games_handler(message: types.Message):
    await message.answer("🧩 Скоро здесь появятся карточки и домашние задания в PDF-формате.")


@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

from aiogram import Router, types

router = Router()

@router.message(lambda msg: msg.text == "🧠 Полезные материалы")
async def helper_handler(message: types.Message):
    await message.answer("🌟 Я твой виртуальный гид Тимми! Скоро здесь появятся:\n— Урок на сегодня\n— Чек-лист недели\n— Игра в реальности\n— Совет дня")

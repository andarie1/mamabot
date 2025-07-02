from aiogram import Router, types
from aiogram.filters import Command
from pathlib import Path
import json

router = Router()


@router.message(Command("admin"))
async def admin_report(message: types.Message):
    user_id = message.from_user.id

    # Защита: команда только для владельца
    if user_id != 123456789:  # ЗАМЕНИ на свой Telegram ID
        await message.answer("❌ У вас нет прав для этой команды.")
        return

    # Загружаем данные пользователей
    users_path = Path("data/users.json")
    users_count = 0
    if users_path.exists():
        try:
            users_data = json.loads(users_path.read_text(encoding="utf-8").strip() or "{}")
            users_count = len(users_data)
        except json.JSONDecodeError:
            pass

    # Загружаем данные прогресса
    progress_path = Path("data/progress.json")
    total_activities = 0
    last_activity = "Нет данных"
    if progress_path.exists():
        try:
            progress_data = json.loads(progress_path.read_text(encoding="utf-8").strip() or "{}")
            total_activities = sum(len(acts) for acts in progress_data.values())
            # Последняя активность из последнего пользователя (по user_id)
            last_user_activities = progress_data.get(str(user_id), [])
            if last_user_activities:
                last_activity = last_user_activities[-1]["timestamp"]
        except json.JSONDecodeError:
            pass

    # Загружаем последние вопросы
    questions_path = Path("data/questions.json")
    last_questions = []
    if questions_path.exists():
        try:
            questions_data = json.loads(questions_path.read_text(encoding="utf-8").strip() or "{}")
            for uid, qlist in questions_data.items():
                for q in qlist:
                    last_questions.append(f"@{q['username'] or 'аноним'}: {q['question']}")
            last_questions = last_questions[-5:]
        except json.JSONDecodeError:
            pass

    # Формируем ответ
    report = (
        f"📊 <b>Отчёт администратора</b>\n\n"
        f"👥 Пользователей: <b>{users_count}</b>\n"
        f"✅ Всего выполнено заданий: <b>{total_activities}</b>\n"
        f"🕒 Последняя активность: <b>{last_activity}</b>\n\n"
    )
    if last_questions:
        report += "📝 Последние вопросы:\n" + "\n".join([f"- {q}" for q in last_questions])
    else:
        report += "📝 Последние вопросы: нет."

    await message.answer(report, parse_mode="HTML")

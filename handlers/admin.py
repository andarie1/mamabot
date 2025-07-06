from aiogram import Router, types
from aiogram.filters import Command
from pathlib import Path
import json
import os
import logging

router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID", "5566778899"))

@router.message(Command("admin"))
async def admin_report(message: types.Message):
    user_id = message.from_user.id

    # Защита: команда только для владельца
    if user_id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для этой команды.")
        return

    report_lines = []

    try:
        # Загрузка данных пользователей
        users_path = Path("data/users.json")
        users_count = 0
        if users_path.exists():
            users_data = json.loads(users_path.read_text(encoding="utf-8").strip() or "{}")
            users_count = len(users_data)

        # Загрузка данных прогресса
        progress_path = Path("data/progress.json")
        total_activities = 0
        last_activity = "Нет данных"
        if progress_path.exists():
            progress_data = json.loads(progress_path.read_text(encoding="utf-8").strip() or "{}")
            total_activities = sum(len(acts) for acts in progress_data.values())
            # Поиск последней активности по всем пользователям
            all_activities = [
                activity["timestamp"]
                for activities in progress_data.values() for activity in activities
            ]
            if all_activities:
                last_activity = max(all_activities)

        # Загрузка последних вопросов
        questions_path = Path("data/questions.json")
        last_questions = []
        if questions_path.exists():
            questions_data = json.loads(questions_path.read_text(encoding="utf-8").strip() or "{}")
            for uid, qlist in questions_data.items():
                for q in qlist:
                    username = f"@{q['username']}" if q.get('username') else 'аноним'
                    last_questions.append(f"{username}: {q['question']}")
            last_questions = last_questions[-5:]

        # Составляем отчёт
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

    except Exception as e:
        logging.exception("Ошибка при формировании отчёта администратора")
        await message.answer("❌ Произошла ошибка при формировании отчёта. Подробности смотри в логах.")

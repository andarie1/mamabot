import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

PROGRESS_FILE = Path("data/progress.json")

# Гарантируем наличие файла с пустым словарём
if not PROGRESS_FILE.exists():
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps({}, indent=2), encoding="utf-8")

def _read_progress_data() -> Dict[str, List[Dict[str, str]]]:
    """Считывает данные прогресса из JSON-файла."""
    text = PROGRESS_FILE.read_text(encoding="utf-8").strip()
    try:
        return json.loads(text) if text and text.startswith("{") else {}
    except json.JSONDecodeError:
        return {}

def update_progress(user_id: int, activity: str) -> None:
    """Обновляет прогресс пользователя, добавляя новое действие с временной меткой."""
    data = _read_progress_data()
    now = datetime.now().isoformat(timespec='seconds')
    data.setdefault(str(user_id), []).append({
        "activity": activity,
        "timestamp": now
    })
    PROGRESS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_progress(user_id: int) -> List[Dict[str, str]]:
    """Возвращает полную историю прогресса пользователя."""
    data = _read_progress_data()
    return data.get(str(user_id), [])

def get_formatted_progress(user_id: int, limit: int = 10) -> list[str]:
    """Возвращает последние N действий пользователя в виде списка строк для отчёта."""
    progress = get_progress(user_id)
    return [
        f"{i + 1}. {p['activity']} — {p['timestamp']}"
        for i, p in enumerate(progress[-limit:])
    ]

def get_last_activities(user_id: int, limit: int = 3) -> List[str]:
    """Возвращает последние N действий для отображения в разделе 'Недавно просмотренные'."""
    data = _read_progress_data()
    return [entry["activity"] for entry in data.get(str(user_id), [])][-limit:]

def get_achievements(user_id: int) -> str:
    """Определяет достижения пользователя на основе количества выполненных уроков."""
    progress = get_progress(user_id)
    lesson_count = sum(1 for p in progress if "урок" in p["activity"].lower())

    if lesson_count >= 3:
        return "⭐ Звёздочка Тимми! Ты выполнил 3 урока!"
    elif lesson_count >= 1:
        return "✨ Первый шаг сделан! Гордимся тобой!"
    return ""

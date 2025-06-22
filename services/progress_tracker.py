import json
from pathlib import Path
from datetime import datetime

PROGRESS_FILE = Path("data/progress.json")

if not PROGRESS_FILE.exists():
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps({}, indent=2), encoding="utf-8")

def update_progress(user_id: int, activity: str) -> None:
    text = PROGRESS_FILE.read_text(encoding="utf-8").strip() if PROGRESS_FILE.exists() else ""

    if not text or not text.startswith("{"):
        data = {}
    else:
        data = json.loads(text)

    now = datetime.now().isoformat(timespec='seconds')

    if str(user_id) not in data:
        data[str(user_id)] = []

    data[str(user_id)].append({"activity": activity, "timestamp": now})

    PROGRESS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_progress(user_id: int) -> list[dict]:
    text = PROGRESS_FILE.read_text(encoding="utf-8").strip()
    data = json.loads(text) if text else {}
    return data.get(str(user_id), [])

def get_last_activities(user_id: int, limit: int = 5) -> list[str]:
    text = PROGRESS_FILE.read_text(encoding="utf-8").strip()
    data = json.loads(text) if text else {}
    return [entry["activity"] for entry in data.get(str(user_id), [])][-limit:]

def get_achievements(user_id: int) -> str:
    progress = get_progress(user_id)
    lesson_count = sum(1 for p in progress if "урок" in p["activity"].lower())

    if lesson_count >= 3:
        return "⭐ Звёздочка Тимми! Ты выполнил 3 урока!"
    elif lesson_count >= 1:
        return "✨ Первый шаг сделан! Гордимся тобой!"
    return ""

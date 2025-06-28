import json
from pathlib import Path
from typing import Optional

USERS_FILE = Path("data/users.json")

# Инициализация файла
if not USERS_FILE.exists():
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps({}, indent=2), encoding="utf-8")

def _read_users_data() -> dict:
    """Считывает данные пользователей из JSON-файла."""
    try:
        text = USERS_FILE.read_text(encoding="utf-8").strip()
        return json.loads(text) if text else {}
    except json.JSONDecodeError:
        return {}

def save_user_age_range(user_id: int, age_range: str) -> None:
    """
    Сохраняет возрастной диапазон в формате строки (например: '0-6 мес', '2-4 года').
    """
    data = _read_users_data()
    data[str(user_id)] = {**data.get(str(user_id), {}), "age_range": age_range}
    USERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_user_age_range(user_id: int) -> Optional[str]:
    """
    Получает сохранённый возрастной диапазон пользователя.
    """
    data = _read_users_data()
    return data.get(str(user_id), {}).get("age_range")

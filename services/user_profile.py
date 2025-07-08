import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# === Загрузка переменных окружения ===
load_dotenv()
admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(uid.strip()) for uid in admin_ids_str.split(",") if uid.strip().isdigit()]

USERS_FILE = Path("data/users.json")

# Гарантируем наличие файла с пользователями
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
    Сохраняет возрастной диапазон для пользователя (например: '0-6 мес', '2-4 года').
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

def save_trial_start(user_id: int) -> None:
    """
    Сохраняет дату начала пробного периода, если она ещё не была записана.
    """
    data = _read_users_data()
    user_key = str(user_id)
    if "trial_start" not in data.get(user_key, {}):
        data[user_key] = {**data.get(user_key, {}), "trial_start": datetime.utcnow().isoformat()}
        USERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_trial_status(user_id: int, trial_days: int = 7) -> str:
    """
    Проверяет статус пробного периода:
    - 'active' — если пробный период ещё идёт
    - 'almost_over' — если остался 1 день
    - 'expired' — если пробный период закончился
    """
    data = _read_users_data()
    trial_start_str = data.get(str(user_id), {}).get("trial_start")
    if not trial_start_str:
        return "expired"

    try:
        trial_start = datetime.fromisoformat(trial_start_str)
        now = datetime.utcnow()
        days_passed = (now - trial_start).days

        if days_passed < trial_days - 1:
            return "active"
        elif days_passed == trial_days - 1:
            return "almost_over"
        else:
            return "expired"
    except ValueError:
        return "expired"

def set_subscription(user_id: int, until: datetime) -> None:
    """
    Устанавливает или обновляет дату окончания платной подписки для пользователя.
    """
    data = _read_users_data()
    data.setdefault(str(user_id), {})
    data[str(user_id)]["subscription_until"] = until.isoformat()
    USERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def has_active_subscription(user_id: int) -> bool:
    """
    Проверяет, активна ли подписка пользователя на текущий момент.
    """
    if user_id in ADMIN_IDS:
        return True

    data = _read_users_data()
    sub_end_str: Optional[str] = data.get(str(user_id), {}).get("subscription_until")
    if not sub_end_str:
        return False

    try:
        sub_end = datetime.fromisoformat(sub_end_str)
        return datetime.utcnow() <= sub_end
    except ValueError:
        return False

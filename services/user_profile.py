import json
from pathlib import Path
from typing import Optional

USERS_FILE = Path("data/users.json")

# Инициализация файла
if not USERS_FILE.exists():
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps({}, indent=2), encoding="utf-8")

def _read_users_data() -> dict:
    try:
        text = USERS_FILE.read_text(encoding="utf-8").strip()
        return json.loads(text) if text else {}
    except json.JSONDecodeError:
        return {}

def save_user_age(user_id: int, age: int) -> None:
    data = _read_users_data()
    data[str(user_id)] = {**data.get(str(user_id), {}), "age": age}
    USERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_user_age(user_id: int) -> Optional[int]:
    data = _read_users_data()
    return data.get(str(user_id), {}).get("age")

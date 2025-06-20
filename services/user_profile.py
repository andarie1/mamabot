import json
from pathlib import Path

USERS_FILE = Path("data/users.json")

# Гарантируем, что файл существует
if not USERS_FILE.exists():
    USERS_FILE.write_text(json.dumps({}, indent=2), encoding="utf-8")


def save_user_age(user_id: int, age: int):
    data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
    user_data = data.get(str(user_id), {})
    user_data["age"] = age
    data[str(user_id)] = user_data
    USERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_user_age(user_id: int) -> int | None:
    data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
    return data.get(str(user_id), {}).get("age")

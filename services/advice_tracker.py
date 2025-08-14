import json
from datetime import datetime
from pathlib import Path

SUGGESTIONS_FILE = Path("logs/suggestions.json")

def _load_data():
    if not SUGGESTIONS_FILE.exists():
        SUGGESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SUGGESTIONS_FILE.write_text(json.dumps({}), encoding="utf-8")
    with SUGGESTIONS_FILE.open(encoding="utf-8") as f:
        return json.load(f)

def _save_data(data):
    with SUGGESTIONS_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def record_advice(user_id: int, topic: str, advice: str) -> None:
    data = _load_data()
    user_str = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")

    if user_str not in data:
        data[user_str] = {}
    if topic not in data[user_str]:
        data[user_str][topic] = []

    # Добавляем совет
    data[user_str][topic].append({"date": today, "advice": advice})

    _save_data(data)

def get_today_advices(user_id: int, topic: str) -> list[str]:
    """Вернёт советы по теме, выданные сегодня пользователю."""
    data = _load_data()
    user_str = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    return [
        item["advice"]
        for item in data.get(user_str, {}).get(topic, [])
        if item["date"] == today
    ]

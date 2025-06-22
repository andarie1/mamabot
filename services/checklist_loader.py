import json
from pathlib import Path

def load_checklist_by_age(age: int) -> list[str]:
    path = Path("data/checklists.json")

    if not path.exists():
        return ["Сделай 3 прыжка", "Нарисуй солнышко"]

    try:
        data = json.loads(path.read_text(encoding="utf-8").strip() or "{}")
    except json.JSONDecodeError:
        return ["Сделай 3 прыжка", "Нарисуй солнышко"]

    return data.get(str(age), ["Сделай 3 прыжка", "Нарисуй солнышко"])

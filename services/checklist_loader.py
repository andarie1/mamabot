import json
from pathlib import Path

def load_checklist_by_age(age: int) -> list[str]:
    path = Path("data/checklists.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get(str(age), ["Сделай 3 прыжка", "Нарисуй солнышко"])

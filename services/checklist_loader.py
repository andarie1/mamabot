import json
from pathlib import Path
from typing import List

CHECKLISTS_PATH = Path("data/checklists.json")

def load_checklist_by_age(age_label: str) -> List[str]:
    """
    Загружает список заданий (чек-лист) по возрастной категории.
    age_label — строка, например: '0-6m', '6-12m', '1-2y', '2-4y', '4-6y'.
    """

    # Если файла нет — возвращаем дефолтный список
    if not CHECKLISTS_PATH.exists():
        return ["Сделай 3 прыжка", "Нарисуй солнышко"]

    try:
        content = CHECKLISTS_PATH.read_text(encoding="utf-8").strip() or "{}"
        data = json.loads(content)
    except json.JSONDecodeError:
        return ["Сделай 3 прыжка", "Нарисуй солнышко"]

    # Получаем список по ключу возрастной категории или дефолт
    return data.get(age_label, ["Сделай 3 прыжка", "Нарисуй солнышко"])

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import json
from datetime import datetime

# Регистрируем кириллический шрифт
FONT_PATH = Path("fonts/DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_PATH)))

def generate_progress_report(user_id: int, username: str) -> str:
    progress_path = Path("data/progress.json")
    output_path = Path(f"assets/pdf/{user_id}_progress_report.pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not progress_path.exists() or not progress_path.read_text(encoding="utf-8").strip():
        return None

    try:
        progress = json.loads(progress_path.read_text(encoding="utf-8").strip())
    except json.JSONDecodeError:
        return None

    user_progress = progress.get(str(user_id), [])
    if not user_progress:
        return None

    c = canvas.Canvas(str(output_path), pagesize=A4)
    c.setFont("DejaVu", 16)
    c.drawString(100, 800, f"Отчёт о прогрессе {username} 🏆")
    c.setFont("DejaVu", 12)

    y = 770
    for i, item in enumerate(user_progress[-10:], 1):
        c.drawString(100, y, f"{i}. {item['activity']} — {item['timestamp']}")
        y -= 25
        if y < 100:
            c.showPage()
            c.setFont("DejaVu", 12)
            y = 800

    c.setFont("DejaVu", 10)
    c.drawString(100, y - 20, f"Дата отчёта: {datetime.now().strftime('%d.%m.%Y')}")
    c.save()
    return str(output_path)

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime
from services.progress_tracker import get_formatted_progress

# Регистрируем кириллический шрифт
FONT_PATH = Path("fonts/DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_PATH)))

def generate_progress_report(user_id: int, username: str) -> str:
    progress_lines = get_formatted_progress(user_id, limit=10)
    if not progress_lines:
        return None

    output_path = Path(f"assets/pdf/{user_id}_progress_report.pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)
    c.setFont("DejaVu", 16)
    c.drawString(100, 800, f"Отчёт о прогрессе {username} 🏆")
    c.setFont("DejaVu", 12)

    y = 770
    for line in progress_lines:
        c.drawString(100, y, line)
        y -= 25
        if y < 100:
            c.showPage()
            c.setFont("DejaVu", 12)
            y = 800

    c.setFont("DejaVu", 10)
    c.drawString(100, y - 20, f"Дата отчёта: {datetime.now().strftime('%d.%m.%Y')}")
    c.save()
    return str(output_path)

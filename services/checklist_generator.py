from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path
from datetime import date

# Регистрируем кириллический шрифт
FONT_PATH = Path("fonts/DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_PATH)))

def generate_checklist_pdf(username: str, tasks: list[str], filename: str = "checklist.pdf") -> str:
    path = Path("assets/pdf") / filename
    c = canvas.Canvas(str(path), pagesize=A4)

    c.setFont("DejaVu", 16)
    c.drawString(100, 800, f"Чек-лист от Тимми 🧸")
    c.setFont("DejaVu", 12)
    c.drawString(100, 780, f"{username}, вот задания на {date.today().strftime('%d.%m.%Y')}:")

    y = 750
    for i, task in enumerate(tasks, 1):
        c.drawString(100, y, f"[ ] {i}. {task}")
        y -= 25

    c.setFont("DejaVu", 10)
    c.drawString(100, 120, "Отмечай галочками, что выполнил 🖍️")
    c.save()
    return str(path)


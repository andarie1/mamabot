from pathlib import Path
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Регистрируем кириллический шрифт
FONT_PATH = Path("fonts/DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_PATH)))

def generate_checklist_pdf(username: str, tasks: list[str], filename: str = "checklist.pdf") -> str:
    path = Path("assets/pdf") / filename
    path.parent.mkdir(parents=True, exist_ok=True)  # Создаёт папку, если её нет
    c = canvas.Canvas(str(path), pagesize=A4)

    c.setFont("DejaVu", 16)
    c.drawString(100, 800, "Чек-лист от Тимми 🧸")

    c.setFont("DejaVu", 12)
    c.drawString(100, 780, f"{username}, вот задания на {date.today().strftime('%d.%m.%Y')}:")

    y = 750
    for i, task in enumerate(tasks, 1):
        c.drawString(100, y, f"[ ] {i}. {task}")
        y -= 25
        if y < 100:
            c.showPage()
            c.setFont("DejaVu", 12)
            y = 800

    c.setFont("DejaVu", 10)
    c.drawString(100, 100, "Отмечай галочками, что выполнил 🖍️")
    c.save()
    return str(path)

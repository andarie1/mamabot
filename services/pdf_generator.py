from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

# Регистрируем кириллический шрифт
FONT_PATH = Path("fonts/DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_PATH)))

def generate_lesson_pdf(username: str, task_text: str, filename: str = "lesson.pdf") -> str:
    output_path = Path("assets/pdf") / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)

    c.setFont("DejaVu", 16)
    c.drawString(100, 800, "Задание от Тимми 🧸")

    c.setFont("DejaVu", 12)
    c.drawString(100, 770, f"Привет, {username}! Вот твоё задание на сегодня:")

    text_object = c.beginText(100, 740)
    text_object.setFont("DejaVu", 12)
    for line in task_text.split('\n'):
        text_object.textLine(line)

    c.drawText(text_object)
    c.save()

    return str(output_path)

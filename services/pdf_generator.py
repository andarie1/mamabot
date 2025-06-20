from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path


def generate_lesson_pdf(username: str, task_text: str, filename: str = "lesson.pdf") -> str:
    output_path = Path("assets/pdf") / filename
    c = canvas.Canvas(str(output_path), pagesize=A4)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, f"Задание от Тимми 🧸")

    c.setFont("Helvetica", 12)
    c.drawString(100, 760, f"Привет, {username}! Вот твоё задание на сегодня:")

    text_object = c.beginText(100, 730)
    text_object.setFont("Helvetica", 12)
    for line in task_text.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)

    c.save()
    return str(output_path)

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import date

# Регистрируем кириллический шрифт
FONT_PATH = Path("fonts/DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_PATH)))

def generate_day_pdf(username: str, lesson: str, ritual: str, tip: str, filename: str = "day_with_timmy.pdf") -> str:
    """
    Генерирует PDF с тремя частями: Задание, Ритуал, Совет.
    """
    output_path = Path("assets/pdf") / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4

    # Заголовок
    c.setFont("DejaVu", 16)
    c.drawString(100, height - 50, "📅 День с Тимми — твой комплект заданий!")

    # Дата и приветствие
    c.setFont("DejaVu", 12)
    c.drawString(100, height - 80, f"Привет, {username}! Сегодня {date.today().strftime('%d.%m.%Y')}:")

    # Задание
    y = height - 120
    c.setFont("DejaVu", 14)
    c.drawString(100, y, "📚 Задание:")
    y -= 20
    c.setFont("DejaVu", 12)
    for line in lesson.split('\n'):
        c.drawString(100, y, line)
        y -= 18
        if y < 100:
            c.showPage()
            c.setFont("DejaVu", 12)
            y = height - 50

    # Ритуал
    y -= 20
    c.setFont("DejaVu", 14)
    c.drawString(100, y, "💤 Ритуал:")
    y -= 20
    c.setFont("DejaVu", 12)
    for line in ritual.split('\n'):
        c.drawString(100, y, line)
        y -= 18
        if y < 100:
            c.showPage()
            c.setFont("DejaVu", 12)
            y = height - 50

    # Совет
    y -= 20
    c.setFont("DejaVu", 14)
    c.drawString(100, y, "🧠 Совет:")
    y -= 20
    c.setFont("DejaVu", 12)
    for line in tip.split('\n'):
        c.drawString(100, y, line)
        y -= 18
        if y < 100:
            c.showPage()
            c.setFont("DejaVu", 12)
            y = height - 50

    c.save()
    return str(output_path)

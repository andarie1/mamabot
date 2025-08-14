from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pathlib import Path

# Регистрируем шрифты один раз при импорте
pdfmetrics.registerFont(TTFont("Comfortaa", "fonts/Comfortaa-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu", "fonts/DejaVuSans.ttf"))

def generate_day_pdf(username: str, content: str, filename: str = "day_with_timmy.pdf") -> str:
    path = Path("assets/pdf") / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    # Вставляем фоновую картинку
    bg_path = Path("assets/backgrounds/background_pdf.png")
    if bg_path.exists():
        c.drawImage(str(bg_path), 0, 0, width=width, height=height, mask='auto')

    # Вставляем логотип в правый верхний угол
    logo_path = Path("assets/backgrounds/timmy_logo.png")
    if logo_path.exists():
        c.drawImage(str(logo_path), width-120, height-120, width=100, height=100, mask='auto')

    # Заголовок шрифтом Comfortaa
    c.setFont("Comfortaa", 28)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(width/2, height-150, f"День с Тимми для {username}")

    # Основной текст шрифтом DejaVu
    c.setFont("DejaVu", 14)
    text = c.beginText(50, height-200)
    for line in content.split('\n'):
        text.textLine(line)
    c.drawText(text)

    c.save()
    return str(path)

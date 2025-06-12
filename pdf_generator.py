from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

FONT_DIR = "fonts"
FONT_FILE = "DejaVuSans.ttf"
FONT_PATH = os.path.join(FONT_DIR, FONT_FILE)

# Регистрируем шрифт (поддерживает кириллицу и emoji частично)
pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))

def generate_pdf(title: str, points: list[str], filename: str = "checklist.pdf"):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 50

    c.setFont("DejaVu", 16)
    c.drawCentredString(width / 2, y, "Советы от мамы к маме")
    y -= 40

    c.setFont("DejaVu", 12)
    c.drawString(50, y, title)
    y -= 30

    for i, point in enumerate(points, 1):
        if y < 100:
            c.showPage()
            y = height - 50
            c.setFont("DejaVu", 12)
        c.drawString(50, y, f"{i}. {point}")
        y -= 20

    c.save()
    print(f"✅ PDF успешно создан: {filename}")

if __name__ == "__main__":
    generate_pdf(
        title="Чеклист: подготовка к детскому саду",
        points=[
            "Сменная одежда и обувь",
            "Папка с документами",
            "Обсудить с ребёнком режим дня",
            "Удобный рюкзачок",
            "Запас носовых платков"
        ],
        filename="checklist_sadik.pdf"
    )

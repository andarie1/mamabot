from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from datetime import datetime
from services.progress_tracker import get_week_progress, get_achievements, get_medal_image

# Регистрируем кириллический шрифт
FONT_PATH = Path("fonts/DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_PATH)))

def generate_progress_report(user_id: int, username: str) -> str:
    week_data = get_week_progress(user_id)
    medals = get_achievements(user_id)

    # Если нет данных — не создаём PDF
    if not week_data and not medals:
        return None

    output_path = Path(f"assets/pdf/{user_id}_progress_report.pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=A4)
    c.setFont("DejaVu", 16)
    c.drawString(100, 800, f"🏆 Прогресс {username} за неделю")
    y = 770

    # === Активность недели ===
    c.setFont("DejaVu", 12)
    if week_data:
        c.drawString(100, y, "📘 Выполненные задания:")
        y -= 25
        for line in week_data:
            c.drawString(100, y, f"— {line}")
            y -= 20
            if y < 100:
                c.showPage()
                c.setFont("DejaVu", 12)
                y = 800
    else:
        c.drawString(100, y, "😔 На этой неделе активности не было.")
        y -= 25
        c.drawString(100, y, "🦝 Тимми по тебе скучает. Возвращайся — он приготовил что-то интересное!")
        y -= 25

    # === Медали ===
    if medals:
        y -= 10
        c.setFont("DejaVu", 12)
        c.drawString(100, y, "🏅 Полученные награды:")
        y -= 25
        for medal in medals:
            c.drawString(100, y, f"• {medal['medal_name']}: {medal['description']}")
            y -= 20

    # === Дата ===
    y -= 20
    c.setFont("DejaVu", 10)
    c.drawString(100, y, f"Дата формирования отчёта: {datetime.now().strftime('%d.%m.%Y')}")
    c.save()

    return str(output_path)

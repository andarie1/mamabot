from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pathlib import Path
import json
from datetime import datetime

def generate_progress_report(user_id: int, username: str) -> str:
    progress_path = Path("data/progress.json")
    output_path = Path(f"assets/pdf/{user_id}_report.pdf")

    if not progress_path.exists():
        return None

    progress = json.loads(progress_path.read_text()).get(str(user_id), [])

    c = canvas.Canvas(str(output_path), pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, f"Отчёт о прогрессе {username} 🏆")
    c.setFont("Helvetica", 12)

    y = 770
    for i, item in enumerate(progress[-10:], 1):
        c.drawString(100, y, f"{i}. {item['activity']} — {item['timestamp']}")
        y -= 25

    c.drawString(100, y - 20, f"Дата отчёта: {datetime.now().strftime('%d.%m.%Y')}")

    c.save()
    return str(output_path)

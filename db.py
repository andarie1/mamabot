import sqlite3
from pathlib import Path
from fpdf import FPDF

DB_PATH = "mamabot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            is_approved INTEGER DEFAULT 0,
            age_group TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_article(title, content, age_group="baby_3_6"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT INTO articles (title, content, age_group) VALUES (?, ?, ?)', (title, content, age_group))
    conn.commit()
    conn.close()

def get_tips_by_age(age_group):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT title, content FROM articles WHERE is_approved = 1 AND age_group = ?', (age_group,))
    results = cur.fetchall()
    conn.close()
    return [{"title": r[0], "content": r[1]} for r in results]

def get_pending_articles():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, title FROM articles WHERE is_approved = 0')
    result = cur.fetchall()
    conn.close()
    return result

def approve_article(article_id, return_article=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if return_article:
        cur.execute('SELECT title, content FROM articles WHERE id = ?', (article_id,))
        row = cur.fetchone()
        article = {"title": row[0], "content": row[1]} if row else None
    else:
        article = None

    cur.execute('UPDATE articles SET is_approved = 1 WHERE id = ?', (article_id,))
    conn.commit()
    conn.close()
    return article

def delete_article(article_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('DELETE FROM articles WHERE id = ?', (article_id,))
    conn.commit()
    conn.close()

def article_to_pdf(title: str, content: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.multi_cell(0, 10, txt=title)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=content)

    pdf_dir = Path("pdfs")
    pdf_dir.mkdir(exist_ok=True)
    filename = pdf_dir / f"{title[:30].replace(' ', '_')}.pdf"
    pdf.output(str(filename))
    return str(filename)

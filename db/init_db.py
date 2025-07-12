import sqlite3
import os

# === Настройка возрастных категорий с числовыми границами ===
AGE_CATEGORIES = {
    "0–2 года": (0, 24),
    "2–4 года": (25, 48),
    "4–6 лет": (49, 72)
}

# === Статьи, которые нужно добавить ===
ARTICLES = [
    {
        "title": "Как помочь ребёнку понять силу слов",
        "description": "Ce să-i spună mama copilului dacă a rostit ceva jignitor",
        "file_path": "pdfs/guides/power_of_words_ru_ro.pdf",
        "ages": ["2–4 года", "4–6 лет"]
    },
    {
        "title": "Играем в уборку с Тимми!",
        "description": "Психологи советуют вовлекать ребёнка в уборку через игру. Тимми учит малышей убирать игрушки с радостью — с помощью волшебного мешочка, таймера и похвалы.",
        "file_path": "pdfs/guides/clean_up_playfully_ru_ro.pdf",
        "ages": ["2–4 года"]
    },
    {
        "title": "Учимся ждать с Тимми!",
        "description": "Навык терпения приходит через игру. Тимми показывает, как ребёнку ждать очередь с радостью, играть в ожидание и учиться спокойствию без слёз.",
        "file_path": "pdfs/guides/wait_your_turn_ru_ro.pdf",
        "ages": ["2–4 года"]
    },
    {
        "title": "Что можно есть детям после 1 года (альтернатива запрещённым продуктам)",
        "description": "Alimente sigure pentru copii de la 1 an, în locul celor interzise",
        "file_path": "pdfs/checklists/alternativa_1_an_ru_ro.pdf",
        "ages": ["0–2 года", "2–4 года"]
    },
    {
        "title": "Когда ребёнок должен начать говорить",
        "description": "Ghid scurt despre când trebuie să înceapă copilul să vorbească și cum îl poți sprijini acasă prin joc și comunicare zilnică",
        "file_path": "pdfs/guides/speech_delay_ru_ro.pdf",
        "ages": ["0–2 года", "2–4 года"]
    },
    {
        "title": "Что бы я не купила для новорождённого, имея опыт с первым ребёнком",
        "description": "Lucruri inutile pe care nu merită să le cumpărați pentru un nou-născut.",
        "file_path": "pdfs/guides/things_not_to_buy_guide_ru_ro.pdf",
        "ages": ["0–2 года"]
    },
    {
        "title": "Чек-лист по подготовке комнаты для новорождённого",
        "description": "Lista completă cu recomandări despre organizarea camerei.",
        "file_path": "pdfs/checklists/preparing_babyroom_cl_ru_ro.pdf",
        "ages": ["0–2 года"]
    },
    {
        "title": "Гид по грудному вскармливанию",
        "description": "Ghid detaliat despre alăptare: semnele atașării corecte.",
        "file_path": "pdfs/guides/breastfeeding_guide_ru_ro.pdf",
        "ages": ["0–2 года"]
    }
]

# === Создание папки для БД ===
os.makedirs("db", exist_ok=True)

# === Подключение к БД ===
conn = sqlite3.connect("db/mamabot_db.db")
cursor = conn.cursor()

# === Удаление старых таблиц ===
cursor.executescript("""
DROP TABLE IF EXISTS age_bindings;
DROP TABLE IF EXISTS age_ranges;
DROP TABLE IF EXISTS library;
""")

# === Создание таблиц ===
cursor.execute("""
CREATE TABLE library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    file_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE age_ranges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    age_from INTEGER NOT NULL,
    age_to INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE age_bindings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL,
    content_id INTEGER NOT NULL,
    age_id INTEGER NOT NULL,
    FOREIGN KEY (age_id) REFERENCES age_ranges(id) ON DELETE CASCADE
)
""")

# === Добавление возрастов ===
for name, (age_from, age_to) in AGE_CATEGORIES.items():
    cursor.execute("""
        INSERT OR IGNORE INTO age_ranges (name, age_from, age_to) VALUES (?, ?, ?)
    """, (name, age_from, age_to))

# === Добавление статей и связей ===
for article in ARTICLES:
    cursor.execute("""
        INSERT INTO library (title, description, file_path) VALUES (?, ?, ?)
    """, (article["title"], article["description"], article["file_path"]))
    library_id = cursor.lastrowid

    for age in article["ages"]:
        cursor.execute("SELECT id FROM age_ranges WHERE name = ?", (age,))
        age_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO age_bindings (content_type, content_id, age_id) VALUES (?, ?, ?)
        """, ("library", library_id, age_id))

conn.commit()
conn.close()
print("✅ База успешно создана и наполнена контентом по новой схеме!")

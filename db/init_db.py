import sqlite3
import os

# Создание папки для базы, если её нет
os.makedirs("db", exist_ok=True)

# Подключение к базе (создаст файл, если его нет)
conn = sqlite3.connect('db/mamabot_db.db')
cursor = conn.cursor()

# Создание таблицы library для библиотеки PDF с полем age_range
cursor.execute("""
CREATE TABLE IF NOT EXISTS library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    file_path TEXT NOT NULL,
    age_range TEXT,  -- возрастной диапазон для фильтрации материалов
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Пример добавления первых записей с возрастом
cursor.executescript("""
INSERT INTO library (title, description, file_path, age_range) VALUES
(
    "Что бы я не купила для новорождённого, имея опыт с первым ребёнком",
    "Lucruri inutile pe care nu merită să le cumpărați pentru un nou-născut.",
    "pdfs/guides/things_not_to_buy_guide_ru_ro.pdf",
    "0–2 года"
),
(
    "Чек-лист по подготовке комнаты для новорождённого",
    "Lista completă cu recomandări despre organizarea camerei.",
    "pdfs/checklists/preparing_babyroom_cl_ru_ro.pdf",
    "0–2 года"
),
(
    "Гид по грудному вскармливанию",
    "Ghid detaliat despre alăptare: semnele atașării corecte.",
    "pdfs/guides/breastfeeding_guide_ru_ro.pdf",
    "0–2 года"
);
""")

conn.commit()
conn.close()

print("✅ База и таблица успешно созданы, первые записи добавлены!")

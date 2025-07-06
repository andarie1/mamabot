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
cursor.executemany("""
INSERT INTO library (title, description, file_path, age_range) VALUES (?, ?, ?, ?)
""", [
    (
        "Первые дни дома",
        "Чек-лист для подготовки дома к малышу.",
        "pdfs/checklist/cl_newborn_prep.pdf",
        "0–6 месяца"
    ),
    (
        "Грудное вскармливание",
        "Полезный гид по началу кормления грудью.",
        "pdfs/guides/breastfeeding_guide.pdf",
        "0–6 месяца"
    )
])

conn.commit()
conn.close()
print("✅ База и таблица успешно созданы, первые записи добавлены!")

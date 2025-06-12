DROP TABLE IF EXISTS tips;

CREATE TABLE tips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age_group TEXT NOT NULL,           -- Ключ: baby_0_1, baby_1_2 и т.д.
    title TEXT NOT NULL,               -- Заголовок совета
    content TEXT NOT NULL              -- Текст совета
);

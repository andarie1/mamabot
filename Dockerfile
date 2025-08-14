# Используем официальный Python-образ
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Устанавливаем переменные окружения для безопасности (по желанию)
# ENV BOT_TOKEN=your_bot_token_here

# Открываем порт (не обязателен для Telegram-бота, но полезен для отладки)
EXPOSE 8000

# Запускаем бота
CMD ["python", "bot.py"]

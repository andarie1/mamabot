import os
from dotenv import load_dotenv
from openai import OpenAI
from services.progress_tracker import get_last_activities

# Загружаем ключ из переменных окружения
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY не установлен в переменных окружения!")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_ai_lesson(user_id: int, age: int = 5, level: str = "начальный") -> str:
    # Получаем последние активности пользователя, чтобы не повторять
    previous = get_last_activities(user_id)
    exclude = ", ".join(previous) if previous else "ничего ещё не делал"

    prompt = (
        f"Ты — Тимми, AI-ассистент. Составь простое задание для ребёнка {age} лет, уровень {level}.\n"
        f"Ребёнок уже делал: {exclude} — не повторяй.\n"
        f"Дай 1 движение, 2 английских слова и 1 творческое задание.\n"
        f"Отвечай дружелюбно и коротко.\n"
        f"Генерируй только задания, которые можно выполнить без внешнего аудио.\n"
        f"Не включай упражнения типа 'услышь', 'пой', 'хлопни', 'если услышишь'."
    )

    # Отправляем запрос в OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content



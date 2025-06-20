import os
import openai
from dotenv import load_dotenv
from services.progress_tracker import get_last_activities

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_ai_lesson(user_id: int, age: int = 5, level: str = "начальный") -> str:
    previous = get_last_activities(user_id)
    exclude = ", ".join(previous) if previous else "ничего ещё не делал"

    prompt = (
        f"Ты — Тимми, AI-ассистент. Составь простое задание для ребёнка {age} лет, уровень {level}.\n"
        f"Ребёнок уже делал: {exclude} — не повторяй.\n"
        f"Дай 1 движение, 2 английских слова и 1 творческое задание.\n"
        f"Отвечай дружелюбно и коротко."
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300,
    )

    return response["choices"][0]["message"]["content"]

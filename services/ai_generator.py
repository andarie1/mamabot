import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from services.progress_tracker import get_last_activities
from services.advice_tracker import get_today_advices, record_advice

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY не установлен в переменных окружения!")

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_ai_lesson(user_id: int, age_range: str = "2–4 года", level: str = "начальный", topic: str = "общие") -> str:
    """
    Генерация AI-задания по теме для указанного возрастного диапазона.
    Темы: "английский", "логика", "арт", "слушаем", "игры", "общие", "ритуал", "совет".
    """

    # Примерное представление возраста в цифре
    age_map = {
        "0–2 года": 1,
        "2–4 года": 3,
        "4–6 лет": 5
    }
    age = age_map.get(age_range, 3)  # значение по умолчанию — 3 года

    previous = get_last_activities(user_id)
    exclude = ", ".join(previous) if previous else "ничего ещё не делал"

    topic_instructions = {
        "английский": "Составь задание по английскому языку (2-3 слова на тему).",
        "логика": "Составь логическую задачу или игру для развития мышления.",
        "арт": "Придумай творческое задание с рисованием или лепкой.",
        "слушаем": "Придумай задание на внимание без использования аудио.",
        "игры": "Придумай простую игру с правилами для малышей.",
        "общие": "Составь простое задание: 1 движение, 2 английских слова, 1 творчество.",
        "ритуал": "Составь короткий ритуал для малыша на вечер или утро, подходящий по возрасту.",
        "совет": "Дай полезный совет родителю по воспитанию малыша в этом возрасте."
    }

    topic_text = topic_instructions.get(topic, topic_instructions["общие"])

    prompt = (
        f"Ты — Тимми, AI-ассистент. Возраст ребёнка: {age_range} (примерно {age} лет), уровень: {level}.\n"
        f"{topic_text}\n"
        f"Ребёнок уже делал: {exclude} — не повторяй.\n"
        f"Отвечай дружелюбно, лаконично, избегай сложных слов.\n"
        f"Задания должны быть выполнимы дома, без оборудования.\n"
        f"Не включай упражнения с аудио или видео."
    )

    log_prompt(user_id, topic, prompt)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def generate_expert_tip(user_id: int, expert: str) -> str:
    """
    Генерирует уникальный совет для родителя от специалиста (логопед, психолог, педиатр),
    с проверкой повторов и лимитом до 3 попыток на генерацию.
    """
    topic = expert.lower()
    today_advices = get_today_advices(user_id, topic)

    if len(today_advices) >= 3:
        return "❗ Ты уже получил максимальное количество советов на сегодня по этой рубрике."

    for attempt in range(3):  # максимум 3 попытки
        prompt = (
            f"Ты — профессиональный {expert} с большим опытом работы с детьми до 6 лет. "
            f"Напиши короткий, но полезный совет для родителей. "
            f"Не используй формат заданий или игр. Дай практическую рекомендацию простыми словами, "
            f"объёмом 2-3 предложения."
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — заботливый и опытный детский специалист."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        advice = response.choices[0].message.content.strip()

        if advice not in today_advices:
            record_advice(user_id, topic, advice)
            return advice

    return "❗ Не удалось сгенерировать новый уникальный совет. Попробуй завтра!"


def log_prompt(user_id: int, topic: str, prompt: str):
    """Записывает все промпты в лог-файл для анализа."""
    log_path = "logs/prompts.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n---\n[{timestamp}] UserID: {user_id} | Topic: {topic}\nPrompt:\n{prompt}\n")

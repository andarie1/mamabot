from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from handlers.start import start_handler
from services.ai_generator import generate_expert_tip
from services.user_profile import (
    get_trial_status,
    _read_users_data,   # читаем общий JSON профилей
    USERS_FILE
)

from datetime import datetime
import json

router = Router()

# === Клавиатура раздела ===
def get_tips_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗣 Совет логопеда"), KeyboardButton(text="🧠 Совет психолога")],
            [KeyboardButton(text="👨‍⚕️ Совет педиатра")],
            [KeyboardButton(text="🔙 Назад в главное меню")]
        ],
        resize_keyboard=True
    )

# === Мягкая проверка триала (ничего не блокируем сейчас) ===
async def check_trial_and_inform(message: types.Message) -> bool:
    status = get_trial_status(message.from_user.id)
    if status == "almost_over":
        await message.answer(
            "⏳ Ваш пробный период заканчивается завтра! Раздел «Советы от профи» остаётся доступным, подписку включим позже 💳."
        )
    # Даже если trial истёк — на текущем этапе советы бесплатны. Ничего не блокируем.
    return True

# === Проверка/фикс суточного лимита советов (1/день на пользователя) ===
def _can_generate_tip_today(user_id: int) -> bool:
    """
    Возвращает True, если сегодня совет ещё не выдавался.
    Если можно — сразу отмечает сегодняшнюю дату в users.json (поле tips_last_gen).
    """
    data = _read_users_data()
    key = str(user_id)
    today = datetime.utcnow().date().isoformat()
    field = "tips_last_gen"

    last = data.get(key, {}).get(field)
    if last == today:
        return False

    data.setdefault(key, {})[field] = today
    USERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return True

# === Вход в раздел ===
@router.message(lambda msg: msg.text == "💡 Советы от профи")
async def show_tips_menu(message: types.Message):
    await check_trial_and_inform(message)
    await message.answer(
        "📑 Полезные советы для родителей от экспертов.\n\n"
        "Ограничение: 1 совет в сутки (любой эксперт).",
        reply_markup=get_tips_keyboard()
    )

# === Общий обработчик с лимитом ===
async def _handle_tip_request(message: types.Message, expert_label: str, expert_key: str):
    # Мягкое уведомление про триал (не блокирует)
    await check_trial_and_inform(message)

    # Проверяем суточный лимит
    if not _can_generate_tip_today(message.from_user.id):
        await message.answer(
            "📅 Лимит на сегодня исчерпан: можно получить только один совет в сутки.\n"
            "Загляни завтра — подготовим новый совет! 😊"
        )
        return

    # Генерируем совет
    await message.answer(f"⏳ Генерирую совет от {expert_label}...")
    tip = generate_expert_tip(user_id=message.from_user.id, expert=expert_key)
    await message.answer(f"{expert_label}:\n\n{tip}")

# === Три кнопки экспертов ===
@router.message(lambda msg: msg.text == "🗣 Совет логопеда")
async def speech_therapist_tip(message: types.Message):
    await _handle_tip_request(message, "🗣 Совет логопеда", "логопед")

@router.message(lambda msg: msg.text == "🧠 Совет психолога")
async def psychologist_tip(message: types.Message):
    await _handle_tip_request(message, "🧠 Совет психолога", "психолог")

@router.message(lambda msg: msg.text == "👨‍⚕️ Совет педиатра")
async def pediatrician_tip(message: types.Message):
    await _handle_tip_request(message, "👨‍⚕️ Совет педиатра", "педиатр")

# === Назад в главное меню ===
@router.message(lambda msg: msg.text == "🔙 Назад в главное меню")
async def go_back_to_main(message: types.Message):
    from handlers.start import start_handler
    await start_handler(message)

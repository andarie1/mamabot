# services/payments_fondy.py
import os
import uuid
import hashlib
import requests
from urllib.parse import urlparse
from typing import Optional, Tuple, Dict

from dotenv import load_dotenv

load_dotenv()

# === Конфиг из .env ===
FONDY_ENDPOINT = os.getenv("FONDY_ENDPOINT", "https://pay.fondy.eu/api/checkout/url/")
FONDY_MERCHANT_ID = os.getenv("FONDY_MERCHANT_ID", "")
FONDY_PASSWORD = os.getenv("FONDY_PASSWORD", "")
FONDY_CURRENCY = os.getenv("FONDY_CURRENCY", "EUR")

# Необязательные — можно оставить пустыми до деплоя
FONDY_SERVER_CALLBACK_URL = os.getenv("FONDY_SERVER_CALLBACK_URL", "")  # https://<domain>/fondy/webhook
FONDY_RESPONSE_URL = os.getenv("FONDY_RESPONSE_URL", "")                # страница "спасибо" / deep‑link

if not FONDY_MERCHANT_ID or not FONDY_PASSWORD:
    raise ValueError("❌ FONDY_MERCHANT_ID и/или FONDY_PASSWORD не заданы в .env")


# === Подпись по правилам Fondy ===
def _fondy_signature(data: Dict[str, object], password: str) -> str:
    """
    Подпись Fondy: sha1( password | concat(sorted(values)) )
    - Исключаем 'signature'
    - Берём только поля с value is not None
    - Сортируем по ключу, конкатенируем значения через '|'
    Документация: https://docs.fondy.eu/docs/page/2/
    """
    filtered = {k: v for k, v in data.items() if k != "signature" and v is not None}
    parts = [password] + [str(filtered[k]) for k in sorted(filtered.keys())]
    raw = "|".join(parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


# === Публичные утилиты ===
def create_payment_link(
    user_id: int,
    plan_key: str,
    amount: float,
    description: str = "Subscription",
    currency: Optional[str] = None,
    response_url: Optional[str] = None,
    server_callback_url: Optional[str] = None,
) -> str:
    """
    Создаёт платёж и возвращает checkout_url.
    order_id = <user_id>:<plan_key>:<rand8>, чтобы затем в вебхуке понять, что покупать и кому.
    """
    cur = (currency or FONDY_CURRENCY).upper()

    if amount <= 0:
        raise ValueError("Fondy: amount должен быть > 0")
    if not FONDY_MERCHANT_ID:
        raise RuntimeError("Fondy: merchant_id не задан")
    if not FONDY_PASSWORD:
        raise RuntimeError("Fondy: password не задан")

    # Корректность URL, если заданы
    resp_url = response_url if response_url is not None else FONDY_RESPONSE_URL
    cb_url = server_callback_url if server_callback_url is not None else FONDY_SERVER_CALLBACK_URL
    for _url in (resp_url, cb_url):
        if _url:
            parsed = urlparse(_url)
            if parsed.scheme not in ("http", "https"):
                raise ValueError(f"Fondy: некорректный URL: {_url}")

    order_id = f"{user_id}:{plan_key}:{uuid.uuid4().hex[:8]}"

    payload: Dict[str, object] = {
        "merchant_id": FONDY_MERCHANT_ID,
        "order_id": order_id,
        "order_desc": description,
        "amount": int(round(amount * 100)),  # в центах
        "currency": cur,
        "response_url": resp_url or None,
        "server_callback_url": cb_url or None,
    }
    payload["signature"] = _fondy_signature(payload, FONDY_PASSWORD)

    resp = requests.post(FONDY_ENDPOINT, json={"request": payload}, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    response = data.get("response", {})
    if response.get("response_status") != "success":
        raise RuntimeError(f"Fondy error: {data}")

    checkout_url = response.get("checkout_url")
    if not checkout_url:
        raise RuntimeError("Fondy: отсутствует checkout_url в ответе")

    return checkout_url


def verify_webhook_signature(payload: Dict[str, object]) -> bool:
    """
    Проверка подписи серверного колбэка Fondy.
    В payload уже приходит 'signature'; пересчитываем и сравниваем.
    """
    if "signature" not in payload:
        return False
    expected = _fondy_signature(payload, FONDY_PASSWORD)
    return expected == payload.get("signature")


def parse_order_id(order_id: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    Разбор order_id формата "<user_id>:<plan_key>:<rand8>".
    Возвращает (user_id, plan_key, rand8) либо (None, None, None).
    """
    try:
        user_s, plan_key, rnd = order_id.split(":")
        return int(user_s), plan_key, rnd
    except Exception:
        return None, None, None

import requests
from bs4 import BeautifulSoup
from db import save_article

def parse_article_from_url(url: str, age_key: str = "baby_3_6") -> str:
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code} — не удалось загрузить статью")

    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string.strip() if soup.title else "Без названия"
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    content = "\n".join(p for p in paragraphs if len(p) > 30)[:2000]

    if not content:
        raise Exception("Не удалось извлечь содержимое статьи")

    save_article(title, content, age_key)
    return title

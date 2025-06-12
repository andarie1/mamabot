import feedparser

# RSS-источники
RSS_FEEDS = {
    "Lifehacker": "https://lifehacker.ru/feed/",
    "TechCrunch": "http://feeds.feedburner.com/TechCrunch/"
}

def fetch_articles():
    results = []

    for source_name, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link
            summary = getattr(entry, "summary", "Без описания")

            results.append({
                "source": source_name,
                "title": title,
                "summary": summary.strip().replace('\n', ' '),
                "link": link
            })

    return results

# Запуск для вывода в консоль
if __name__ == "__main__":
    articles = fetch_articles()

    if not articles:
        print("Статей нет, возможно, источник пуст.")
    else:
        for article in articles:
            print(f"🔹 <{article['source']}> {article['title']}")
            print(f"📝 {article['summary']}")
            print(f"🔗 {article['link']}\n{'-'*60}\n")


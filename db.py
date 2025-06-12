import aiosqlite

DB_PATH = "mamabot.db"

async def get_tips_by_age(age_group: str):
    tips = []
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT title, content FROM tips WHERE age_group = ?", (age_group,)) as cursor:
            async for row in cursor:
                tips.append({"title": row[0], "content": row[1]})
    return tips

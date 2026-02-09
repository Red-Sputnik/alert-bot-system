import asyncio
from typing import Set
from aiogram import Bot
from database import Database
from mchs_rss import get_events
from logger import logger

CHECK_INTERVAL = 300  # 5 минут
processed_events: Set[str] = set()

async def rss_monitor(bot: Bot, db: Database):
    logger.info("Модуль автоматического мониторинга МЧС запущен")

    while True:
        try:
            events = get_events()

            for event in events:
                event_id = event["link"]

                if event_id in processed_events:
                    continue

                await process_event(bot, db, event)
                processed_events.add(event_id)

        except Exception as e:
            logger.error(f"Ошибка мониторинга RSS МЧС: {e}")

        await asyncio.sleep(CHECK_INTERVAL)


async def process_event(bot: Bot, db: Database, event: dict):
    title = event["title"]
    regions = event["regions"]
    link = event["link"]
    is_demo = event.get("is_demo", False)

    db.add_alert(
        title=title,
        regions=regions,
        link=link,
        is_demo=is_demo
    )

    logger.warning(
        f"Новое предупреждение МЧС: {title} | регионы={regions} | demo={is_demo}"
    )

    users = db.get_users_by_regions(regions)

    for telegram_id in users:
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=(
                    "⚠️ *ВНИМАНИЕ! Экстренное предупреждение МЧС*\n\n"
                    f"{title}\n\n"
                    f"Затронутые регионы:\n"
                    + "\n".join(f"• {r}" for r in regions)
                    + f"\n\nПодробнее: {link}"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(
                f"Ошибка отправки пользователю {telegram_id}: {e}"
            )



import asyncio
from aiogram import Bot, Dispatcher

from handlers import user_router
from database import Database
from notifier import rss_monitor
from config import BOT_TOKEN


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    db = Database()

    dp.include_router(user_router)

    asyncio.create_task(rss_monitor(bot, db))

    await dp.start_polling(bot)


import asyncio
from aiogram import Bot, Dispatcher
from logger import logger
from aiogram import BotCommand

from handlers import user_router
from database import Database
from notifier import rss_monitor
from config import BOT_TOKEN


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    db = Database()

    await bot.set_my_commands([
        BotCommand(command="start", description="Регистрация в системе оповещения"),
        BotCommand(command="help", description="Справка по работе бота"),
        BotCommand(command="stats", description="Статистика (администратор)"),
        BotCommand(command="alert", description="Ручное оповещение (администратор)")
    ])

    dp.include_router(user_router)

    asyncio.create_task(rss_monitor(bot, db))

    logger.info("Бот запущен и ожидает сообщения")

    await dp.start_polling(bot)



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")

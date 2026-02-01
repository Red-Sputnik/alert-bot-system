from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import asyncio

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def handle_start(message: Message):
   await message.answer("Hello, world!")

async def main():
   await dp.start_polling(bot)

if __name__ == "__main__":
   asyncio.run(main())
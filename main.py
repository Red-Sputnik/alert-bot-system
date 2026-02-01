from aiogram import Bot, Dispatcher, F
from handlers import user
import asyncio

async def main():
   bot = Bot(token='8252517925:AAEFdJpMStFjdI2nx_dIcp4F0TQWexSnmPo')
   dp = Dispatcher()
   dp.include_router(user)
   await dp.start_polling(bot)

if __name__ == '__main__':
   try:
       asyncio.run(main())
   except KeyboardInterrupt:
       pass
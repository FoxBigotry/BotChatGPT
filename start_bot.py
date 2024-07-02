import asyncio
from aiogram import Bot, Dispatcher
from settings import settings
from handlers.handlers import router

dp = Dispatcher()


async def main():
    bot = Bot(token=settings.TG_KEY)
    dp.include_router(router)
    print("Start polling")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('бот выключен')
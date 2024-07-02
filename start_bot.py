import asyncio
from aiogram import Bot, Dispatcher
from settings import settings
from handlers.messages import router_message
from handlers.commands import router_command

dp = Dispatcher()


async def main():
    bot = Bot(token=settings.TG_KEY)
    router_command.include_router(router_message)
    dp.include_router(router_command)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('бот выключен')

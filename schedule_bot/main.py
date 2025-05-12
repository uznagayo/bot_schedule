import asyncio
from aiogram import Bot, Dispatcher
from handlers import all_routers
from handlers.config import BOT_TOKEN
from filters import IsRegisteredMiddleware

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(IsRegisteredMiddleware())
    dp.callback_query.middleware(IsRegisteredMiddleware())

    for router in all_routers:
        dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
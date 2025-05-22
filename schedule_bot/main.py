import asyncio
from aiogram import Bot, Dispatcher
from handlers import all_routers
from handlers.config import BOT_TOKEN
from filters import IsRegisteredMiddleware
from handlers.reminders import reminders


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(IsRegisteredMiddleware())
    dp.callback_query.middleware(IsRegisteredMiddleware())
    
    try:
        asyncio.create_task(reminders(bot))
        print('done')
    except Exception as e:
        print('not done', e)



    for router in all_routers:
        dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
import asyncio
from aiogram import Bot, Dispatcher
from handlers import all_routers
from handlers.config import settings
from filters import IsRegisteredMiddleware
from handlers.reminders import reminders_req, reminders_rand
from loguru import logger


async def main():
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp.message.middleware(IsRegisteredMiddleware())
    dp.callback_query.middleware(IsRegisteredMiddleware())
    
    try:

        asyncio.create_task(reminders_req(bot))
        logger.success('done_req\n')

        asyncio.create_task(reminders_rand(bot))
        logger.success('done_rand\n')        
    
    except Exception as e:
        logger.error('not done\n', e)



    for router in all_routers:
        dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
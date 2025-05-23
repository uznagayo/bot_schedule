from datetime import datetime, timedelta
import aiogram
from aiogram import types, Router, F, Bot
import asyncio
from utils.db import get_telegram_ids

reminders_router = Router()


# tomorrow = today + timedelta(days=1)
# tomorrow_str = tomorrow.strftime("%Y-%m-%d")


# if today.weekday() == 4 and today.hour() == 12:


async def reminders(bot: Bot):
    # today = datetime.now()
    # today_str = today.strftime("%Y-%m-%d")
    while True:
        today = datetime.now()
        # print(today)
        # print(today.weekday(), today.hour, today.minute)
        today_str = today.strftime("%Y-%m-%d")
        if today.weekday() == 4 and today.hour == 16 and today.minute == 30:
            await select_schedule_rem(bot)

        await asyncio.sleep(60)


async def select_schedule_rem(bot: Bot):
    ids = get_telegram_ids("employee")
    for id in ids:
        try:
            await bot.send_message(
                chat_id=id, text="Пора выбрать смены, если еще не выбраны"
            )
            print("message send to", id)
        except Exception as e:
            await print(id, e)
    # print('trying')

    # try:
    #     await bot.send_message(chat_id=357434524, text='Пора выбрать смены, если еще не выбраны')

    # except Exception as e:
    #     print(e)

from datetime import datetime
from aiogram import Router, Bot
import asyncio
from utils.db import get_telegram_ids, get_ancient_sheets, get_users_data
from loguru import logger
from .callback_classes import AncientDutiesCb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .config import channel_id


reminders_router = Router()


# tomorrow = today + timedelta(days=1)
# tomorrow_str = tomorrow.strftime("%Y-%m-%d")


# if today.weekday() == 4 and today.hour() == 12:


async def reminders(bot: Bot):
    # today = datetime.now()
    # today_str = today.strftime("%Y-%m-%d")
    while True:
        today = datetime.now()
        today.strftime("%Y-%m-%d")

        if today.hour == 22:
            await ancient_kassa_rem(bot)
            # await bot.send_message(chat_id=357434524, text='test')

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
            logger.info(f"message send to {id}")
        except Exception as e:
            await logger.exception(id, e)


async def ancient_kassa_rem(bot: Bot):
    today = datetime.now()
    time = today.strftime("%Y-%m-%d, %H-%M-%S")
    keybroad = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Сделано",
                    callback_data=AncientDutiesCb(
                        dutie="kassa_check", conf=True, time_mark=time
                    ).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Не сделано",
                    callback_data=AncientDutiesCb(
                        dutie="kassa_check",
                        conf=False,
                        time_mark=time,
                    ).pack(),
                )
            ],
        ]
    )

    today_str = today.strftime("%Y-%m-%d")
    __, __, admin_id, __, __, __ = get_ancient_sheets(time=True, date=today_str)
    data = get_users_data(user_id=admin_id[0])
    if not data:
        return
    else:
        __, name, telegram_id = data[0]
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text="Пора считать кассу, и сверить безнал",
                reply_markup=keybroad,
            )
            await bot.send_message(
                chat_id=channel_id,
                text=f"kassa_check message sended to {name} in {time}"
            )
            logger.info(f"message send to {name}")
        except Exception as e:
            await logger.exception(name, telegram_id, e)


async def sheet_rem(bot: Bot):
    pass

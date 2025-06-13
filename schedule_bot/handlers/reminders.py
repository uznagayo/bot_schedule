from datetime import datetime
from aiogram import Router, Bot
import asyncio
from utils.db import get_telegram_ids, get_ancient_sheets, get_users_data
from loguru import logger
from .callback_classes import AncientDutiesCb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .config import channel_id
from .duties import ancient_admin_duties, junior_admin_duties, ancient_admin_duties_cb
from random import choice, randrange


reminders_router = Router()


def choose_dutie():
    key = choice(ancient_admin_duties)
    value = ancient_admin_duties_cb[ancient_admin_duties.index(key)]
    dutie = {key: value}
    return dutie


flowers = {"Нужно полить цветы":
              "flowers_rem"}

kassa = {"Пора считать кассу, и сверить безнал":
              "kassa_check"}

async def reminders_req(bot: Bot):
    while True:
        today = datetime.now()
        today.strftime("%Y-%m-%d")

        if (today.weekday() == 3 or today.weekday() == 0) and today.hour == 9 and today.minute == 30:
            await ancient_universal_rem(duties=flowers, bot=bot)

        if today.hour == 17 and today.minute == 30:
            await ancient_universal_rem(duties=kassa, bot=bot)

        if today.weekday() == 4 and today.hour == 13 and today.minute == 30:
            await select_schedule_rem(bot)

        await asyncio.sleep(60)


async def reminders_rand(bot: Bot):
    while True:
        today = datetime.now()
        today.strftime("%Y-%m-%d")        
        mins = randrange(3600, 5400)

        if today.hour >= 6 and today.hour <=17:
            await ancient_universal_rem(duties=choose_dutie(), bot=bot)

        await asyncio.sleep(mins)





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

async def ancient_universal_rem(duties: dict[str, str], bot: Bot):
    dutie_str = str(list(duties.keys())[0])
    dutie_cb = str(list(duties.values())[0])


    today = datetime.now()
    time = today.strftime("%Y-%m-%d, %H-%M-%S")
    keybroad = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Сделано",
                    callback_data=AncientDutiesCb(
                        dutie=dutie_cb, conf=True, time_mark=time
                    ).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Не сделано",
                    callback_data=AncientDutiesCb(
                        dutie=dutie_cb,
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
                text=f"Это сообщение означает, что тебе пора сделать кое-что:\n{dutie_str}",
                reply_markup=keybroad,
            )
            await bot.send_message(
                chat_id=channel_id,
                text=f"{dutie_cb} message sended to {name} in {time}"
            )
            logger.info(f"message send to {name}")
        except Exception as e:
            await logger.exception(name, telegram_id, e)


async def sheet_rem(bot: Bot):
    pass

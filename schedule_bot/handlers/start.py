from aiogram import Router, types, Bot
from aiogram.filters import Command
from utils.db import send_meme, get_user_name, get_schedule, get_user_id
from .commands import start_true
from datetime import datetime, timedelta
from loguru import logger

start_router = Router()


@start_router.message(Command("start"))
async def start_command(message: types.Message):
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    id = message.from_user.id
    user_id = get_user_id(id)
    name = get_user_name(user_id)
    schedule = get_schedule(user_id, start_of_week)
    schedule_true = 'Твое расписание на неделю:\n'
    if not schedule:
        schedule_true = 'На этой неделе у тебя нет смен'
    else:
        for __, day, date, start, end in schedule:
            schedule_true += f"{day} ({date}) - {start}–{end}\n"
    hello = f'Привет {name}!\n{schedule_true}'
    await message.answer(text=hello, reply_markup=start_true(message))


@start_router.message(Command("send_meme"))
async def send_meme_handler(message: types.Message):
    meme = send_meme()
    logger.info(f'{message.from_user.first_name} заказал мем')
    await message.answer_photo(photo=meme, caption="Вот тебе мем, епт")


@start_router.message(Command("id"))
async def telegram_id_getting(message: types.Message, bot: Bot):
    id = message.chat.id
    name = message.from_user.username
    print(f"chat id {id} name {name}")
    await bot.send_message(chat_id=id, text=f"chat id {id} name {name} id confirmed")

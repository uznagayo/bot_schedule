from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from utils.db import send_meme, get_user_name, get_schedule, get_user_id
from .commands import start_true
from datetime import datetime, timedelta

start_router = Router()


@start_router.message(Command("start"))
async def start_command(message: types.Message):
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    id = message.from_user.id
    name, user_id = get_user_name(id), get_user_id(id)
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
    print(message.from_user.first_name, "заказал мем") # type: ignore
    await message.answer_photo(photo=meme, caption="Вот тебе мем, епт")

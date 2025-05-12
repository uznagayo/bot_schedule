from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from utils.db import get_user_id, get_schedule, get_next_week_sheeets

schedule_router = Router()


@schedule_router.message(F.text == "Мое расписание")
async def my_schedule(message: types.Message):
    await message.delete()
    await this_week(message)


async def this_week(message):
    user_id = get_user_id(message.from_user.id)
    if not user_id:
        await message.answer("Ты ещё не зарегистрирован в системе.")
        return

    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    schedule = get_schedule(user_id, start_of_week)

    if not schedule:
        await message.answer("На этой неделе у тебя пока нет смен.")
        return

    message1 = "Твое расписание на текущую неделю:\n"
    for date, start, end in schedule:
        weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
        message1 += f"{weekday} ({date}): {start}–{end}\n"

    await message.answer(message1)


@schedule_router.message(F.text == "По сменам")
async def send_shedule(message: types.Message):
    await new_schedule(message)
    await message.delete()


async def new_schedule(message: types.Message):
    shift_id, next_week_names, dates = get_next_week_sheeets()
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    for i in range(len(shift_id)):
        time = ",".join(next_week_names[i].split(" ")[1:])
        button = InlineKeyboardButton(
            text=next_week_names[i],
            callback_data=(f"new_shift_key,{dates[i]},{shift_id[i]},{time}"),
        )
        keybroad.inline_keyboard.append([button])
    if not shift_id:
        await message.answer("Свободных смен нету")
    else:
        await message.answer("Сободные смены:", reply_markup=keybroad)

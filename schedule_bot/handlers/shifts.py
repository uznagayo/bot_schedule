from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from utils.db import get_user_id, get_schedule, get_next_week_sheeets, get_user_role

schedule_router = Router()


# @schedule_router.message(F.text == "Мое расписание")
# async def my_schedule(message: types.Message):
#     print(message.from_user.first_name, 'act_send_my_shedule')
#     await message.delete()
#     await this_week(message)


async def this_week(callback: types.CallbackQuery):
    user_id = get_user_id(callback.from_user.id)
    if not user_id:
        await callback.message.answer("Ты ещё не зарегистрирован в системе.")
        return

    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    schedule = get_schedule(user_id, start_of_week)

    if not schedule:
        await callback.message.answer("На этой неделе у тебя пока нет смен.")
        return

    # message1 = "Твое расписание на текущую неделю:\n"
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    for id, day, date, start, end in schedule:
        
        button = InlineKeyboardButton(
            text=f'{day} ({date}) - {start}–{end}',
            callback_data=(f"shift_key,{id}"),
        )
        keybroad.inline_keyboard.append([button])

    keybroad.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data="back_to_main_menu",
                )
            ]
        )

    await callback.message.edit_text(text="Твое расписание на текущую неделю")
    await callback.message.edit_reply_markup(reply_markup=keybroad)


# @schedule_router.message(F.text == "По сменам")
# async def send_shedule(message: types.Message):
#     print(message.from_user.first_name, 'act_send_new_shedule')
#     await new_schedule(message)
#     await message.delete()


def new_schedule():

    shift_id, next_week_names, dates = get_next_week_sheeets()
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    for i in range(len(shift_id)):
        time = ",".join(next_week_names[i].split(" ")[1:])
        button = InlineKeyboardButton(
            text=next_week_names[i],
            callback_data=(f"new_shift_key,{dates[i]},{shift_id[i]},{time}"),
        )
        keybroad.inline_keyboard.append([button])
    keybroad.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="back_to_main_menu",
            )
        ]
    )
    return keybroad


# def shift_swap

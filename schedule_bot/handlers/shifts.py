from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from utils.db import (
    get_user_id,
    get_schedule,
    get_next_week_sheeets,
    get_user_role,
    get_shift_id_onday,
)

from .commands import start_true
schedule_router = Router()


# @schedule_router.message(F.text == "Мое расписание")
# async def my_schedule(message: types.Message):
#     print(message.from_user.first_name, 'act_send_my_shedule')
#     await message.delete()
#     await this_week(message)


async def this_week(callback: types.CallbackQuery):
    user_id = get_user_id(callback.from_user.id)
    if not user_id:
        await callback.message.answer("Ты ещё не зарегистрирован в системе.")  # type: ignore
        return

    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    schedule = get_schedule(user_id, start_of_week)

    if not schedule:
        await callback.answer("На этой неделе у тебя пока нет смен.", show_alert=True)
        await callback.message.edit_text("Главное меню")
        await callback.message.edit_reply_markup(reply_markup=start_true(callback))
        return

    # message1 = "Твое расписание на текущую неделю:\n"
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    for id, day, date, start, end in schedule:

        button = InlineKeyboardButton(
            text=f"{day} ({date}) - {start}–{end}",
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

    await callback.message.edit_text(text="Твое расписание на текущую неделю")  # type: ignore
    await callback.message.edit_reply_markup(reply_markup=keybroad)  # type: ignore


# @schedule_router.message(F.text == "По сменам")
# async def send_shedule(message: types.Message):
#     print(message.from_user.first_name, 'act_send_new_shedule')
#     await new_schedule(message)
#     await message.delete()


# def new_schedule():

#     shift_id, days, times, dates = get_next_week_sheeets()
#     keybroad = InlineKeyboardMarkup(inline_keyboard=[])
#     for i in range(len(shift_id)):

#         button = InlineKeyboardButton(
#             text=days[i],
#             callback_data=(f"new_shift_key,{dates[i]},{shift_id[i]},{times[i]}"),
#         )
#         keybroad.inline_keyboard.append([button])
#     keybroad.inline_keyboard.append(
#         [
#             InlineKeyboardButton(
#                 text="Назад",
#                 callback_data="back_to_main_menu",
#             )
#         ]
#     )
#     return keybroad


# def shift_swap


async def new_schedule_days(callback: types.CallbackQuery):
    __, days, __, dates = get_next_week_sheeets()
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    days_ctrl = []
    buttons = []
    for i in range(len(days)):
        day = days[i]
        if day not in days_ctrl:
            days_ctrl.append(day)
            buttons.append(
                InlineKeyboardButton(
                    text=day, callback_data=(f"new_shift_day_key,{day}")
                ),
            )
        else:
            continue

    buttons.append(
        InlineKeyboardButton(
            text="Назад",
            callback_data="back_to_main_menu",
        ),
    )
    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i : i + 2])

    text = f"Сободные смены: {dates[0]} -- {dates[-1]}"
    await callback.message.edit_text(text)
    await callback.message.edit_reply_markup(reply_markup=keybroad)


def new_schedule(shift_ids):
    # print(shift_ids)

    shift_id, __, times, dates = get_next_week_sheeets()
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    buttons = []
    for i in shift_ids:
        if i in shift_id:
            k = shift_id.index(i)
        else:
            continue
        # print(k)
        # print(days[k])
        buttons.append(
            InlineKeyboardButton(
                text="-".join(times[k].split(",")),
                callback_data=(f"new_shift_key,{dates[k]},{shift_id[k]},{times[k]}"),
            ),
        )

    buttons.append(
        InlineKeyboardButton(
            text="Назад",
            callback_data=(f"new_schedule_day_key"),
        ),
    )

    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i : i + 2])
    return keybroad

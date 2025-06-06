from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from utils.db import (
    get_user_id,
    get_schedule,
    get_next_week_sheeets,
    get_requests_id,
)

from .commands import start_true
from .callback_classes import CalendarCb
import calendar

schedule_router = Router()





async def this_week(callback: types.CallbackQuery):
    user_id = get_user_id(callback.from_user.id)
    if not user_id:
        await callback.message.answer("Ты ещё не зарегистрирован в системе.")  
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

    await callback.message.edit_text(text="Твое расписание на текущую неделю") 
    await callback.message.edit_reply_markup(reply_markup=keybroad) 


async def get_income_requests(callback: types.CallbackQuery):
    requests = get_requests_id(callback.from_user.id)
    if not requests:
        await callback.answer("Входящих запросов нет", show_alert=True)
        await callback.message.edit_text("Главное меню")
        await callback.message.edit_reply_markup(reply_markup=start_true(callback))
        return
    
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    for id, name, date, start, end in requests:

        button = InlineKeyboardButton(
            text=f"{name} ({date}) - {start}–{end}",
            callback_data=(f"income_request,{id}"),
        )
        keybroad.inline_keyboard.append([button])

    keybroad.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="shift_exchenge_requests_key",
            )
        ]
    )

    await callback.message.edit_text(text="Входящие запросы") 
    await callback.message.edit_reply_markup(reply_markup=keybroad) 


async def get_outcome_requests(callback: types.CallbackQuery):
    requests = get_requests_id(callback.from_user.id, way = False)
    if not requests:
        await callback.answer("Исходящих запросов нет", show_alert=True)
        await callback.message.edit_text("Главное меню")
        await callback.message.edit_reply_markup(reply_markup=start_true(callback))
        return
    
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    for id, name, date, start, end in requests:

        button = InlineKeyboardButton(
            text=f"{name} ({date}) - {start}–{end}",
            callback_data=(f"outcome_request,{id}"),
        )
        keybroad.inline_keyboard.append([button])

    keybroad.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="shift_exchenge_requests_key",
            )
        ]
    )

    await callback.message.edit_text(text="Исходящие запросы") 
    await callback.message.edit_reply_markup(reply_markup=keybroad) 


async def new_schedule_days(callback: types.CallbackQuery):
    __, days, __, dates = get_next_week_sheeets()
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    days_ctrl = []
    buttons = []
    for i in range(len(days)):
        day = days[i]
        if day == "Внеочередная":
            continue
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
            callback_data=("new_schedule_day_key"),
        ),
    )

    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i : i + 2])
    return keybroad

def generate_calendar(selected_days: set[int] = None, time: bool = True) -> InlineKeyboardMarkup:
    if selected_days is None:
        selected_days = set()

    now = datetime.now()
    year, month = now.year, now.month
    
    month_cal = calendar.monthcalendar(year, month)
    

    buttons = []

    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    buttons.append([
        InlineKeyboardButton(text=day, callback_data=CalendarCb(action="ignore", day=0).pack(),)
        for day in week_days
    ])

    for week in month_cal:
        week_buttons = []
        for day in week:
            if day == 0:
                week_buttons.append(
                    InlineKeyboardButton(text=" ", callback_data=CalendarCb(action="ignore", day=0).pack(),),
                )
            else:
                if day in selected_days:
                    text = f'{day}✅'
                    week_buttons.append(InlineKeyboardButton(
                        text=text,
                        callback_data=CalendarCb(action="delete", day=str(day), time=time).pack(),),)
                else:
                    text = f'{day}'
                    week_buttons.append(InlineKeyboardButton(
                        text=text,
                        callback_data=CalendarCb(action="select", day=str(day), time=time).pack(),),)
        buttons.append(week_buttons)

    buttons.append([
        InlineKeyboardButton(
            text="Назад",
            callback_data="back_to_main_menu",
        ),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
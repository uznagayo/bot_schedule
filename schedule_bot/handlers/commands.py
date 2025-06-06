from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.db import get_user_role
from .callback_classes import AssignNewJun, CalendarCb



def start_true(message: types.Message):
    role = get_user_role(message.from_user.id)
    user_id = message.from_user.id
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    


    buttons = [
            InlineKeyboardButton(text="По сменам", callback_data="new_schedule_day_key"),
            InlineKeyboardButton(text="Мои смены", callback_data="my_schedule_key"),
            InlineKeyboardButton(text="Запросы на обмен", callback_data="shift_exchenge_requests_key"),
            InlineKeyboardButton(text="Расписание на неделю", callback_data="schedule_week_key"),
        ]

    if role != "employee":
        buttons.append(
            InlineKeyboardButton(text="Вызвать младшего", callback_data="emploee_summon_key"),
            )
            # InlineKeyboardButton(text="Мое расписание", callback_data="my_schedule_key"),
            # InlineKeyboardButton(text="Расписание на сегодня", callback_data="today_schedule_key"),
        buttons.append(
            InlineKeyboardButton(text="Поставить младшего на сегодня", callback_data=AssignNewJun(action="run", user_id=0, start=0, end=0).pack()),)
        buttons.append(
            InlineKeyboardButton(text="Смены дневных", callback_data=CalendarCb(action="show", day=0, time=True).pack()),)
        buttons.append(
            InlineKeyboardButton(text="Смены ночных", callback_data=CalendarCb(action="show", day=0, time=False).pack()),
            )
        
    
    if user_id == 357434524:
        buttons.append(
            
                InlineKeyboardButton(text="Hash", callback_data="hash_key"),
            
        )
    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i:i + 2])
    return keybroad

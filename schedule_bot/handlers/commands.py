from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.db import get_user_role

def start_true(message: types.Message):
    role = get_user_role(message.from_user.id)
    user_id = message.from_user.id
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    print(role)


    buttons = [
            InlineKeyboardButton(text="По сменам", callback_data="new_schedule_day_key"),
            InlineKeyboardButton(text="Мое расписание", callback_data="my_schedule_key"),
        ]

    if role != "employee":
        buttons.append(
            InlineKeyboardButton(text="Вызвать младшего", callback_data="emploee_summon_key"),
            )
            # InlineKeyboardButton(text="Мое расписание", callback_data="my_schedule_key"),
           # InlineKeyboardButton(text="Расписание на сегодня", callback_data="today_schedule_key"),
        
    
    if user_id == 357434524:
        buttons.append(
            
                InlineKeyboardButton(text="Hash", callback_data="hash_key"),
            
        )
    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i:i + 2])
    return keybroad

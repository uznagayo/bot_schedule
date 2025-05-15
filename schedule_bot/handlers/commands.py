from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start(message: types.Message):
    user_id = message.from_user.id
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    buttons = [
        InlineKeyboardButton(text="По сменам", callback_data="new_schedule_key"),
        InlineKeyboardButton(text="Мое расписание", callback_data="my_schedule_key"),
    ]
    # if user_id == 357434524:
    #     buttons.append(
    #         [
    #             InlineKeyboardButton(text="Hash", callback_data="hash_key"),
    #         ]
    #     )
    keybroad.inline_keyboard.append(buttons)
    return keybroad

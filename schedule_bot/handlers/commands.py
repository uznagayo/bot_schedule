from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.db import get_user_role
from .callback_classes import AssignNewJun, CalendarCb, HashKeyAdmin, HashActions


def buttons(admin: bool = True) -> InlineKeyboardMarkup:
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    buttons = []
    buttons_jun = [
        InlineKeyboardButton(text="По сменам", callback_data="new_schedule_day_key"),
        InlineKeyboardButton(text="Мои смены", callback_data="my_schedule_key"),
        InlineKeyboardButton(
            text="Запросы на обмен", callback_data="shift_exchenge_requests_key"
        ),
        InlineKeyboardButton(
            text="Назад",
            callback_data="back_to_main_menu",
        ),
    ]

    buttons_ancient = [
        InlineKeyboardButton(
            text="Вызвать младшего", callback_data="emploee_summon_key"
        ),
        InlineKeyboardButton(
            text="Поставить младшего на сегодня",
            callback_data=AssignNewJun(action="run", user_id=0, start=0, end=0).pack(),
        ),
        InlineKeyboardButton(
            text="Смены дневных",
            callback_data=CalendarCb(action="show", day=0, time=True).pack(),
        ),
        InlineKeyboardButton(
            text="Смены ночных",
            callback_data=CalendarCb(action="show", day=0, time=False).pack(),
        ),
        InlineKeyboardButton(
            text="Назад",
            callback_data="back_to_main_menu",
        ),
        InlineKeyboardButton(
            text="Зыкрытие смены",
            callback_data="start_shift_closing"
        ),
    ]

    if not admin:
        buttons.extend(buttons_jun)
    if admin:
        buttons.extend(buttons_ancient)

    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i : i + 2])

    return keybroad


def start_true(message: types.Message):
    role = get_user_role(message.from_user.id)
    user_id = message.from_user.id
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])

    buttons = []

    buttons_jun = [
        InlineKeyboardButton(text="По сменам", callback_data="new_schedule_day_key"),
        InlineKeyboardButton(text="Мои смены", callback_data="my_schedule_key"),
        InlineKeyboardButton(
            text="Запросы на обмен", callback_data="shift_exchenge_requests_key"
        ),
    ]

    if role == "employee":
        buttons.extend(buttons_jun)

    elif role == "user":
        return InlineKeyboardMarkup(inline_keyboard=[
            InlineKeyboardButton(text="Ниче")
        ])

    else:
        buttons.extend(
            [
                InlineKeyboardButton(
                    text="Функционал младшего", callback_data="but_key:jun"
                ),
                InlineKeyboardButton(
                    text="Функционал старшего", callback_data="but_key:ancient"
                ),
            ]
        )

    if user_id == 357434524:
        buttons.append(
            InlineKeyboardButton(
                text="Фель",
                callback_data=HashActions(action="buttons").pack(),
            ),
        )

    buttons.append(
        InlineKeyboardButton(
            text="Расписание на неделю", callback_data="schedule_week_key"
        ),
    )
    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i : i + 2])
    return keybroad

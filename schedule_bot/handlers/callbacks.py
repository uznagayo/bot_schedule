from aiogram import Router, types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import sqlite3, csv, os
from .config import DB_PATH
from utils.db import get_user_id, get_next_week_sheeets, get_user_role, delete_shift_not
from .shifts import new_schedule, this_week
from .commands import start


callbacks_router = Router()


@callbacks_router.callback_query(lambda c: c.data.startswith("new_shift_key"))
async def callback_message(callback: CallbackQuery):
    user_id = get_user_id(callback.from_user.id)
    if not user_id:
        await callback.answer("Ты не зарегистрирован.")
        return

    data = callback.data

    _, date_str, shift_id, start_time, end_time = data.split(",")
    print(
        callback.from_user.first_name,
        "choose",
        date_str,
        shift_id,
        start_time,
        end_time,
    )
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
        INSERT OR REPLACE INTO schedule (user_id, date, shift_id, actual_start, actual_end)
        VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, date_str, int(shift_id), start_time, end_time),
        )
    await callback.answer("Смена добавлена!")
    await callback.message.answer(
        f"Выбрано: {date_str} — смена {start_time}-{end_time}"
    )
    await callback.message.edit_reply_markup(reply_markup=new_schedule())


@callbacks_router.callback_query(lambda c: c.data == "my_schedule_key")
async def my_schedule(callback: CallbackQuery):
    print(callback.from_user.first_name, "act_send_my_shedule")
    await this_week(callback)


@callbacks_router.callback_query(lambda c: c.data == "new_schedule_key")
async def send_shedule(callback: CallbackQuery):
    print(callback.from_user.first_name, "act_send_new_shedule")
    user_role = get_user_role(callback.from_user.id)
    if user_role == "ancient":
        await callback.answer("Эта кнопка не тебе")
        return

    if not new_schedule():
        await callback.message.answer("Свободных смен нету")
    else:
        await callback.message.edit_text("Сободные смены:")
        await callback.message.edit_reply_markup(reply_markup=new_schedule())


@callbacks_router.callback_query(lambda c: c.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню")
    await callback.message.edit_reply_markup(reply_markup=start(callback))


@callbacks_router.callback_query(lambda c: c.data == "hash_key")
async def hash(callback: CallbackQuery):
    await callback.message.answer(
        "Введи начальную и конечную дату в формате ГГГГ-ММ-ДД через пробел и не забудь кодовое слово!"
    )


@callbacks_router.callback_query(lambda c: c.data.startswith("shift_key"))
async def shift_key(callback: CallbackQuery):
    data = callback.data
    _, id = data.split(",")
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    buttuns = [
        InlineKeyboardButton(
            text="Удалить смену",
            callback_data=f"delete_shift,{id}",
        ),
        InlineKeyboardButton(
            text="Отдать смену",
            callback_data=f"give_shift,{id}",
        ),
        InlineKeyboardButton(
            text="Назад",
            callback_data="my_schedule_key",
        ),
    ]
    keybroad.inline_keyboard.append(buttuns)
    await callback.message.edit_text("Что сделать хочешь?")
    await callback.message.edit_reply_markup(reply_markup=keybroad)


@callbacks_router.callback_query(lambda c: c.data.startswith("delete_shift"))
async def delete_shift(callback: CallbackQuery):
    data = callback.data
    _, id = data.split(",")
    try:
        delete_shift_not(id)
        await callback.answer("Смена удалена!")
        await callback.message.edit_text("Главное меню")
        await callback.message.edit_reply_markup(reply_markup=start(callback))
        await callback.bot.send_message(
            chat_id=357434524, text=f"{callback.from_user.first_name} удалил смену {id}"
        )
    except Exception as e:
        print(e)
        await callback.answer("Ошибка удаления смены. Попробуй позже.")

from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import sqlite3, csv, os
from .config import DB_PATH
from utils.db import get_user_id, get_next_week_sheeets
from .schedule import new_schedule


callbacks_router = Router()


@callbacks_router.callback_query(lambda c: c.data.startswith("new_shift_key"))
async def callback_message(callback: CallbackQuery):
    user_id = get_user_id(callback.from_user.id)
    if not user_id:
        await callback.answer("Ты не зарегистрирован.")
        return

    data = callback.data

    _, date_str, shift_id, start_time, end_time = data.split(",")
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
    await callback.message.delete()
    await new_schedule(callback.message)



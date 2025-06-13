from aiogram import Router, types, F
from aiogram.types import CallbackQuery, Message
import sqlite3
import csv
import os
from .config import DB_PATH
from loguru import logger
from utils.db import save_mem_id


admin_router = Router()



async def send_schedule_file(start_str, end_str, callback: CallbackQuery, admin: bool = True):
    if admin:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT schedule.date, schedule.actual_start, schedule.actual_end, users.full_name, shifts.day_of_week
                FROM schedule
                JOIN users ON schedule.user_id = users.id
                JOIN shifts ON schedule.shift_id = shifts.id
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            """,
                (start_str, end_str),
            )
            shifts = cursor.fetchall()

        if not shifts:
            await callback.answer("Нет смен за выбранный период.", show_alert=True)
            return
        
    else:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ancient_schedule.date, ancient_schedule.day_night, users.full_name
                FROM ancient_schedule
                JOIN users ON ancient_schedule.user_id = users.id
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            """,
                (start_str, end_str),
            )
            shifts = cursor.fetchall()

        if not shifts:
            await callback.answer("Нет смен за выбранный период.", show_alert=True)
            return        
    

        
    BASE_DIR = os.path.dirname(__file__)
    file_path = os.path.join(BASE_DIR, 'exports', f"schedule_{start_str} - {end_str}.csv")

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";", lineterminator="\n")
            writer.writerow(["Дата", "Начало", " Конец", "Имя", "День"])
            writer.writerows(shifts)

    file = types.FSInputFile(file_path)

    await callback.message.answer_document(file)
    os.remove(file_path)


@admin_router.channel_post(F.photo)
async def mem_catcher_handler(message: Message):
    file_id = message.photo[-1].file_id
    save_mem_id(file_id)
    print('Сохранено фото')


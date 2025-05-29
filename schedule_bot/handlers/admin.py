from aiogram import Router, types, F
from aiogram.types import Message
import sqlite3
import csv
import os
from .config import DB_PATH
from loguru import logger
from utils.db import save_mem_id


admin_router = Router()


# @admin_router.message(lambda m: m.text == "Hash")
# async def hash(message: types.Message):
#     await message.answer(
#         "Введи начальную и конечную дату в формате ГГГГ-ММ-ДД через пробел и не забудь кодовое слово!"
#     )


@admin_router.message(lambda message: message.text.startswith("расписание "))
async def send_schedule_file(message: types.Message):
    user_id = message.from_user.id
    if user_id != 357434524:
        return
    try:
        # Ожидаем сообщение вида "расписание 2025-05-01 2025-05-10"
        _, start_str, end_str = message.text.split()

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT schedule.date, schedule.actual_start, schedule.actual_end, users.full_name, shifts.day_of_week
                FROM schedule
                JOIN users ON schedule.user_id = users.id
                JOIN shifts ON schedule.shift_id = shifts.id
                WHERE date BETWEEN ? AND ?
            """,
                (start_str, end_str),
            )
            shifts = cursor.fetchall()

        if not shifts:
            await message.answer("Нет смен за выбранный период.")
            return

        # Сохраняем как CSV
        BASE_DIR = os.path.dirname(__file__)
        file_path = os.path.join(BASE_DIR, 'exports', f"schedule_{start_str} - {end_str}.csv")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";", lineterminator="\n")
            writer.writerow(["Дата", "Начало", " Конец", "Имя", "День"])
            writer.writerows(shifts)

        file = types.FSInputFile(file_path)

        await message.answer_document(file)
        os.remove(file_path)


    except Exception as e:
        logger.exception(e)
        await message.answer(
            "Неверный формат. Введите: расписание ГГГГ-ММ-ДД ГГГГ-ММ-ДД"
        )


@admin_router.channel_post(F.photo)
async def mem_catcher_handler(message: Message):
    file_id = message.photo[-1].file_id
    save_mem_id(file_id)
    print('Сохранено фото')


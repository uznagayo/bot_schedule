from aiogram import Router, F, types
import sqlite3, csv, os
from .config import DB_PATH


admin_router = Router()


@admin_router.message(lambda m: m.text == "Hash")
async def hash(message: types.Message):
    await message.answer(
        "Введи начальную и конечную дату в формате ГГГГ-ММ-ДД через пробел и не забудь кодовое слово!"
    )


@admin_router.message(lambda message: message.text.startswith("расписание "))
async def send_schedule_file(message: types.Message):
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
        file_path = f"utils/schedule_{start_str} - {end_str}.csv"
        with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";", lineterminator="\n")
            writer.writerow(["Дата", "Начало", " Конец", "Имя", "День"])
            writer.writerows(shifts)


        await message.answer_document(types.InputFile(file_path))
        os.remove(file_path)


    except Exception as e:
        await message.answer(
            "Неверный формат. Введите: расписание ГГГГ-ММ-ДД ГГГГ-ММ-ДД"
        )
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, timedelta
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
import sqlite3
import os
import csv

DB_PATH = "schedule.db"

bot = Bot("7820867755:AAF7WBQ1BrWu-CYD58xa3UnRWLTE2zBlgkI")
dp = Dispatcher(bot)

# with sqlite3.connect(DB_PATH) as conn:
#    cursor = conn.cursor()
#    cursor.execute(
#       """
#       SELECT day_of_week || ' ' || start_time || ' ' || end_time
#       FROM schedule
#      """,
#      )
#  shifts_name = [i[0] for i in cursor.fetchall()]


def get_next_week_sheeets():
    shift_ids = list(range(1, 14))
    next_monday = datetime.today() + timedelta(days=7 - datetime.today().weekday())
    next_sunday = next_monday + timedelta(days=6)
    dates = [(next_monday + timedelta(days=k)).strftime("%Y-%m-%d") for k in range(7)]
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT shift_id
        FROM schedule
        WHERE date BETWEEN ? AND ?
        """,
            (next_monday.strftime("%Y-%m-%d"), next_sunday.strftime("%Y-%m-%d")),
        )
        num = [i[0] for i in cursor.fetchall()]

        # cursor = conn.cursor()
        cursor.execute(
            """
            SELECT day_of_week || ' ' || start_time || ' ' || end_time
            FROM shifts
            """,
        )
        shifts_name = [i[0] for i in cursor.fetchall()]
        dates.extend([dates[4], dates[5], dates[5], dates[6], dates[6], dates[5]])
        if num:
            for i in num:
                shifts_name.pop(shift_ids.index(i))
                dates.pop(shift_ids.index(i))
                shift_ids.remove(i)

        print(shifts_name, num, next_monday, next_sunday)
    return shift_ids, shifts_name, dates


def get_users_name(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT full_name || ' ' || telegram_id
        FROM users
        """,
        )
        users = [i[0] for i in cursor.fetchall() if user_id not in i]
        return users


def get_schedule(user_id, start_date: datetime):
    end_date = start_date + timedelta(days=13)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT date, actual_start, actual_end
        FROM schedule
        JOIN shifts ON schedule.shift_id = shifts.id
        WHERE user_id = ? AND date BETWEEN ? AND ?
        ORDER BY date
        """,
            (user_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
        )
        return cursor.fetchall()


def get_user_id(telegram_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return result[0] if result else None


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    buttons = [
        KeyboardButton(
            text="По сменам",
        ),
        KeyboardButton(
            text="Мое расписание",
        ),
    ]
    if user_id == 357434524:
        buttons.append(KeyboardButton(text="Hash"))
    marcup = ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True)

    await message.answer("Hello", reply_markup=marcup)


@dp.message_handler(lambda message: message.text == "По сменам")
async def send_shedule(message: types.Message):
    await new_schedule(message)
    await message.delete()


async def new_schedule(message: types.Message):
    shift_id, next_week_names, dates = get_next_week_sheeets()
    keybroad = InlineKeyboardMarkup(row_width=2)
    for i in range(len(shift_id)):
        time = ",".join(next_week_names[i].split(" ")[1:])
        button = InlineKeyboardButton(
            text=next_week_names[i], callback_data=(f"new_shift_key,{dates[i]},{shift_id[i]},{time}")
        )
        keybroad.inline_keyboard.append([button])
    if not shift_id:
        await message.answer("Свободных смен нету")
    else:
        await message.answer("Сободные смены:", reply_markup=keybroad)


@dp.callback_query_handler()
async def callback_message(callback: types.CallbackQuery):
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


@dp.message_handler(lambda message: message.text == "Мое расписание")
async def my_schedule(message: types.Message):
    await message.delete()
    await this_week(message)


async def this_week(message):
    user_id = get_user_id(message.from_user.id)
    if not user_id:
        await message.answer("Ты ещё не зарегистрирован в системе.")
        return

    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    schedule = get_schedule(user_id, start_of_week)

    if not schedule:
        await message.answer("На этой неделе у тебя пока нет смен.")
        return

    message1 = "Твое расписание на текущую неделю:\n"
    for date, start, end in schedule:
        weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
        message1 += f"{weekday} ({date}): {start}–{end}\n"

    await message.answer(message1)


@dp.message_handler(lambda message: message.text == "Отдать смену")
async def shift_change(message: types.Message):
    pass


@dp.message_handler(lambda m: m.text == "Hash")
async def hash(message: types.Message):
    await message.answer(
        "Введи начальную и конечную дату в формате ГГГГ-ММ-ДД через пробел и не забудь кодовое слово!"
    )


@dp.message_handler(lambda message: message.text.startswith("расписание "))
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
        file_path = f"schedule_{start_str} - {end_str}.csv"
        with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";", lineterminator="\n")
            writer.writerow(["Дата", "Начало", " Конец", "Имя", "День"])
            writer.writerows(shifts)

        await message.answer_document(types.InputFile(file_path))
        os.remove(file_path)

    except Exception:
        await message.answer(
            "Неверный формат. Введите: расписание ГГГГ-ММ-ДД ГГГГ-ММ-ДД"
        )


executor.start_polling(dp)

import sqlite3
from handlers.config import DB_PATH
from datetime import datetime, timedelta
import json
from random import choice


def get_user_role(telegram_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT role
        FROM users
        WHERE telegram_id = ?
        """,
            (telegram_id,),
        )
        result = cursor.fetchone()
        return result[0] if result else None


def send_meme():
    with open("schedule_bot/memes.json", "r", encoding="utf-8") as file:
        memes = json.load(file)
    meme = choice(memes)
    return meme


def get_user_name(telegram_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute(
            "SELECT full_name FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return result[0] if result else None


def get_user_id(telegram_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute(
            "SELECT id FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return result[0] if result else None


def get_schedule(user_id, start_date: datetime):
    end_date = start_date + timedelta(days=13)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT schedule.id, day_of_week, date, actual_start, actual_end
        FROM schedule
        JOIN shifts ON schedule.shift_id = shifts.id
        WHERE user_id = ? AND date BETWEEN ? AND ?
        ORDER BY date
        """,
            (user_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
        )
        return cursor.fetchall()


def get_all_schedule(week: bool):
    start_of_week = datetime.today() - timedelta(days=datetime.today().weekday())
    
    if week:
            end_of_week = start_of_week + timedelta(days=6)
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                """
                SELECT day_of_week, actual_start, actual_end, users.full_name
                FROM shifts
                JOIN schedule ON schedule.shift_id = shifts.id
                JOIN users ON users.id = schedule.user_id
                WHERE date BETWEEN ? AND ?
                """,
                    (start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")),
                )
                return cursor.fetchall()
    else:
        start_of_week += timedelta(days=7)
        end_of_week = start_of_week + timedelta(days=6)
        with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                """
                SELECT day_of_week, actual_start, actual_end, users.full_name
                FROM shifts
                JOIN schedule ON schedule.shift_id = shifts.id
                JOIN users ON users.id = schedule.user_id
                WHERE date BETWEEN ? AND ?
                """,
                    (start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")),
                )
                return cursor.fetchall()

def get_onday_admins(day: datetime):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT full_name, telegram_id
            FROM users
            JOIN schedule ON schedule.user_id = users.id
            WHERE date = ?
            """,
                (day.strftime("%Y-%m-%d"),),
        )
        return cursor.fetchall

def get_users_data():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT id, full_name, telegram_id
        FROM users
        """,
        )
        return cursor.fetchall()


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

        days = []
        times = []
        # print(shifts_name)
        for k in range(len(shifts_name)):
            day, time = shifts_name[k].split(" ")[0], ",".join(
                shifts_name[k].split(" ")[1:]
            )
            days.append(day)
            times.append(time)

    # print(
    #     shift_ids,
    #     days,
    #     times,
    #     dates,
    # )

    return shift_ids, days, times, dates


def delete_shift_not(shift_id: int):

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM schedule
            WHERE id = ?
            """,
            (shift_id,),
        )
        conn.commit()


def get_telegram_ids(role: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT telegram_id
            FROM users
            WHERE role = ?
            """,
            (role,),
        )
        result = cursor.fetchall()
        return [i[0] for i in result]


def get_shift_id_onday(day: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT id
        FROM shifts
        WHERE day_of_week = ?
        """,
            (day,),
        )
        shift_ids = [i[0] for i in cursor.fetchall()]
        print(shift_ids)
        return shift_ids


def create_shift_exchange_request(sender_id, recipient_id, shift_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO shift_exchange_requests (sender_id, recipient_id, shift_id)
        VALUES (?, ?, ?)
        """,
        (sender_id, recipient_id, shift_id),
    )
    conn.commit()
    conn.close()
    return


def get_requests_id(telegram_id: int, way: bool = True):
    user_id = get_user_id(telegram_id)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if way:

            cursor.execute(
                """
                SELECT r.id, u2.full_name, s.date, s.actual_start, s.actual_end
                FROM shift_exchange_requests r
                JOIN users u2 ON r.sender_id = u2.id
                JOIN schedule s ON r.shift_id = s.id
                WHERE r.recipient_id = ? AND r.status = 'pending'
                """,
                (user_id,),
            )
            return cursor.fetchall()
        else:
            cursor.execute(
                """
                SELECT r.id, u2.full_name, s.date, s.actual_start, s.actual_end
                FROM shift_exchange_requests r
                JOIN users u2 ON r.recipient_id = u2.id
                JOIN schedule s ON r.shift_id = s.id
                WHERE r.sender_id = ? AND r.status = 'pending'
                """,
                (user_id,),
            )
            return cursor.fetchall()




def shift_swap_handler(request_id, action):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if action == 'accepted':
            cursor.execute(
            """
                SELECT recipient_id, shift_id
                FROM shift_exchange_requests
                WHERE id = ?
                """,
            (request_id,),
            )
            result = cursor.fetchall()
            recipient_id, shift_id = result[0]

            cursor.execute(
            f"UPDATE schedule SET user_id = {recipient_id} WHERE id = {shift_id}"
            )
            cursor.execute(
            f"UPDATE shift_exchange_requests SET status = 'accepted' WHERE id = {request_id}"
            )
            return ("Смена принята")

        elif action == 'declined':
            cursor.execute(
            f"UPDATE shift_exchange_requests SET status = 'declined' WHERE id = {request_id}"
            )
            return ("Как хош")

        elif action == 'canceled':
            cursor.execute(
            f"UPDATE shift_exchange_requests SET status = 'canceled' WHERE id = {request_id}"
            )
            return ("Запрос отозван")


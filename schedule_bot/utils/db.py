import sqlite3
from handlers.config import DB_PATH
from datetime import datetime, timedelta



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
        SELECT date, actual_start, actual_end
        FROM schedule
        JOIN shifts ON schedule.shift_id = shifts.id
        WHERE user_id = ? AND date BETWEEN ? AND ?
        ORDER BY date
        """,
            (user_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
        )
        return cursor.fetchall()

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



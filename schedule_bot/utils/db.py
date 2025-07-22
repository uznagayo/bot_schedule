import sqlite3
from handlers.config import DB_PATH
from datetime import datetime, timedelta
import json
from random import choice
import calendar


MEMES = "memes.json"


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


def save_mem_id(file_id):
    data = []
    try:
        with open(MEMES, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    if file_id not in data:
        data.append(file_id)

        with open(MEMES, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ Добавлен: {file_id}")
    else:
        print(f"ℹ️ Уже есть: {file_id}")


def send_meme():
    with open(MEMES, "r", encoding="utf-8") as file:
        memes = json.load(file)
    meme = choice(memes)
    return meme


def get_user_name(id: int):
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute(
            "SELECT full_name FROM users WHERE id = ?", (id,)
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
                ORDER BY date
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
                ORDER BY date
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


def get_users_data(user_id=None, telegram_id=None, role=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT id, full_name, telegram_id
        FROM users
        WHERE (id = ? OR ? IS NULL)
        AND (telegram_id = ? OR ? IS NULL) 
        AND (role = ? OR ? IS NULL)
        """,
            (user_id, user_id, telegram_id, telegram_id, role, role),
        )
        return cursor.fetchall()


def get_next_week_sheeets(week: bool = True):
    shift_ids = list(range(1, 14))
    next_monday = (
        datetime.today() + timedelta(days=7 - datetime.today().weekday())
        if week
        else datetime.today() - timedelta(datetime.today().weekday())
    )
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
                if i == 14:
                    continue
                else:
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
        if action == "accepted":
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
            return "Смена принята"

        elif action == "declined":
            cursor.execute(
                f"UPDATE shift_exchange_requests SET status = 'declined' WHERE id = {request_id}"
            )
            return "Как хош"

        elif action == "canceled":
            cursor.execute(
                f"UPDATE shift_exchange_requests SET status = 'canceled' WHERE id = {request_id}"
            )
            return "Запрос отозван"


def insert_uncommon_sheet(user_id, start, end):

    coef = get_salary_coef(user_id)

    cost = (end - start) * coef
    date = datetime.today()
    date_str = date.strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
        INSERT OR REPLACE INTO schedule (user_id, date, shift_id, actual_start, actual_end, cost)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                date_str,
                14,
                (str(start) + ":00"),
                (str(end) + ":00"),
                cost,
            ),
        )


# def doSQLQuery # takes int db_string and payload
# 1. Make connectiong
# 2. dp query
# 3. commit


# def InsertUser # takes in user
# doSQLQuery('SQL', user)


def get_ancient_sheets(time: bool = True, date: str = ""):

    if time:
        t = "День"
    else:
        t = "Ночь"

    today = datetime.today()
    year, month = today.year, today.month
    if not date:
        first_day = datetime(year, month, 1).strftime("%Y-%m-%d")
        last_day = datetime(year, month, calendar.monthrange(year, month)[1]).strftime(
            "%Y-%m-%d"
        )
    else:
        first_day = date
        last_day = date

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT *
            FROM ancient_schedule
            WHERE
                date BETWEEN ? AND ?
                AND day_night = ?
            ORDER BY date
            """,
            (first_day, last_day, t),
        )
        result = cursor.fetchall()
    if not result:
        return [], [], [0], [], today.strftime("%Y"), today.strftime("%m")

    id = [i[0] for i in result]
    day_night = [i[1] for i in result]
    user = [i[2] for i in result]
    date = [i[3] for i in result]

    return id, day_night, user, date, today.strftime("%Y"), today.strftime("%m")


def insert_ancient_sheet(
    user_id=0, day_night=True, date="", ins=True, exs=False, id=None
):
    time = "День" if day_night else "Ночь"
    if ins and not exs:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO ancient_schedule (user_id, day_night, date)
                VALUES (?, ?, ?)
                """,
                (user_id, time, date),
            )
            conn.commit()
    elif exs:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE ancient_schedule (user_id)
                SET user_id = ?
                WHERE id = ?
                """,
                (user_id, id),
            )
            conn.commit()
    elif not ins and not exs:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM ancient_schedule
                WHERE date = ? 
                AND user_id = ?
                AND day_night = ?
                """,
                (date, user_id, time),
            )
            conn.commit()


def add_user(full_name: str, telegram_id: int, role: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
                INSERT OR REPLACE INTO users (telegram_id, full_name, role)
                VALUES (?, ?, ?)
                """,
            (telegram_id, full_name, role),
        )
        conn.commit()


def unicue_db_update(data: dict):
    table = data["table"]
    column = data["column"]
    value = data["value"]
    id = data["id"]
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                    UPDATE {table} SET {column} = ? WHERE id = ?
                    """,
                (value, id),
            )
        return "Done"
    except Exception as e:
        return e


def unicue_db_select(data: dict):
    table = data["table"]
    column = data["column"]
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                    SELECT {column}
                    FROM {table}
                """
            )
            rows = cursor.fetchall()
            result = "\n".join([" ".join(str(item) for item in row) for row in rows])
        return result
    except Exception as e:
        return e


def unicue_db_delete(data: dict):
    table = data["table"]
    id = data["id"]
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                    DELETE
                    FROM {table}
                    WHERE id = {id}
                """
            )
        return "Done"
    except Exception as e:
        return e


def get_salary_coef(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT rc.salary_coef
        FROM users u
        JOIN role_coefficients rc ON u.role = rc.role
        WHERE u.id = ?
    """,
        (user_id,),
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        raise ValueError(f"Не удалось найти коэффициент для user_id = {user_id}")


def get_salary(user_id):
    end_date = datetime.today()
    mount_start = end_date.replace(day=1)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        SELECT cost
        FROM schedule
        WHERE user_id = ? AND date BETWEEN ? AND ?
        ORDER BY date
        """,
            (user_id, mount_start.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
        )
        costs = cursor.fetchall()

        salary = ((sum([int(i[0]) for i in costs if i[0] is not None]) + 49) // 50) * 50
    return salary


def make_salary_db_request(user_id: int, sum: int):
    date = datetime.today().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
                INSERT OR REPLACE INTO given_salaries (user_id, date, sum)
                VALUES (?, ?, ?)
                """,
            (user_id, date, sum),
        )
        conn.commit()


def delete_salaries(user_id: int):
    end_date = datetime.today()
    mount_start = end_date.replace(day=1)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        UPDATE schedule SET cost = 0 
        WHERE user_id = ? and date BETWEEN ? AND ?
        
        """,
            (user_id, mount_start.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
        )

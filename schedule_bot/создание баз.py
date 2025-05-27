import sqlite3
from handlers.config import DB_PATH
from datetime import datetime, timedelta
from utils.db import get_users_data

# print(get_users_data())


# conn = sqlite3.connect(DB_PATH)
# cursor = conn.cursor()
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute(
                """
                SELECT r.id, u2.full_name, s.date, s.actual_start, s.actual_end
                FROM shift_exchange_requests r
                JOIN users u2 ON r.sender_id = u2.id
                JOIN schedule s ON r.shift_id = s.id
                WHERE r.recipient_id = ? AND r.status = 'pending'
                """,
                (int(8),),
            )
    result = cursor.fetchall()
print(result)
# conn = sqlite3.connect(DB_PATH)
# cursor = conn.cursor()
# cursor.execute(
#         """
#             SELECT recipient_id, shift_id
#             FROM shift_exchange_requests
#             WHERE id = ?
#             """,
#         (2,),
#     )
# result = cursor.fetchall()
# recipient_id, shift_id = result[0]
# print(recipient_id, shift_id)

# cursor.execute(f'DELETE FROM shift_exchange_requests WHERE shift_id = {111}')

# cursor.execute(
#     """
# CREATE TABLE IF NOT EXISTS shift_exchange_requests (
#    id INTEGER PRIMARY KEY AUTOINCREMENT,
#    sender_id INTEGER NOT NULL,
#    recipient_id INTEGER,
#    shift_id INTEGER NOT NULL,
#    status VARCHAR(20) CHECK(status IN('pending', 'accepted', 'declined', 'canceled')) DEFAULT 'pending',
#    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#    FOREIGN KEY(sender_id) REFERENCES users(id),
#    FOREIGN KEY(recipient_id) REFERENCES users(id),
#    FOREIGN KEY(shift_id) REFERENCES schedule(id)
# )
# """
# )

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS shifts (
# id INTEGER PRIMARY KEY AUTOINCREMENT,
# day_of_week TEXT NOT NULL,
# start_time TEXT NOT NULL,
# end_time TEXT NOT NULL
# )
# """)

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS schedule (
# id INTEGER PRIMARY KEY AUTOINCREMENT,
# user_id INTEGER NOT NULL,
# date TEXT NOT NULL,
# shift_id INTEGER NOT NULL,
#  actual_start TEXT,
#  actual_end TEXT,
# FOREIGN KEY(user_id) REFERENCES users(id),
# FOREIGN KEY(shift_id) REFERENCES shifts(id)
# )
# """)
# print("done")
# conn.commit()
# conn.close()

# with sqlite3.connect(DB_PATH) as conn:
#         cursor = conn.cursor()
#         cursor.execute(
#             """
#         SELECT id, full_name, telegram_id
#         FROM users
#         """,
#         )
#         result = cursor.fetchall()
#         users_id, users_name, users_telegram_id = result[0]
# print(users_id, users_name, users_telegram_id)
# def get_next_week_sheeets():
#    shift_ids = list(range(1, 14))
#    next_monday = datetime.today() + timedelta(days=7 - datetime.today().weekday())
#    next_sunday = next_monday + timedelta(days=6)
#    dates = [(next_monday + timedelta(days=k)).strftime("%Y-%m-%d") for k in range(7)]
#    with sqlite3.connect(DB_PATH) as conn:
#       cursor = conn.cursor()
#       cursor.execute(
#             """
#         SELECT shift_id
#         FROM schedule
#         WHERE date BETWEEN ? AND ?
#         """, (next_monday, next_sunday)
#         )
#       num = cursor.fetchall()[0]

#        # cursor = conn.cursor()
#       cursor.execute(
#             """
#             SELECT day_of_week || ' ' || start_time || ' ' || end_time
#             FROM shifts
#             """,
#             )
#       shifts_name = [i[0] for i in cursor.fetchall()]
#       dates.extend([dates[4], dates[5], dates[5], dates[6], dates[6], dates[5]])
#       if num:
#          for i in num:

#             shift_ids.pop(i)
#             shifts_name.pop(i)
#             dates.pop(i)
#    return shift_ids, shifts_name, dates


# a, b, c = get_next_week_sheeets()
# print(a[1], ' '.join(b[1].split(" ")[1:]), c[1])


# def get_users_name(user_id: int):
#     with sqlite3.connect(DB_PATH) as conn:
#         cursor = conn.cursor()
#         cursor.execute(
#             """
#         SELECT full_name || ' ' || telegram_id
#         FROM users
#         """,
#         )
#         users = [i[0] for i in cursor.fetchall() if user_id not in i]
#         return users
# print(get_users_name(45612354995))

# with sqlite3.connect(DB_PATH) as conn:
#         conn.execute(
#             """
#         INSERT OR REPLACE INTO users (telegram_id, full_name)
#         VALUES (?, ?)
#         """,
#             (int(input()), input()),
#         )

# _, start_str, end_str = 'расписание', '2025-05-01', '2025-05-30'

# with sqlite3.connect(DB_PATH) as conn:
#             cursor = conn.cursor()
#             cursor.execute("""
#                 SELECT schedule.date, schedule.actual_start, schedule.actual_end, users.full_name, shifts.day_of_week
#                 FROM schedule
#                 JOIN users ON schedule.user_id = users.id
#                 JOIN shifts ON schedule.shift_id = shifts.id
#                 WHERE date BETWEEN ? AND ?
#             """, (start_str, end_str))
#             shifts = cursor.fetchall()
# print(shifts)

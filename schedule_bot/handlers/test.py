import sqlite3
from config import DB_PATH
from loguru import logger
# import csv, os
# import utils.db


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
# cursor.execute('SELECT * FROM users')
# print(cursor.fetchall())

# cursor.execute(
#     "UPDATE users SET role = 'ancient' WHERE full_name = 'Левацкий Артём Юрьевич'"
# )

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(
        """
            SELECT recipient_id, shift_id
            FROM shift_exchange_requests
            WHERE id = ?
            """,
        (2,),
    )
print(cursor.fetchall())

# for i in range(int(input())):
#     cursor.execute(
#         """
#         INSERT OR REPLACE INTO users (telegram_id, full_name)
#         VALUES (?, ?)
#         """,
#         (int(input()), input()),
#     )

# data = "расписание 2025-04-01 2025-05-20"
# _, start_str, end_str = data.split()

# with sqlite3.connect(DB_PATH) as conn:
#     cursor = conn.cursor()
#     cursor.execute(
#         """
#                 SELECT schedule.date, schedule.actual_start, schedule.actual_end, users.full_name, shifts.day_of_week
#                 FROM schedule
#                 JOIN users ON schedule.user_id = users.id
#                 JOIN shifts ON schedule.shift_id = shifts.id
#                 WHERE date BETWEEN ? AND ?
#             """,
#         (start_str, end_str),
#     )
#     shifts = cursor.fetchall()

# if not shifts:
#     print("none")



#     # Сохраняем как CSV
# BASE_DIR = os.path.dirname(__file__)
# file_path = os.path.join(BASE_DIR, 'exports', f"schedule_{start_str} - {end_str}.csv")

# os.makedirs(os.path.dirname(file_path), exist_ok=True)
# print(file_path)
# with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
#     writer = csv.writer(f, delimiter=";", lineterminator="\n")
#     writer.writerow(["Дата", "Начало", " Конец", "Имя", "День"])
#     writer.writerows(shifts)


# conn = sqlite3.connect(DB_PATH)
# cursor = conn.cursor()

# cursor.execute(f'DELETE FROM schedule WHERE user_id = {1}')

logger.success("done")
conn.commit()
conn.close()

# print(utils.db.get_users_name(1))
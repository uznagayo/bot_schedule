import sqlite3
from config import DB_PATH


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_sequence')
print(cursor.fetchall())
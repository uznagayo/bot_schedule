from datetime import datetime, timedelta
import aiogram 
from aiogram import types, Router, F

reminders_router = Router()

today = datetime.now()
today_str = today.strftime("%Y-%m-%d")
tomorrow = today + timedelta(days=1)
tomorrow_str = tomorrow.strftime("%Y-%m-%d")



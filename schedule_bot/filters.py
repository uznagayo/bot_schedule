from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import sqlite3
from handlers.config import DB_PATH, channel_id
from loguru import logger


def is_user_registered(user_id: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (user_id,))
        return cursor.fetchone() is not None

class IsRegisteredMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        if not is_user_registered(user_id):
            if isinstance(event, Message):
                logger.info(event.from_user.id, event.from_user.first_name, "не зарегистрирован")
                await event.answer("Ты не зарегистрирован в системе.")
                await event.bot.send_message(chat_id=channel_id, text=f"{event.from_user.id}, {event.from_user.first_name}, не зарегистрирован")
            elif isinstance(event, CallbackQuery):
                logger.info(event.from_user.id, event.from_user.first_name, "не зарегистрирован")
                await event.answer("Ты не зарегистрирован в системе.", show_alert=True)
                await event.bot.send_message(chat_id=channel_id, text=f"{event.from_user.id}, {event.from_user.first_name}, не зарегистрирован")
            return
        return await handler(event, data)
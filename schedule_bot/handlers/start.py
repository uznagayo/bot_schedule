from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from utils.db import send_meme
from .commands import start_true

start_router = Router()


@start_router.message(Command("start"))
async def start_command(message: types.Message):
    # user_id = message.from_user.id
    # keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    # buttons = [
    #     InlineKeyboardButton(text="По сменам", callback_data="new_schedule_key"),
    #     InlineKeyboardButton(text="Мое расписание", callback_data="my_schedule_key"),
    # ]
    # if user_id == 357434524:
    #     buttons.append(
    #         [
    #             InlineKeyboardButton(text="Hash", callback_data="hash_key"),
    #         ]
    #     )
    # keybroad.inline_keyboard.append(buttons)
    await message.answer("Дарова епт", reply_markup=start_true(message))


@start_router.message(Command("send_meme"))
async def send_meme_handler(message: types.Message):
    meme = send_meme()
    print(message.from_user.first_name, "заказал мем") # type: ignore
    await message.answer_photo(photo=meme, caption="Вот тебе мем, епт")

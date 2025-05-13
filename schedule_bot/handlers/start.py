from aiogram import Router, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from utils.db import send_meme


start_router = Router()

@start_router.message(Command('start'))
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

    await message.answer("Дарова епт", reply_markup=marcup)


@start_router.message(Command('send_meme'))
async def send_meme_handler(message: types.Message):
    meme = send_meme()
    print(message.from_user.first_name, 'заказал мем')
    await message.answer_photo(photo=meme, caption="Вот тебе мем, епт")


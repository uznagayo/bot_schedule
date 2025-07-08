from aiogram import Router, types, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import sqlite3
import csv
import os
from .config import DB_PATH, channel_id
from loguru import logger
from utils.db import save_mem_id, add_user, unicue_db_update, unicue_db_select, unicue_db_delete
from .states import AddUserSt
from .commands import start_true


admin_router = Router()



async def send_schedule_file(start_str, end_str, callback: CallbackQuery, admin: bool = True):
    if admin:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT schedule.date, schedule.actual_start, schedule.actual_end, users.full_name, shifts.day_of_week
                FROM schedule
                JOIN users ON schedule.user_id = users.id
                JOIN shifts ON schedule.shift_id = shifts.id
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            """,
                (start_str, end_str),
            )
            shifts = cursor.fetchall()

        if not shifts:
            await callback.answer("Нет смен за выбранный период.", show_alert=True)
            return
        
    else:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ancient_schedule.date, ancient_schedule.day_night, users.full_name
                FROM ancient_schedule
                JOIN users ON ancient_schedule.user_id = users.id
                WHERE date BETWEEN ? AND ?
                ORDER BY date
            """,
                (start_str, end_str),
            )
            shifts = cursor.fetchall()

        if not shifts:
            await callback.answer("Нет смен за выбранный период.", show_alert=True)
            return        
    

        
    BASE_DIR = os.path.dirname(__file__)
    file_path = os.path.join(BASE_DIR, 'exports', f"schedule_{start_str} - {end_str}.csv")

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";", lineterminator="\n")
            writer.writerow(["Дата", "Начало", " Конец", "Имя", "День"])
            writer.writerows(shifts)

    file = types.FSInputFile(file_path)

    await callback.message.answer_document(file)
    os.remove(file_path)

async def db_func(text: str):
    querry = text.split("|")
    action = querry[0]
    data = {}
    if action == "update":
        data['table'] = querry[1]
        data['column'] = querry[2]
        data['value'] = querry[3]
        data['id'] = int(querry[4])
        return unicue_db_update(data=data)
    elif action == "select":
        data['table'] = querry[1]
        data['column'] = querry[2]
        return unicue_db_select(data=data)
    elif action == "delete":
        data['table'] = querry[1]
        data['id'] = int(querry[4])
        return unicue_db_delete(data=data)


@admin_router.channel_post(F.photo)
async def mem_catcher_handler(message: Message):
    file_id = message.photo[-1].file_id
    save_mem_id(file_id)
    print('Сохранено фото')


@admin_router.callback_query(F.data == "add_user")
async def add_user_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введи имя пользователя", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ОТМЕНА", callback_data="go_back_state")],
        ]
    ))
    await state.set_state(AddUserSt.name)

@admin_router.message(AddUserSt.name)
async def add_user_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введи telegram_id", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ОТМЕНА", callback_data="go_back_state")],
        ]
    ))
    await state.set_state(AddUserSt.telegram_id)

@admin_router.message(AddUserSt.telegram_id)
async def add_user_telegram_id(message: Message, state: FSMContext):
    await state.update_data(telegram_id=int(message.text))

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Младший", callback_data="role:employee")],
            [InlineKeyboardButton(text="Старший", callback_data="role:ancient")],
            [InlineKeyboardButton(text="Игровед", callback_data="role:gm")],
            [InlineKeyboardButton(text="ОТМЕНА", callback_data="go_back_state")],
        ]
    )

    await message.answer("Выбери роль", reply_markup=keyboard)
    await state.set_state(AddUserSt.role)

@admin_router.callback_query(AddUserSt.role)
async def add_user_role(callback: CallbackQuery, state: FSMContext):
    role = callback.data.split(":")[1]
    await state.update_data(role=role)

    data = await state.get_data()

    name = data["name"]
    telegram_id = data["telegram_id"]

    await callback.message.answer(text=f"Ты хочешь добавить пользователя\n{name} id: {telegram_id} роль: {role}", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подтверждаю", callback_data="conf")],
            [InlineKeyboardButton(text="ОТМЕНА", callback_data="go_back_state")],
        ]
    ))
    await state.set_state(AddUserSt.conf)

@admin_router.callback_query(AddUserSt.conf)
async def add_user_conf(callback: CallbackQuery, state: FSMContext):
    conf = callback.data
    await state.update_data(conf=conf)

    data = await state.get_data()

    name = data["name"]
    telegram_id = data["telegram_id"]
    role = data["role"]    

    try:
        add_user(full_name=name, telegram_id=telegram_id, role=role)
        await state.clear()
        await callback.answer(text="Пользователь добавлен", show_alert=True)
        await callback.message.answer(text="Главное меню", reply_markup=start_true(callback))
    
    except Exception as e:
        await state.clear()
        await callback.answer(text=f"Что-то не то\n{e}", show_alert=True)
        await callback.message.answer(text="Главное меню", reply_markup=start_true())


@admin_router.callback_query(F.data == "go_back_state", StateFilter("*"))
async def state_clear(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer(text="Операция отменена", show_alert=True)
    await callback.message.delete()
    await callback.message.answer(text="Главное меню", reply_markup=start_true(callback))
    

@admin_router.callback_query(lambda c: c.data == "register_start")
async def register_basic_user(callback: CallbackQuery):
    full_name = callback.from_user.first_name
    telegram_id = callback.from_user.id
    role = "user"
    
    try:
        add_user(full_name, telegram_id, role)
        await callback.message.answer(
            text="Вы успешно зарегистрированы как базовый " \
            "пользователь и можете смотреть мемы. Для этого " \
            "воспользуйтесь коммандой /send_meme"
            )
    except Exception as e:
        await callback.answer(text="Чет не то", show_alert=True)
        await callback.bot.send_message(
            chat_id=channel_id,
                    text=f"{telegram_id}, {full_name}, не смог зарегаться. {e}"
        )
    



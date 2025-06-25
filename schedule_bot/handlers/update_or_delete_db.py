from aiogram import Router, types, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from .states import DbUpdate
from .admin import db_func
from .callback_classes import HashActions
from .start import start_true


update_or_delete_db_router = Router()

@update_or_delete_db_router.callback_query(HashActions.filter(F.action == "delete"))
async def update_db_start(callback: CallbackQuery, callback_data: HashActions, state: FSMContext):
        await state.update_data(table=callback_data.data)
        await state.update_data(action="delete")
        await callback.message.answer("Введи айди записи", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="ОТМЕНА", callback_data="go_back_state")],
            ]
        ))
        await state.set_state(DbUpdate.value)


@update_or_delete_db_router.callback_query(HashActions.filter(F.action == "update"))
async def update_db_start(callback: CallbackQuery, callback_data: HashActions, state: FSMContext):
        await state.update_data(table=callback_data.data)
        await state.update_data(action="update")
        await callback.message.answer("Введи айди записи", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="ОТМЕНА", callback_data="go_back_state")],
            ]
        ))
        await state.set_state(DbUpdate.id)

@update_or_delete_db_router.message(DbUpdate.id)
async def update_db_start(message: Message, state: FSMContext):
        await state.update_data(id=int(message.text))
        await message.answer("Введи колонку", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="ОТМЕНА", callback_data="go_back_state")],
            ]
        ))
        await state.set_state(DbUpdate.column)
    
@update_or_delete_db_router.message(DbUpdate.column)
async def update_db_value(message: Message, state: FSMContext):
        await state.update_data(column=message.text.strip().lower())
        await message.answer("Введи новое значение", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="ОТМЕНА", callback_data="go_back_state")],
            ]
        ))
        await state.set_state(DbUpdate.value)

@update_or_delete_db_router.message(DbUpdate.value)
async def update_db_id(message: Message, state: FSMContext):
        await state.update_data(value=message.text.strip().lower())
        data = await state.get_data()

        action = data["action"]
        table = data["table"]

        if action == "update":
            column = data["column"]
            value = data["value"]
            id = data["id"]
            text = f"Ты хочешь изменить запись в таблице {table} № {id}\n{column} -> {value}"
        else:
            await state.update_data(id=int(message.text))
            data = await state.get_data()
            id = data["id"]
            text = f"Ты хочешь удалить запись № {id} из таблицы {table}"

        await message.answer(text=text, reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подтверждаю", callback_data="conf")],
                [InlineKeyboardButton(text="ОТМЕНА", callback_data="go_back_state")],
            ]
        ))
        await state.set_state(DbUpdate.conf)

@update_or_delete_db_router.callback_query(DbUpdate.conf)
async def update_dp_conf(callback: CallbackQuery, state: FSMContext):
        conf = callback.data
        await state.update_data(conf=conf)

        data = await state.get_data()

        action = data["action"]
        table = data["table"]

        if action == "update":
            column = data["column"]
            value = data["value"]
            id = data["id"]
        else:
            column = 0
            value = 0
            id = data["id"]

        text = f"{action}|{table}|{column}|{value}|{id}"

        answer = await db_func(text=text)
        await state.clear()

        if answer == "Done":
            await callback.answer(text="Готово", show_alert=True)
            await callback.message.answer(text="Главное меню", reply_markup=start_true(callback))
        
        else:
            await callback.answer(text=f"Что-то не так:\n{answer}", show_alert=True)
            await callback.message.answer(text="Главное меню", reply_markup=start_true(callback))



        



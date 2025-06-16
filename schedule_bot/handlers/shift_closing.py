from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from .states import ShiftClosingStages
from .commands import start_true
from .config import channel_id

shift_closing_router = Router()


keybroad = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Готово", callback_data='0')],
                [InlineKeyboardButton(text="ОТМЕНА", callback_data="go_back_state")]
                ]
                )

@shift_closing_router.callback_query(F.data == "start_shift_closing")
async def start_shift_closing(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Проверим всё ли в порядке перед закрытием смены.")
    await callback.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                text="Начать", callback_data='0')],
                [InlineKeyboardButton(
                    text="ОТМЕНА", callback_data="go_back_state")]
                    ],
        )
        )
    await state.set_state(ShiftClosingStages.supplies_in_place)

@shift_closing_router.callback_query(ShiftClosingStages.supplies_in_place)
async def supplies_in_place(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.message.edit_text(
        "Расходники в зале есть")
    await callback.message.edit_reply_markup(
        reply_markup=keybroad,
        )
        
    await state.set_state(ShiftClosingStages.tea_shelf_stocked)
    

@shift_closing_router.callback_query(ShiftClosingStages.tea_shelf_stocked)
async def supplies_in_place(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.message.edit_text(
        "Чайная полка заполнена")
    await callback.message.edit_reply_markup(
        reply_markup=keybroad,
        )
        
    await state.set_state(ShiftClosingStages.napkins_ready)



@shift_closing_router.callback_query(ShiftClosingStages.napkins_ready)
async def supplies_in_place(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.message.edit_text(
        "Салфетки и сахар на месте")
    await callback.message.edit_reply_markup(
        reply_markup=keybroad
        )

    await state.set_state(ShiftClosingStages.no_dishes_in_halls)



@shift_closing_router.callback_query(ShiftClosingStages.no_dishes_in_halls)
async def supplies_in_place(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.message.edit_text(
        "Посуды в залах нет")
    await callback.message.edit_reply_markup(
        reply_markup=keybroad,
        )
        
    await state.set_state(ShiftClosingStages.no_dishes_in_sink)



@shift_closing_router.callback_query(ShiftClosingStages.no_dishes_in_sink)
async def supplies_in_place(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.message.edit_text(
        "Посуды в мойке тоже нет")
    await callback.message.edit_reply_markup(
        reply_markup=keybroad,
        )
        
    await state.set_state(ShiftClosingStages.trash_cleaned)


@shift_closing_router.callback_query(ShiftClosingStages.trash_cleaned)
async def supplies_in_place(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.message.edit_text(
        "В залах убран мусор, в том числе в толчках")
    await callback.message.edit_reply_markup(
        reply_markup=keybroad,
        )
        
    await state.set_state(ShiftClosingStages.kitchen_bin_empty)


@shift_closing_router.callback_query(ShiftClosingStages.kitchen_bin_empty)
async def supplies_in_place(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.message.edit_text(
        "Мусорка на кухне вынесена")
    await callback.message.edit_reply_markup(
        reply_markup=keybroad,
        )
        
    await state.set_state(ShiftClosingStages.cash_closed)


@shift_closing_router.callback_query(ShiftClosingStages.cash_closed)
async def supplies_in_place(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.message.edit_text(
        "Касса посчитана и закрыта, фотки фелю отправлены")
    await callback.message.edit_reply_markup(
        reply_markup=keybroad,
        )
        
    await state.set_state(ShiftClosingStages.end)

@shift_closing_router.callback_query(ShiftClosingStages.end)
async def supplies_in_place(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.answer("Смена сдана", show_alert=True)
    await callback.message.delete()    
    await callback.bot.send_message(
        chat_id=channel_id,
        text="Смена закрыта")
    await state.clear()
    await callback.message.answer(text="Главное меню", reply_markup=start_true(callback))


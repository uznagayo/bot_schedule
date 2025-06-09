from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import sqlite3
from .config import DB_PATH
from utils.db import (
    get_user_id,
    delete_shift_not,
    get_telegram_ids,
    get_shift_id_onday,
    get_users_data,
    create_shift_exchange_request,
    shift_swap_handler,
    get_all_schedule,
    insert_uncommon_sheet,
    get_ancient_sheets,
    insert_ancient_sheet,
)
from .shifts import (
    new_schedule,
    this_week,
    new_schedule_days,
    get_income_requests,
    get_outcome_requests,
    generate_calendar,
)
from .commands import start_true
from loguru import logger
from .callback_classes import (
    SwapRequestHandler,
    WeekScheduleHandler,
    AssignNewJun,
    CalendarCb,
)

callbacks_router = Router()


# assign_new_jun = CallbackData("assign", "action", "user_id", "start", "end")


@callbacks_router.callback_query(lambda c: c.data.startswith("new_shift_day_key"))
async def new_shift_day_key(callback: CallbackQuery):
    data = callback.data
    day = data.split(",")[-1]
    # print(day)
    shift_ids = get_shift_id_onday(day)
    keybroad = new_schedule(shift_ids)
    await callback.message.edit_reply_markup(reply_markup=keybroad)


@callbacks_router.callback_query(lambda c: c.data.startswith("new_shift_key"))
async def new_shift_key(callback: CallbackQuery):
    user_id = get_user_id(callback.from_user.id)
    if not user_id:
        await callback.answer("Ты не зарегистрирован.")
        return

    data = callback.data

    _, date_str, shift_id, start_time, end_time = data.split(",")
    logger.info(
        f"{callback.from_user.first_name} choose {date_str} {shift_id} {start_time} {end_time}"
    )
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
        INSERT OR REPLACE INTO schedule (user_id, date, shift_id, actual_start, actual_end)
        VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, date_str, int(shift_id), start_time, end_time),
        )

    await callback.answer(
        f"Выбрано: {date_str} — смена {start_time}-{end_time}", show_alert=True
    )

    await new_schedule_days(callback)


@callbacks_router.callback_query(lambda c: c.data == "my_schedule_key")
async def my_schedule(callback: CallbackQuery):
    logger.info(f"{callback.from_user.first_name} act_send_my_shedule")
    await this_week(callback)


@callbacks_router.callback_query(lambda c: c.data.startswith("new_schedule_day_key"))
async def send_shedule(callback: CallbackQuery):
    logger.info(f"{callback.from_user.first_name} act_send_new_shedule")
    # user_role = get_user_role(callback.from_user.id)
    # if user_role == "ancient":
    #     await callback.answer("Эта кнопка не тебе")
    #     return

    if not new_schedule_days(callback):
        await callback.answer("Свободных смен нету", show_alert=True)
        return
    else:
        await new_schedule_days(callback)


@callbacks_router.callback_query(lambda c: c.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню")
    await callback.message.edit_reply_markup(reply_markup=start_true(callback))


@callbacks_router.callback_query(lambda c: c.data == "hash_key")
async def hash(callback: CallbackQuery):
    await callback.message.answer(
        "Введи начальную и конечную дату в формате ГГГГ-ММ-ДД через пробел и не забудь кодовое слово!"
    )


@callbacks_router.callback_query(lambda c: c.data.startswith("shift_key"))
async def shift_key(callback: CallbackQuery):
    data = callback.data
    _, id = data.split(",")
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    buttuns = [
        InlineKeyboardButton(
            text="Удалить смену",
            callback_data=f"delete_shift,{id}",
        ),
        InlineKeyboardButton(
            text="Отдать смену",
            callback_data=f"give_shift,{id}",
        ),
        InlineKeyboardButton(
            text="Назад",
            callback_data="my_schedule_key",
        ),
    ]
    for i in range(0, len(buttuns), 2):
        keybroad.inline_keyboard.append(buttuns[i : i + 2])
    await callback.message.edit_text("Что сделать хочешь?")
    await callback.message.edit_reply_markup(reply_markup=keybroad)


@callbacks_router.callback_query(lambda c: c.data.startswith("delete_shift"))
async def delete_shift(callback: CallbackQuery):
    data = callback.data
    _, id = data.split(",")
    try:
        delete_shift_not(id)
        await callback.answer("Смена удалена!", show_alert=True)
        await this_week(callback)
        await callback.bot.send_message(
            chat_id=357434524, text=f"{callback.from_user.first_name} удалил смену {id}"
        )
    except Exception as e:
        logger.exception(e)
        await callback.answer("Ошибка удаления смены. Попробуй позже.")


@callbacks_router.callback_query(lambda c: c.data == "emploee_summon_key")
async def emploee_summon_callback(callback: CallbackQuery):
    await callback.answer("Вызов младшего пока не работает", show_alert=True)
    return

    for id in get_telegram_ids("employee"):
        try:
            await callback.bot.send_message(
                chat_id=id,
                text=f"{callback.from_user.first_name} вызвал младшего на сегодня, с любого времени",
            )
            logger.info(f"Message sent to {id}")
        except Exception as e:
            logger.exception(f"Failed to send message to {id}: {e}")
            await callback.answer("Ошибка вызова младшего. Попробуй позже.")

    logger.info(
        text=f"{callback.from_user.first_name} вызвал младшего",
    )


@callbacks_router.callback_query(lambda c: c.data.startswith("give_shift"))
async def choosing_recipient(callback: CallbackQuery):

    data = callback.data
    _, shift_id = data.split(",")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """ 
                   SELECT recipient_id, shift_id
                   FROM shift_exchange_requests
                   WHERE shift_id = ? AND status = 'pending'
                   """,
            (shift_id,),
        )
    if cursor.fetchall():
        await callback.answer("Эта смена в процессе обмена", show_alert=True)
        await this_week(callback)
        return

    user_id = get_user_id(callback.from_user.id)
    # telegram_id_str = str(callback.from_user.id)
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    buttons = []
    users_data = get_users_data()
    for users_id, users_name, users_telegram_id in users_data:
        if users_telegram_id == user_id:
            continue

        buttons.append(
            InlineKeyboardButton(
                text=users_name,
                callback_data=(f"to_user,{users_id},{users_telegram_id},{shift_id}"),
            ),
        )
    buttons.append(
        InlineKeyboardButton(
            text="Назад",
            callback_data=("my_schedule_key"),
        ),
    )
    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i : i + 2])

    await callback.message.edit_text("Кому отдать?")
    await callback.message.edit_reply_markup(reply_markup=keybroad)


@callbacks_router.callback_query(lambda c: c.data.startswith("to_user"))
async def give_shift(callback: CallbackQuery):
    data = callback.data
    user_id = get_user_id(callback.from_user.id)
    __, recipient_id, recipient_telegram_id, shift_id = data.split(",")
    create_shift_exchange_request(user_id, recipient_id, shift_id)
    await callback.answer(
        "Создан запрос на обмен сменой, жди подтверждения", show_alert=True
    )
    await callback.bot.send_message(
        recipient_telegram_id, text="Тебе отправили новый запрос на обмен сменой"
    )
    await this_week(callback)


@callbacks_router.callback_query(lambda c: c.data == ("shift_exchenge_requests_key"))
async def get_shift_exchange_request(callback: CallbackQuery):
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    buttons = [
        InlineKeyboardButton(text="Входящие запросы", callback_data="requests_income"),
        InlineKeyboardButton(
            text="Исходящие запросы", callback_data="requests_outcome"
        ),
    ]
    buttons.append(
        InlineKeyboardButton(
            text="Назад",
            callback_data=("back_to_main_menu"),
        ),
    )
    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i : i + 2])

    await callback.message.edit_text("Запросы")
    await callback.message.edit_reply_markup(reply_markup=keybroad)


@callbacks_router.callback_query(lambda c: c.data == ("requests_income"))
async def get_income_shift_req(callback: CallbackQuery):
    await get_income_requests(callback)


@callbacks_router.callback_query(lambda c: c.data == ("requests_outcome"))
async def get_outcome_shift_req(callback: CallbackQuery):
    await get_outcome_requests(callback)


@callbacks_router.callback_query(lambda c: c.data.startswith("income_request"))
async def income_request(callback: CallbackQuery):
    data = callback.data
    (
        __,
        id,
    ) = data.split(",")
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    buttons = [
        InlineKeyboardButton(
            text="Принять",
            callback_data=SwapRequestHandler(action="accepted", request_id=id).pack(),
        ),
        InlineKeyboardButton(
            text="Отклонить",
            callback_data=SwapRequestHandler(action="declined", request_id=id).pack(),
        ),
        InlineKeyboardButton(text="Назад", callback_data="requests_outcome"),
    ]
    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i : i + 2])

    await callback.message.edit_text("Что сделать?")
    await callback.message.edit_reply_markup(reply_markup=keybroad)


@callbacks_router.callback_query(lambda c: c.data.startswith("outcome_request"))
async def outcome_request(callback: CallbackQuery):
    data = callback.data
    (
        __,
        id,
    ) = data.split(",")
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    buttons = [
        InlineKeyboardButton(
            text="Отменить",
            callback_data=SwapRequestHandler(action="canceled", request_id=id).pack(),
        ),
        InlineKeyboardButton(text="Назад", callback_data="requests_outcome"),
    ]
    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i : i + 2])

    await callback.message.edit_text("Что сделать?")
    await callback.message.edit_reply_markup(reply_markup=keybroad)


@callbacks_router.callback_query(lambda c: c.data == "schedule_week_key")
async def week_schedule_choose(callback: CallbackQuery):
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    buttons = [
        InlineKeyboardButton(
            text="Эта",
            callback_data=WeekScheduleHandler(week=True).pack(),
        ),
        InlineKeyboardButton(
            text="Следующая",
            callback_data=WeekScheduleHandler(week=False).pack(),
        ),
        InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu"),
    ]
    for i in range(0, len(buttons), 2):
        keybroad.inline_keyboard.append(buttons[i : i + 2])

    await callback.message.edit_text("Выбери неделю")
    await callback.message.edit_reply_markup(reply_markup=keybroad)


@callbacks_router.callback_query(WeekScheduleHandler.filter())
async def week_schedule(callback: CallbackQuery, callback_data: WeekScheduleHandler):
    week = callback_data.week
    result = get_all_schedule(week)
    keybroad = InlineKeyboardMarkup(inline_keyboard=[])
    for day, start, end, name in result:
        button = InlineKeyboardButton(
            text=(f"{day}: {name} {start}--{end}"), callback_data="kek"
        )
        keybroad.inline_keyboard.append([button])
    keybroad.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="schedule_week_key",
            )
        ]
    )
    await callback.message.edit_text("Расписание выбранной недели")
    await callback.message.edit_reply_markup(reply_markup=keybroad)


@callbacks_router.callback_query(SwapRequestHandler.filter())
async def swap_hanlder(callback: CallbackQuery, callback_data: SwapRequestHandler):
    action = callback_data.action
    request_id = callback_data.request_id
    text = shift_swap_handler(request_id, action)
    await callback.answer(text=text, show_alert=True)
    await get_shift_exchange_request(callback)


@callbacks_router.callback_query(AssignNewJun.filter())
async def assign_flow(callback: CallbackQuery, callback_data: AssignNewJun):
    action = callback_data.action
    user_id = callback_data.user_id
    start = callback_data.start
    end = callback_data.end

    if action == "run":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        buttons = []
        users_data = get_users_data()
        for id, name, __ in users_data:
            buttons.append(
                InlineKeyboardButton(
                    text=name,
                    callback_data=AssignNewJun(
                        action="select_start", user_id=id, start=0, end=0
                    ).pack(),
                )
            )
        buttons.append(
            InlineKeyboardButton(
                text="Назад",
                callback_data=("back_to_main_menu"),
            ),
        )

        for i in range(0, len(buttons), 2):
            keyboard.inline_keyboard.append(buttons[i : i + 2])
        await callback.message.edit_text("Выбери админа")
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    elif action == "select_start":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        buttons = []
        for i in range(23):
            buttons.append(
                InlineKeyboardButton(
                    text=(f"{i}:00"),
                    callback_data=AssignNewJun(
                        action="select_end", user_id=user_id, start=i, end=0
                    ).pack(),
                )
            )
        buttons.append(
            InlineKeyboardButton(
                text="Назад",
                callback_data=AssignNewJun(
                    action="run", user_id=0, start=0, end=0
                ).pack(),
            ),
        )
        for i in range(0, len(buttons), 2):
            keyboard.inline_keyboard.append(buttons[i : i + 2])
        await callback.message.edit_text("Выбери начало смены")
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    elif action == "select_end":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        buttons = []
        for i in range(23):
            buttons.append(
                InlineKeyboardButton(
                    text=(f"{i}:00"),
                    callback_data=AssignNewJun(
                        action="end", user_id=user_id, start=start, end=i
                    ).pack(),
                )
            )
        buttons.append(
            InlineKeyboardButton(
                text="Назад",
                callback_data=AssignNewJun(
                    action="select_start", user_id=user_id, start=0, end=0
                ).pack(),
            ),
        )
        for i in range(0, len(buttons), 2):
            keyboard.inline_keyboard.append(buttons[i : i + 2])
        await callback.message.edit_text(
            "Выбери конец смены (система не спросит подтверждения)"
        )
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    elif action == "end":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        buttons = [
            InlineKeyboardButton(
                text="Да",
                callback_data=AssignNewJun(
                    action="confirm", user_id=user_id, start=start, end=end
                ).pack(),
            ),
            InlineKeyboardButton(text="Нет", callback_data="back_to_main_menu"),
        ]
        user_name = ""
        with sqlite3.connect(DB_PATH) as conn:
            result = conn.execute(
                "SELECT full_name FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        user_name = result[0]
        for i in range(0, len(buttons), 2):
            keyboard.inline_keyboard.append(buttons[i : i + 2])

        await callback.message.edit_text(
            f"Поставить админа {user_name} в смену сегодня с {start} до {end}?"
        )
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    elif action == "confirm":
        try:
            insert_uncommon_sheet(user_id, start, end)
            await callback.answer(
                f"Админ на сегодня поставлен с {start} до {end}", show_alert=True
            )
            await callback.message.edit_text("Главное меню")
            await callback.message.edit_reply_markup(reply_markup=start_true(callback))

        except Exception as e:
            logger.error(e)
            await callback.answer("Возникла ошибка", show_alert=True)
            await callback.message.edit_text("Главное меню")
            await callback.message.edit_reply_markup(reply_markup=start_true(callback))


@callbacks_router.callback_query(CalendarCb.filter())
async def calendar_callback(callback: CallbackQuery, callback_data: CalendarCb):
    action = callback_data.action
    day = callback_data.day
    time = callback_data.time
    user_id = get_user_id(callback.from_user.id)
    a = "\n"
    days_int = []
    dates = ""

    id, t, __, selected_days, year, month = get_ancient_sheets(user_id, time=time)
    if day < 10:
        day = f"0{day}"
    day_str = f"{year}-{month}-{day}"
    # if selected_days:
    #     for i in range(len(selected_days)):
    #         days_int.append(int(selected_days[i][-2:]))
    #         dates += f"{selected_days[i]} -- {t[i]} \n"

    if action == "select":
        insert_ancient_sheet(user_id=user_id, day_night=time, date=day_str)
        await callback.answer(f"Выбрана смена {day_str}")
        id, t, __, selected_days, year, month = get_ancient_sheets(user_id, time=time)
        if selected_days:
            for i in range(len(selected_days)):
                days_int.append(int(selected_days[i][-2:]))
                dates += f"{selected_days[i]} -- {t[i]} \n"
        await callback.message.edit_text(f"Твои смены: \n{dates}")
        await callback.message.edit_reply_markup(
            reply_markup=generate_calendar(days_int, time=time)
        )

    elif action == "show":
        id, t, __, selected_days, year, month = get_ancient_sheets(user_id, time=time)
        if selected_days:
            for i in range(len(selected_days)):
                days_int.append(int(selected_days[i][-2:]))
                dates += f"{selected_days[i]} -- {t[i]} \n"
        await callback.message.edit_text(f"Твои смены: \n{dates}")
        await callback.message.edit_reply_markup(
            reply_markup=generate_calendar(days_int, time=time)
        )

    elif action == "delete":
        # insert_ancient_sheet(ins=False, date=day_str)
        # await callback.answer("Смена удалена")
        # id, t, __, selected_days, year, month = get_ancient_sheets(user_id, time=time)
        # if selected_days:
        #     for i in range(len(selected_days)):
        #         days_int.append(int(selected_days[i][-2:]))
        #         dates += f"{selected_days[i]} -- {t[i]} \n"
        # await callback.message.edit_text(f"Твои смены: \n{dates}")
        # await callback.message.edit_reply_markup(
        #     reply_markup=generate_calendar(days_int, time=time)
        # )
        await callback.answer("Не тыкай сюда, это не работает", show_alert=True)

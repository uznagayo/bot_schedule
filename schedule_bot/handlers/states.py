from aiogram.fsm.state import StatesGroup, State

class AddUserSt(StatesGroup):
    name = State()
    telegram_id = State()
    role = State()
    conf = State()

class ShiftClosingStages(StatesGroup):
    supplies_in_place = State()
    cash_closed = State()                # Касса посчитана и закрыта, фотки фелю отправлены
    trash_cleaned = State()             # В залах убран мусор, в том числе в толчках
    kitchen_bin_empty = State()         # Мусорка на кухне вынесена
    no_dishes_in_sink = State()         # Посуды в мойке нет
    no_dishes_in_halls = State()        # Посуды в залах нет
    tea_shelf_stocked = State()         # Чайная полка заполнена
    napkins_ready = State()             # Салфетки на месте        # Расходники в зале есть
    end = State()                    # Завершение процесса закрытия смены


class DbUpdate(StatesGroup):
    action = State()
    table = State()
    column = State()
    value = State()
    id = State()
    conf = State()
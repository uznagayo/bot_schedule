from aiogram.fsm.state import StatesGroup, State

class AddUserSt(StatesGroup):
    name = State()
    telegram_id = State()
    role = State()
    conf = State()

from aiogram.filters.callback_data import CallbackData

class SwapRequestHandler(CallbackData, prefix="swap"):
    action: str
    request_id: int

class WeekScheduleHandler(CallbackData, prefix="week"):
    week: bool


class AssignNewJun(CallbackData, prefix="assign"):
    action: str
    user_id: int
    start: int
    end: int


class CalendarCb(CallbackData, prefix="calendar"):
    action: str
    day: int
    time: bool = True
    user_id: int = 0


class AncientDutiesCb(CallbackData, prefix="ancient"):
    dutie: str
    conf: bool
    time_mark: str
    

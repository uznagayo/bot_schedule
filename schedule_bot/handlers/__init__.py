from .start import start_router
from .shifts import schedule_router
from .callbacks import callbacks_router
from .admin import admin_router
# from .reminders

all_routers = [start_router, schedule_router, callbacks_router, admin_router]


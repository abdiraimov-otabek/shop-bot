from aiogram.dispatcher.filters.state import State, StatesGroup


class DeleteUser(StatesGroup):
    user_id = State()

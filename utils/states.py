from aiogram.dispatcher.filters.state import State, StatesGroup

class UserStates(StatesGroup):
    """States for user interaction"""
    selecting_server = State()
    confirming_purchase = State()
    entering_phone = State()
    waiting_for_payment = State()
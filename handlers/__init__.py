from aiogram import Dispatcher
from handlers import common, user, admin

def register_all_handlers(dp: Dispatcher):
    """Register all handlers for the bot"""
    common.register_handlers(dp)
    user.register_handlers(dp)
    admin.register_handlers(dp)
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from keyboards.user_kb import get_main_menu
from resources.messages import WELCOME_MESSAGE, HELP_MESSAGE
from utils.api import register_user


async def cmd_start(message: types.Message):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # Register user in the backend
    await register_user(user_id, username, first_name)

    # Send welcome message with main menu
    await message.answer(WELCOME_MESSAGE, reply_markup=get_main_menu())


async def cmd_help(message: types.Message):
    """Handle /help command"""
    await message.answer(HELP_MESSAGE, disable_web_page_preview=True, reply_markup=get_main_menu(), parse_mode='HTML')


def register_handlers(dp: Dispatcher):
    """Register common handlers"""
    dp.register_message_handler(cmd_start, CommandStart())
    dp.register_message_handler(cmd_help, CommandHelp())
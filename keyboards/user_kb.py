from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu():
    """Return main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("Получить VPN"), KeyboardButton("Мои VPN ключи"))
    keyboard.row(KeyboardButton("Помощь"), KeyboardButton("Профиль"))
    return keyboard


def get_vpn_keyboard(has_keys=False):
    """Return VPN management keyboard"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    if has_keys:
        keyboard.row(KeyboardButton("Показать QR-коды"))
    else:
        keyboard.row(KeyboardButton("Получить VPN"))

    keyboard.row(KeyboardButton("Вернуться в меню"))
    return keyboard


def get_servers_keyboard(servers):
    """Return keyboard with server selection"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    for server in servers:
        keyboard.add(KeyboardButton(server["server_name"]))

    keyboard.row(KeyboardButton("Отмена"))
    return keyboard
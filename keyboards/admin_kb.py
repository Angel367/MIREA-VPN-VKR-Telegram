from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_menu():
    """Return admin menu keyboard"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("👥 Пользователи"), KeyboardButton("🖥️ Серверы"))
    keyboard.row(KeyboardButton("🔑 Ключи"), KeyboardButton("🗑️ Отозвать ключ"))
    keyboard.row(KeyboardButton("Вернуться в меню"))
    return keyboard
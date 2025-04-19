import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import IDFilter
from keyboards.admin_kb import get_admin_menu
from utils.api import get_all_users, get_all_servers, get_all_keys, revoke_key
from config import ADMIN_IDS

logger = logging.getLogger(__name__)


# Admin states
class AdminStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_key_id = State()


async def cmd_admin(message: types.Message):
    """Handle /admin command"""
    if message.from_user.id not in ADMIN_IDS:
        return

    await message.answer(
        "👑 Админ-панель\n\nВыберите действие:",
        reply_markup=get_admin_menu()
    )


async def admin_show_users(message: types.Message):
    """Show all users to admin"""
    if message.from_user.id not in ADMIN_IDS:
        return

    users = await get_all_users()

    if not users:
        await message.answer("Пользователей не найдено")
        return

    text = "👥 Список пользователей:\n\n"

    for user in users:
        text += (
            f"ID: {user['id']}\n"
            f"Telegram ID: {user['telegram_id']}\n"
            f"Username: {user.get('username', 'Не указан')}\n"
            f"Имя: {user.get('first_name', 'Не указано')}\n"
            f"Активен: {'Да' if user['is_active'] else 'Нет'}\n\n"
        )

    await message.answer(text)


async def admin_show_servers(message: types.Message):
    """Show all servers to admin"""
    if message.from_user.id not in ADMIN_IDS:
        return

    servers = await get_all_servers()

    if not servers:
        await message.answer("Серверы не найдены")
        return

    text = "🖥️ Список серверов:\n\n"

    for server in servers:
        text += (
            f"ID: {server['id']}\n"
            f"Имя: {server['server_name']}\n"
            f"Локация: {server['server_location']}\n"
            f"Активен: {'Да' if server['active'] else 'Нет'}\n\n"
        )

    await message.answer(text)


async def admin_show_keys(message: types.Message):
    """Show all keys to admin"""
    if message.from_user.id not in ADMIN_IDS:
        return

    keys = await get_all_keys()

    if not keys:
        await message.answer("Ключи не найдены")
        return

    text = "🔑 Список ключей:\n\n"

    for key in keys:
        text += (
            f"ID: {key['id']}\n"
            f"Пользователь: {key['user_telegram_id']}\n"
            f"Сервер: {key['server_name']}\n"
            f"Название: {key['name']}\n"
            f"Активен: {'Да' if key['is_active'] else 'Нет'}\n\n"
        )

    await message.answer(text)


async def admin_revoke_key_start(message: types.Message, state: FSMContext):
    """Start revoking a key as admin"""
    if message.from_user.id not in ADMIN_IDS:
        return

    await message.answer("Введите ID ключа для отзыва:")
    await AdminStates.waiting_for_key_id.set()


async def admin_revoke_key_process(message: types.Message, state: FSMContext):
    """Process key ID input for revocation"""
    try:
        key_id = int(message.text)
        result = await revoke_key(key_id)

        if result:
            await message.answer(f"✅ Ключ с ID {key_id} успешно отозван")
        else:
            await message.answer(f"❌ Не удалось отозвать ключ с ID {key_id}")

    except ValueError:
        await message.answer("❌ Некорректный ID ключа. Введите число.")

    except Exception as e:
        logger.error(f"Error revoking key: {e}")
        await message.answer(f"❌ Ошибка при отзыве ключа: {str(e)}")

    finally:
        await state.finish()
        await cmd_admin(message)


def register_handlers(dp: Dispatcher):
    """Register admin handlers"""
    # Admin command
    dp.register_message_handler(cmd_admin, IDFilter(user_id=ADMIN_IDS), commands=["admin"])

    # Admin menu handlers
    dp.register_message_handler(admin_show_users, IDFilter(user_id=ADMIN_IDS), lambda m: m.text == "👥 Пользователи")
    dp.register_message_handler(admin_show_servers, IDFilter(user_id=ADMIN_IDS), lambda m: m.text == "🖥️ Серверы")
    dp.register_message_handler(admin_show_keys, IDFilter(user_id=ADMIN_IDS), lambda m: m.text == "🔑 Ключи")
    dp.register_message_handler(admin_revoke_key_start, IDFilter(user_id=ADMIN_IDS),
                                lambda m: m.text == "🗑️ Отозвать ключ")

    # Admin state handlers
    dp.register_message_handler(admin_revoke_key_process, IDFilter(user_id=ADMIN_IDS),
                                state=AdminStates.waiting_for_key_id)
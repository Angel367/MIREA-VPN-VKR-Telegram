import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.user_kb import get_main_menu, get_servers_keyboard, get_vpn_keyboard
from utils.api import get_user_keys, get_available_servers, create_vpn_key
from utils.vpn import generate_vpn_qr_code
from config import DEFAULT_TRAFFIC_LIMIT_GB, DEFAULT_EXPIRATION_DAYS
from handlers.common import cmd_help

logger = logging.getLogger(__name__)


# States for the conversation
class VPNStates(StatesGroup):
    selecting_server = State()
    confirming_key = State()


async def cmd_profile(message: types.Message):
    """Handle /profile command - show user profile"""
    user_id = message.from_user.id

    # Get user's VPN keys
    keys = await get_user_keys(user_id)

    if not keys:
        await message.answer("У вас пока нет активных VPN ключей. Используйте /vpn для получения доступа.")
        return

    # Prepare profile message
    profile_text = "🔑 Ваши VPN ключи:\n\n"

    for key in keys:
        # Format expiration date and traffic info
        expiration = key.get('expiration_date', 'Бессрочно')
        if expiration and expiration != 'Бессрочно':
            expiration = expiration.split('T')[0]  # Format date to YYYY-MM-DD

        traffic_limit = key.get('traffic_limit', 0)
        traffic_used = key.get('traffic_used', 0)

        if traffic_limit > 0:
            traffic_info = f"{traffic_used / (1024 ** 3):.2f} GB / {traffic_limit / (1024 ** 3):.2f} GB"
        else:
            traffic_info = f"{traffic_used / (1024 ** 3):.2f} GB / Безлимитно"

        # Add key info to profile text
        profile_text += (
            f"🔸 {key['name']}\n"
            f"📍 Сервер: {key['server_name']} ({key['server_location']})\n"
            f"📅 Истекает: {expiration}\n"
            f"📊 Трафик: {traffic_info}\n"
            f"🔗 Статус: {'Активен' if key['is_active'] else 'Неактивен'}\n\n"
        )

    await message.answer(profile_text, reply_markup=get_main_menu())


async def cmd_vpn(message: types.Message):
    """Handle /vpn command - VPN key management"""
    # Get user's VPN keys
    keys = await get_user_keys(message.from_user.id)

    if not keys:
        # User has no keys, offer to create one
        await message.answer(
            "У вас пока нет VPN ключей. Хотите создать новый?",
            reply_markup=get_vpn_keyboard(has_keys=False)
        )
    else:
        # User has keys, show management options
        await message.answer(
            f"У вас {len(keys)} VPN ключ(ей). Что вы хотите сделать?",
            reply_markup=get_vpn_keyboard(has_keys=True)
        )


async def cmd_servers(message: types.Message):
    """Handle /servers command - show available servers"""
    servers = await get_available_servers()

    if not servers:
        await message.answer("В настоящее время нет доступных серверов.")
        return

    text = "🌍 Доступные серверы:\n\n"

    for server in servers:
        text += f"🔹 {server['server_name']} - {server['server_location']}\n"

    await message.answer(text, reply_markup=get_main_menu())


async def process_create_vpn(message: types.Message, state: FSMContext):
    """Process the create VPN button click"""
    servers = await get_available_servers()

    if not servers:
        await message.answer("В настоящее время нет доступных серверов. Пожалуйста, попробуйте позже.")
        return

    await message.answer(
        "Выберите сервер для создания VPN ключа:",
        reply_markup=get_servers_keyboard(servers)
    )

    # Set state to wait for server selection
    await VPNStates.selecting_server.set()

    # Store servers in state data
    await state.update_data(available_servers=servers)


async def process_server_selection(message: types.Message, state: FSMContext):
    """Process server selection"""
    user_data = await state.get_data()
    servers = user_data.get('available_servers', [])

    # Find selected server
    selected_server = None
    for server in servers:
        if server['server_name'] == message.text:
            selected_server = server
            break

    if not selected_server:
        await message.answer(
            "Пожалуйста, выберите сервер из списка",
            reply_markup=get_servers_keyboard(servers)
        )
        return

    # Store selected server
    await state.update_data(selected_server=selected_server)

    # Ask for confirmation
    await message.answer(
        f"Вы выбрали сервер: {selected_server['server_name']} ({selected_server['server_location']})\n\n"
        f"Будет создан VPN ключ со следующими параметрами:\n"
        f"- Трафик: {DEFAULT_TRAFFIC_LIMIT_GB} GB\n"
        f"- Срок действия: {DEFAULT_EXPIRATION_DAYS} дней\n\n"
        f"Подтвердить создание ключа?",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Подтвердить")],
                [types.KeyboardButton(text="Отмена")]
            ],
            resize_keyboard=True
        )
    )

    # Set state to wait for confirmation
    await VPNStates.confirming_key.set()


async def process_key_confirmation(message: types.Message, state: FSMContext):
    """Process key creation confirmation"""
    if message.text != "Подтвердить":
        await message.answer("Создание ключа отменено", reply_markup=get_main_menu())
        await state.finish()
        return

    user_data = await state.get_data()
    selected_server = user_data.get('selected_server')

    if not selected_server:
        await message.answer("Ошибка: сервер не выбран", reply_markup=get_main_menu())
        await state.finish()
        return

    # Show "processing" message
    processing_msg = await message.answer("⏳ Создаем VPN ключ...")

    try:
        # Create VPN key
        key_data = await create_vpn_key(
            user_id=message.from_user.id,
            server_id=selected_server['id'],
            name=f"TG_{message.from_user.id}_{selected_server['server_name']}",
            traffic_limit_gb=DEFAULT_TRAFFIC_LIMIT_GB,
            expiration_days=DEFAULT_EXPIRATION_DAYS
        )

        # Generate QR code
        qr_image = generate_vpn_qr_code(key_data['access_url'])

        from aiogram.utils.markdown import escape_md

        # access_url = escape_md(key_data['access_url'])

        caption = (
            f"✅ <b>VPN ключ успешно создан!</b>\n\n"
            f"📍 <b>Сервер:</b> {selected_server['server_name']} ({selected_server['server_location']})\n"
            f"📅 <b>Срок действия:</b> {DEFAULT_EXPIRATION_DAYS} дней\n"
            f"📊 <b>Трафик:</b> {DEFAULT_TRAFFIC_LIMIT_GB} GB\n\n"
            f"🔑 <b>Конфигурация:</b>\n"
            f"Ссылка <b>на конфигурацию:</b> <code>{key_data['access_url']}</code>\n\n"
            f"Отсканируйте QR-код или скопируйте конфигурацию для настройки VPN-клиента."
        )
        await message.answer_photo(
            qr_image,
            caption=caption,
            parse_mode=types.ParseMode.HTML,
            reply_markup=get_main_menu()
        )

        # Delete processing message
        await processing_msg.delete()

    except Exception as e:
        logger.error(f"Error creating VPN key: {e}")
        await message.answer(
            f"❌ Ошибка при создании VPN ключа. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=get_main_menu()
        )

    # End the conversation
    await state.finish()


async def process_show_keys(message: types.Message):
    """Process show VPN keys button click"""
    # Get user's VPN keys
    keys = await get_user_keys(message.from_user.id)

    if not keys:
        await message.answer(
            "У вас пока нет VPN ключей. Хотите создать новый?",
            reply_markup=get_vpn_keyboard(has_keys=False)
        )
        return

    # Send each key as a separate message with QR code
    for key in keys:
        if not key['is_active']:
            continue

        # Generate QR code
        qr_image = generate_vpn_qr_code(key['access_url'])

        # Format expiration date and traffic info
        expiration = key.get('expiration_date', 'Бессрочно')
        if expiration and expiration != 'Бессрочно':
            expiration = expiration.split('T')[0]  # Format date to YYYY-MM-DD

        traffic_limit = key.get('traffic_limit', 0)
        traffic_used = key.get('traffic_used', 0)

        if traffic_limit > 0:
            traffic_info = f"{traffic_used / (1024 ** 3):.2f} GB / {traffic_limit / (1024 ** 3):.2f} GB"
        else:
            traffic_info = f"{traffic_used / (1024 ** 3):.2f} GB / Безлимитно"

        # Send key info with QR code
        await message.answer_photo(
            qr_image,
            caption=(
                f"🔑 VPN ключ: {key['name']}\n"
                f"📍 Сервер: {key['server_name']} ({key['server_location']})\n"
                f"📅 Истекает: {expiration}\n"
                f"📊 Трафик: {traffic_info}\n\n"
                f"🔗 Конфигурация:\n"
                f"`{key['access_url']}`"
            ),
            parse_mode=types.ParseMode.MARKDOWN
        )

    await message.answer(
        "Выберите действие:",
        reply_markup=get_vpn_keyboard(has_keys=True)
    )


async def process_back_to_menu(message: types.Message):
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=get_main_menu()
    )


def register_handlers(dp: Dispatcher):
    """Register user handlers"""
    # Commands
    dp.register_message_handler(cmd_profile, commands=["profile"])
    dp.register_message_handler(cmd_vpn, commands=["vpn"])
    dp.register_message_handler(cmd_servers, commands=["servers"])

    # Button clicks
    dp.register_message_handler(process_create_vpn, lambda m: m.text == "Получить VPN")
    dp.register_message_handler(process_show_keys, lambda m: m.text == "Мои VPN ключи")
    dp.register_message_handler(process_back_to_menu, lambda m: m.text == "Вернуться в меню")
    dp.register_message_handler(cmd_help, lambda m: m.text == "Помощь")


    # State handlers
    dp.register_message_handler(process_server_selection, state=VPNStates.selecting_server)
    dp.register_message_handler(process_key_confirmation, state=VPNStates.confirming_key)
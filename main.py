import logging
import asyncio
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN, LOG_LEVEL
from handlers import register_all_handlers

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def on_startup(dispatcher):
    """Действия при запуске бота"""
    # Register all handlers
    register_all_handlers(dispatcher)

    logger.info("Bot started")


async def on_shutdown(dispatcher):
    """Действия при остановке бота"""
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

    logger.info("Bot stopped")


if __name__ == '__main__':
    try:
        # Start the bot
        executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
    except Exception as e:
        logger.error(f"Bot error: {e}")
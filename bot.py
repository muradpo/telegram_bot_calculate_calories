
import asyncio
import logging
from aiogram import Bot, Dispatcher, types,  F
from aiogram.filters.command import Command
from config_reader import config
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from app.handlers import router
from aiogram.fsm.storage.memory import MemoryStorage
from app.middlewares.profile_required import ProfileRequiredMiddleware
from app.middlewares.logging_middleware import LoggingMiddleware



bot = Bot(token=config.bot_token.get_secret_value(),
          default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

# Диспетчер
dp = Dispatcher(storage=MemoryStorage())  
# dp.message.middleware(ProfileRequiredMiddleware())

dp.message.middleware(LoggingMiddleware())        

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
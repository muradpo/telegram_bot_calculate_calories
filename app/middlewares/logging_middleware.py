
import logging
from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger("bot")

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        if event.text:
            logger.info(
                f"USER={event.from_user.id} "
                f"USERNAME={event.from_user.username} "
                f"TEXT={event.text}"
            )
        return await handler(event, data)

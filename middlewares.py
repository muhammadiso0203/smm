"""
Middlewares — har bir xabar/callbackdan oldin ishlovchi funksiyalar
"""
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from database import update_last_seen, is_banned

logger = logging.getLogger(__name__)


class BanCheckMiddleware(BaseMiddleware):
    """Ban tekshirish va last_seen yangilash middleware"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Message yoki CallbackQuery dan user olish
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        else:
            return await handler(event, data)

        if not user:
            return await handler(event, data)

        # last_seen yangilash
        update_last_seen(user.id)

        # Ban tekshirish (Adminlar hech qachon bloklanmaydi)
        from config import ADMINS
        if user.id not in ADMINS and is_banned(user.id):
            if isinstance(event, Message):
                await event.answer("🚫 Siz botdan blocklangansiz.")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Siz botdan blocklangansiz!", show_alert=True)
            return 

        return await handler(event, data)

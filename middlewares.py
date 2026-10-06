"""
Middlewares — har bir xabar/callbackdan oldin ishlovchi funksiyalar
"""
import logging
from typing import Any, Awaitable, Callable, Dict, Tuple, List

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery

from database import update_last_seen, is_banned, get_mandatory_channels

logger = logging.getLogger(__name__)


async def check_user_subscription(bot: Bot, user_id: int) -> Tuple[bool, List[dict]]:
    """
    Foydalanuvchining majburiy kanallarga a'zo ekanligini tekshirish.
    (is_subscribed, unsubscribed_channels) qaytaradi.
    """
    from config import ADMINS
    if user_id in ADMINS:
        return True, []

    channels = get_mandatory_channels()
    if not channels:
        return True, []

    unsubscribed = []
    for ch in channels:
        target = str(ch.get("channel_id", "")).strip()
        if not target:
            continue
        try:
            # Agar ID bo'lsa int ga aylantiramiz
            if (target.startswith("-") and target[1:].isdigit()) or target.isdigit():
                chat_target = int(target)
            else:
                chat_target = target if target.startswith("@") else f"@{target}"

            member = await bot.get_chat_member(chat_id=chat_target, user_id=user_id)
            if member.status in ("creator", "administrator", "member"):
                continue
            elif member.status == "restricted" and getattr(member, "is_member", False):
                continue
            else:
                unsubscribed.append(ch)
        except Exception as e:
            logger.warning(f"Kanalga a'zolikni tekshirishda xatolik ({ch.get('title')} / {target}): {e}")
            unsubscribed.append(ch)

    return len(unsubscribed) == 0, unsubscribed


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


class SubscriptionMiddleware(BaseMiddleware):
    """Majburiy kanallarga obunani tekshiruvchi middleware"""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        else:
            return await handler(event, data)

        if not user:
            return await handler(event, data)

        from config import ADMINS
        if user.id in ADMINS:
            return await handler(event, data)

        # Agar callback_data "check_subscription" bo'lsa, handlarga o'tkazamiz
        if isinstance(event, CallbackQuery) and event.data == "check_subscription":
            return await handler(event, data)

        bot: Bot = data.get("bot") or getattr(event, "bot", None)
        if not bot:
            return await handler(event, data)

        # Bazadan kanallarni olib tekshiramiz
        channels = get_mandatory_channels()
        if not channels:
            return await handler(event, data)

        is_sub, unsub = await check_user_subscription(bot, user.id)
        if is_sub:
            return await handler(event, data)

        # Obuna bo'lmagan bo'lsa ogohlantiramiz
        from keyboards import subscription_required_kb
        text = (
            f'<tg-emoji emoji-id="6025976301838405549">⚠️</tg-emoji> <b>Botdan foydalanish uchun homiy kanallarga obuna bo\'ling!</b>\n\n'
            f'Bot xizmatlaridan to\'liq va cheklovlarsiz foydalanish uchun quyidagi kanallarga a\'zo bo\'ling va <b>"✅ Obunani tekshirish"</b> tugmasini bosing:'
        )

        if isinstance(event, Message):
            await event.answer(
                text=text,
                reply_markup=subscription_required_kb(unsub),
                parse_mode="HTML"
            )
            return
        elif isinstance(event, CallbackQuery):
            await event.answer("⚠️ Botdan foydalanish uchun kanallarga a'zo bo'ling!", show_alert=True)
            try:
                await event.message.edit_text(
                    text=text,
                    reply_markup=subscription_required_kb(unsub),
                    parse_mode="HTML"
                )
            except Exception:
                pass
            return


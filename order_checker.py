"""
🔄 Buyurtmalar holatini avtomatik tekshiruvchi fon xizmati (Background Order Checker)
GrandSMM API orqali kutilayotgan buyurtmalar holatini tekshirib turadi.
Buyurtma bajarilganda yoki bekor qilinganda foydalanuvchiga xabar beradi.
"""
import asyncio
import html
import logging
import time
from datetime import datetime
from aiogram import Bot

from config import ADMINS
from database import (
    get_active_orders,
    update_order_status,
    add_user_balance,
    get_orders_channel,
    get_user
)
from smm_api import smm_api

logger = logging.getLogger(__name__)

# Oxirgi marta kam balans haqida ogohlantirilgan vaqt
_last_api_balance_alert = 0


_bot_username = None


async def get_bot_username(bot: Bot) -> str:
    global _bot_username
    if not _bot_username:
        try:
            me = await bot.get_me()
            _bot_username = me.username or "smm_uz_1bot"
        except Exception:
            _bot_username = "smm_uz_1bot"
    return _bot_username


async def send_order_to_channel(bot: Bot, order_type: str, details: dict):
    """
    Buyurtma haqidagi ma'lumotni maxsus kanalga premium emojilar bilan jo'natish
    """
    channel = get_orders_channel()
    if not channel:
        return

    try:
        user_id = details.get("user_id", 0)
        user_name = details.get("user_name", "")
        username = details.get("username", "")

        if (not user_name or not username) and user_id:
            user_data = get_user(user_id)
            if user_data:
                if not user_name:
                    user_name = user_data.get("full_name") or f"Foydalanuvchi {user_id}"
                if not username:
                    username = user_data.get("username") or ""

        # Foydalanuvchi havolasi (ID raqamsiz, faqat profil linki)
        display_name = html.escape(str(user_name or "Foydalanuvchi"))
        if username:
            user_link = f'<a href="https://t.me/{username}">{display_name}</a>'
        elif user_id:
            user_link = f'<a href="tg://user?id={user_id}">{display_name}</a>'
        else:
            user_link = "Foydalanuvchi"

        time_now = datetime.now().strftime("%d.%m.%Y %H:%M")
        order_id = details.get("order_id", "—")
        price = float(details.get("price", 0.0))

        if order_type == "smm":
            service_title = html.escape(str(details.get("service_title", "Xizmat")))
            qty = details.get("quantity", 0)
            link = html.escape(str(details.get("link", "")))
            msg = (
                f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>YANGI BUYURTMA — SMM XIZMATI</b>\n'
                f'━━━━━━━━━━━━━━━━━━━━\n'
                f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{order_id}</code>\n'
                f'<tg-emoji emoji-id="6032609071373226027">👤</tg-emoji> <b>Buyurtmachi:</b> {user_link}\n'
                f'<tg-emoji emoji-id="5456432998092133477">🚀</tg-emoji> <b>Xizmat:</b> <b>{service_title}</b>\n'
                f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji> <b>Miqdori:</b> <b>{qty:,} ta</b>\n'
                f'<tg-emoji emoji-id="5201989772448381592">🔗</tg-emoji> <b>Havola:</b> <code>{link}</code>\n'
                f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>To\'lov summasi:</b> <b>{price:,.0f} so\'m</b>\n'
                f'<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> <b>Holat:</b> <b>Kutilmoqda / Jarayonda</b>\n'
                f'<tg-emoji emoji-id="5849724424957851226">📅</tg-emoji> <b>Sana:</b> <code>{time_now}</code>\n'
                f'━━━━━━━━━━━━━━━━━━━━\n'
                f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <i>Avtomatlashtirilgan SMM xizmati</i>'
            )

        elif order_type == "stars":
            stars_amount = details.get("quantity", 0)
            target_user = html.escape(str(details.get("target_user", details.get("link", ""))))
            msg = (
                f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>YANGI BUYURTMA — TELEGRAM STARS</b>\n'
                f'━━━━━━━━━━━━━━━━━━━━\n'
                f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{order_id}</code>\n'
                f'<tg-emoji emoji-id="6032609071373226027">👤</tg-emoji> <b>Buyurtmachi:</b> {user_link}\n'
                f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Miqdori:</b> <b>{stars_amount:,} Stars</b>\n'
                f'<tg-emoji emoji-id="5201989772448381592">🎯</tg-emoji> <b>Qabul qiluvchi:</b> <code>{target_user}</code>\n'
                f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>To\'lov summasi:</b> <b>{price:,.0f} so\'m</b>\n'
                f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Holat:</b> <b>Bajarildi (Yuborildi)</b>\n'
                f'<tg-emoji emoji-id="5849724424957851226">📅</tg-emoji> <b>Sana:</b> <code>{time_now}</code>\n'
                f'━━━━━━━━━━━━━━━━━━━━\n'
                f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <i>Tezkor Telegram Stars xizmati</i>'
            )

        elif order_type == "number":
            number_str = html.escape(str(details.get("number", "")))
            country_name = html.escape(str(details.get("country_name", "")))
            flag = details.get("flag", "🌍")
            msg = (
                f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> <b>YANGI BUYURTMA — VIRTUAL RAQAM</b>\n'
                f'━━━━━━━━━━━━━━━━━━━━\n'
                f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{order_id}</code>\n'
                f'<tg-emoji emoji-id="6032609071373226027">👤</tg-emoji> <b>Buyurtmachi:</b> {user_link}\n'
                f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> <b>Raqam:</b> <code>{number_str}</code>\n'
                f'🌍 <b>Davlat:</b> {flag} <b>{country_name}</b>\n'
                f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>To\'lov summasi:</b> <b>{price:,.0f} so\'m</b>\n'
                f'<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> <b>Holat:</b> <b>SMS kutilmoqda</b>\n'
                f'<tg-emoji emoji-id="5849724424957851226">📅</tg-emoji> <b>Sana:</b> <code>{time_now}</code>\n'
                f'━━━━━━━━━━━━━━━━━━━━\n'
                f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <i>Avtomatlashtirilgan Virtual SMS xizmati</i>'
            )

        elif order_type == "completed":
            service_title = html.escape(str(details.get("service_title", "Xizmat")))
            qty = details.get("quantity", 0)
            msg = (
                f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>BUYURTMA MUVAFFAQIYATLI BAJARILDI</b>\n'
                f'━━━━━━━━━━━━━━━━━━━━\n'
                f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{order_id}</code>\n'
                f'<tg-emoji emoji-id="6032609071373226027">👤</tg-emoji> <b>Foydalanuvchi:</b> {user_link}\n'
                f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>Xizmat:</b> <b>{service_title}</b>\n'
                f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji> <b>Miqdori:</b> <b>{qty:,} ta</b>\n'
                f'<tg-emoji emoji-id="6026257381678124710">⚡️</tg-emoji> <b>Holat:</b> <b>Bajarildi (Completed)</b>\n'
                f'<tg-emoji emoji-id="5849724424957851226">📅</tg-emoji> <b>Vaqt:</b> <code>{time_now}</code>\n'
                f'━━━━━━━━━━━━━━━━━━━━'
            )

        elif order_type == "canceled":
            service_title = html.escape(str(details.get("service_title", "Xizmat")))
            msg = (
                f'<tg-emoji emoji-id="6028346797368283073">❌</tg-emoji> <b>BUYURTMA BEKOR QILINDI & QAYTARILDI</b>\n'
                f'━━━━━━━━━━━━━━━━━━━━\n'
                f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{order_id}</code>\n'
                f'<tg-emoji emoji-id="6032609071373226027">👤</tg-emoji> <b>Foydalanuvchi:</b> {user_link}\n'
                f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>Xizmat:</b> <b>{service_title}</b>\n'
                f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Qaytarilgan summa:</b> <b>{price:,.0f} so\'m</b>\n'
                f'<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <b>Holat:</b> <i>Server tomonidan bekor qilindi (Mablag\' qaytarildi)</i>\n'
                f'<tg-emoji emoji-id="5849724424957851226">📅</tg-emoji> <b>Vaqt:</b> <code>{time_now}</code>\n'
                f'━━━━━━━━━━━━━━━━━━━━'
            )

        else:
            return

        bot_uname = await get_bot_username(bot)
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="Buyurtma holati",
                callback_data=f"chk_ord:{order_id}",
                icon_custom_emoji_id="5936143551854285132"
            )
        )
        if bot_uname:
            builder.row(
                InlineKeyboardButton(
                    text="Bot orqali buyurtma berish",
                    url=f"https://t.me/{bot_uname}",
                    icon_custom_emoji_id="5456432998092133477"
                )
            )

        await bot.send_message(
            chat_id=channel,
            text=msg,
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )
    except Exception as ex:
        logger.warning(f"Kanalga ({channel}) buyurtma xabarini yuborishda xatolik: {ex}")




async def check_api_balance_alert(bot: Bot, threshold: float = 5000.0, cooldown_seconds: int = 1800):
    """
    GrandSMM API balansi 5,000 so'mdan kam qolganda barcha adminlarga eslatma yuborish
    """
    global _last_api_balance_alert
    now = time.time()
    if now - _last_api_balance_alert < cooldown_seconds:
        return

    try:
        res = await smm_api.get_balance()
        if isinstance(res, dict) and "balance" in res:
            bal = float(res["balance"])
            if bal < threshold:
                _last_api_balance_alert = now
                msg = (
                    f"⚠️ <b>DIQQAT: GrandSMM API Balansi Kam Qoldi!</b>\n\n"
                    f"🌐 <b>Provayder:</b> GrandSMM API\n"
                    f"💰 <b>Qolgan balans:</b> <b>{bal:,.0f} UZS</b>\n"
                    f"⏳ <b>Cheklov darajasi:</b> 5,000 UZS\n\n"
                    f"⚡️ <i>Foydalanuvchilar buyurtmalari to'xtab qolmasligi uchun API hisobini to'ldiring!</i>"
                )
                for admin_id in ADMINS:
                    try:
                        await bot.send_message(chat_id=admin_id, text=msg, parse_mode="HTML")
                    except Exception as ex:
                        logger.warning(f"Admin {admin_id} ga API balans ogohlantirishini yuborishda xatolik: {ex}")

    except Exception as e:
        logger.error(f"check_api_balance_alert xatosi: {e}")


async def check_orders_loop(bot: Bot, interval_seconds: int = 40):
    """
    Buyurtmalar holatini doimiy tekshirib boruvchi asinxron sikl.
    """
    logger.info("🚀 Buyurtmalar statusini avtomatik tekshiruvchi fon xizmati ishga tushdi.")

    while True:
        try:
            # 1. API balansi 5000 dan kam qolganini tekshirish
            await check_api_balance_alert(bot)

            # 2. Faol buyurtmalarni tekshirish
            active_orders = get_active_orders()
            if active_orders:
                for order in active_orders:
                    try:
                        order_id = order["order_id"]
                        user_id = order["user_id"]
                        old_status = (order.get("status") or "").strip()
                        service_title = order.get("service_title", "Xizmat")
                        qty = order.get("quantity", 0)
                        link = order.get("link", "")
                        price = float(order.get("price", 0.0))

                        # Stars yoki boshqa ichki buyurtmalar API dan tekshirilmaydi
                        if order.get("service_id") == 9999:
                            continue

                        # GrandSMM API dan statusni olamiz
                        resp = await smm_api.get_order_status(order_id)
                        if not resp or "status" not in resp:
                            await asyncio.sleep(1.0)
                            continue

                        current_status = str(resp["status"]).strip()
                        status_lower = current_status.lower()

                        # Agar status o'zgarmagan bo'lsa, o'tkazib yuboramiz
                        if status_lower == old_status.lower():
                            await asyncio.sleep(1.0)
                            continue

                        logger.info(f"Order #{order_id} holati o'zgardi: '{old_status}' -> '{current_status}'")

                        # 1. Bajarildi (Completed / Bajarildi / Yakunlandi)
                        if status_lower in ["completed", "bajarildi", "yakunlandi", "success", "done", "выполнено", "готов"]:
                            update_order_status(order_id, "Completed")
                            msg = (
                                f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Buyurtmangiz muvaffaqiyatli bajarildi!</b>\n\n'
                                f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{order_id}</code>\n'
                                f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>Xizmat:</b> <b>{service_title}</b>\n'
                                f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji> <b>Miqdor:</b> <b>{qty:,} ta</b>\n'
                            )
                            if link:
                                msg += f'<tg-emoji emoji-id="5201989772448381592">🔗</tg-emoji> <b>Havola:</b> {link}\n'
                            msg += (
                                f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>To\'lov:</b> <b>{price:,.0f} so\'m</b>\n\n'
                                f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <i>Xizmatimizdan foydalanganingiz uchun rahmat! Yangi buyurtma berish uchun bot menyusidan foydalaning.</i>'
                            )
                            try:
                                await bot.send_message(chat_id=user_id, text=msg, parse_mode="HTML")
                            except Exception as ex:
                                logger.warning(f"Foydalanuvchiga #{order_id} xabarini yuborishda xatolik: {ex}")

                        # 2. Bekor qilindi (Canceled / Cancelled / Bekor qilindi) -> Balansga to'liq qaytarish
                        elif status_lower in ["canceled", "cancelled", "bekor qilindi", "bekor", "отменен", "отменено", "refunded", "failed", "xatolik"]:
                            update_order_status(order_id, "Canceled/Refunded")
                            add_user_balance(user_id, price)
                            refund_msg = (
                                f'<tg-emoji emoji-id="6028346797368283073">❌</tg-emoji> <b>Buyurtmangiz bekor qilindi</b>\n\n'
                                f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{order_id}</code>\n'
                                f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>Xizmat:</b> <b>{service_title}</b>\n'
                                f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Qaytarilgan mablag\':</b> <b>{price:,.0f} so\'m</b>\n\n'
                                f'<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <i>Buyurtma server tomonidan bekor qilindi va sarflangan to\'liq mablag\' balansingizga qaytarildi.</i>'
                            )
                            try:
                                await bot.send_message(chat_id=user_id, text=refund_msg, parse_mode="HTML")
                            except Exception as ex:
                                logger.warning(f"Foydalanuvchiga #{order_id} bekor xabarini yuborishda xatolik: {ex}")



                        # 3. Qisman bajarildi (Partial / Qisman) -> Qolgan qismi hisoblanib qaytariladi
                        elif status_lower in ["partial", "qisman", "qisman bajarildi", "частично"]:
                            remains = int(resp.get("remains", 0)) if str(resp.get("remains", "")).isdigit() else 0
                            refund_amount = 0.0
                            if qty > 0 and remains > 0:
                                refund_amount = round((remains / qty) * price, 2)
                                add_user_balance(user_id, refund_amount)
                            update_order_status(order_id, "Partial/Refunded")

                            partial_msg = (
                                f'<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <b>Buyurtmangiz qisman bajarildi</b>\n\n'
                                f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{order_id}</code>\n'
                                f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>Xizmat:</b> <b>{service_title}</b>\n'
                                f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji> <b>Bajarilmay qolgan miqdor:</b> <b>{remains:,} ta</b>\n'
                            )
                            if refund_amount > 0:
                                partial_msg += f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Balansingizga qaytarildi:</b> <b>{refund_amount:,.0f} so\'m</b>\n\n'
                            partial_msg += '<i>Bajarilmagan miqdor uchun to\'lov balansingizga qaytarildi.</i>'
                            try:
                                await bot.send_message(chat_id=user_id, text=partial_msg, parse_mode="HTML")
                            except Exception as ex:
                                logger.warning(f"Foydalanuvchiga #{order_id} qisman xabarini yuborishda xatolik: {ex}")

                        else:
                            # In progress, Processing, Pending bo'lsa faqat statusni bazada yangilab qo'yamiz
                            update_order_status(order_id, current_status)

                        # Har bir buyurtma tekshiruvi orasida 1.5 soniya tanaffus (API limitini asrash)
                        await asyncio.sleep(1.5)

                    except Exception as order_err:
                        logger.error(f"Buyurtma #{order.get('order_id')} ni tekshirishda xatolik: {order_err}")

        except Exception as e:
            logger.error(f"check_orders_loop siklida xatolik: {e}")

        # Navbatdagi tekshiruvgacha kutish
        await asyncio.sleep(interval_seconds)

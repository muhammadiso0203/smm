"""
🤖 SMM Bot Avtomatik To'lov Userboti (Telethon)
@humocardbot dan kelgan SMS xabarlarni eshitib, to'lovlarni avtomatik tasdiqlaydi.
"""
import re
import asyncio
import logging
from telethon import TelegramClient, events
import aiohttp

from config import (
    TELEGRAM_API_ID, 
    TELEGRAM_API_HASH, 
    HUMOCARD_BOT_USERNAME, 
    BOT_TOKEN, 
    ADMINS,
    CARD_NUMBER
)
from database import find_pending_deposit_by_amount, complete_deposit

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s — %(message)s")
logger = logging.getLogger("userbot")

client = TelegramClient("smm_userbot_session", TELEGRAM_API_ID, TELEGRAM_API_HASH)


async def send_bot_message(chat_id: int, text: str):
    """Telegram Bot orqali foydalanuvchiga bildirishnoma yuborish"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status != 200:
                    logger.error(f"Xabar yuborish xatosi HTTP {resp.status}: {await resp.text()}")
    except Exception as e:
        logger.error(f"Telegram API yuborish xatosi: {e}")


@client.on(events.NewMessage(chats=HUMOCARD_BOT_USERNAME))
async def humo_notification_handler(event):
    text = event.message.message or ""
    logger.info(f"📩 HumoCard botdan yangi xabar:\n{text}")

    # Faqat to'ldirish (kirim) xabarlarini qayta ishlaymiz
    if "to'ldirish" not in text.lower() and "+" not in text and "➕" not in text:
        logger.info("ℹ️ Bu kirim to'lovi emas, o'tkazib yuborildi.")
        return

    # Summani ajratib olamiz (Masalan: ➕ 1.000,00 UZS yoki ➕ 10.005,00 UZS)
    match = re.search(r'[+➕]\s*([\d\.\s]+)(?:[,\.]\d{2})?\s*UZS', text, re.IGNORECASE)
    if not match:
        logger.warning("⚠️ Xabardan summani aniqlab bo'lmadi.")
        return

    raw_sum = match.group(1).replace('.', '').replace(' ', '').strip()
    try:
        received_amount = int(raw_sum)
    except ValueError:
        logger.error(f"Noto'g'ri summa raqami: {raw_sum}")
        return

    logger.info(f"💰 Qabul qilingan summa: {received_amount} so'm")

    # Bazadan ushbu aniq summa bo'yicha kutilayotgan to'lovni topamiz
    dep = find_pending_deposit_by_amount(received_amount)
    if not dep:
        logger.warning(f"⚠️ {received_amount} so'm miqdorida 5 daqiqa ichida kutilayotgan faol to'lov topilmadi!")
        for admin_id in ADMINS:
            await send_bot_message(
                admin_id,
                f"⚠️ <b>Noma'lum to'lov tushdi!</b>\n\n"
                f"💰 Summa: <b>{received_amount:,} so'm</b>\n"
                f"Karta: *{CARD_NUMBER[-4:]}\n\n"
                f"<i>Bazada ushbu summada 5 daqiqa ichida kutilayotgan faol to'lov topilmadi.</i>"
            )
        return

    # To'lovni tasdiqlaymiz va foydalanuvchi balansiga qo'shamiz
    completed = complete_deposit(dep["id"])
    if not completed:
        logger.error(f"To'lovni yakunlashda xatolik yuz berdi: deposit_id={dep['id']}")
        return

    user_id = dep["user_id"]
    credited_amount = dep["amount"]
    new_balance = completed["new_balance"]

    logger.info(f"✅ To'lov muvaffaqiyatli yakunlandi! Foydalanuvchi: {user_id}, Summa: {credited_amount}, Yangi balans: {new_balance}")

    # Foydalanuvchiga bot nomidan xushxabar yuborish
    user_msg = (
        f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>To\'lovingiz muvaffaqiyatli qabul qilindi!</b>\n\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Qo\'shilgan mablag\':</b> <b>{credited_amount:,} so\'m</b>\n'
        f'<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>Sizning balansingiz:</b> <b>{new_balance:,.0f} so\'m</b>\n\n'
        f'Endi bot xizmatlaridan bemalol buyurtma berishingiz mumkin! 🚀'
    )
    await send_bot_message(user_id, user_msg)

    # Adminga to'lov hisoboti
    for admin_id in ADMINS:
        await send_bot_message(
            admin_id,
            f"💸 <b>To'lov muvaffaqiyatli qabul qilindi!</b>\n\n"
            f"👤 Foydalanuvchi: <code>{user_id}</code>\n"
            f"💳 Kartaga tushdi: <b>{received_amount:,} so'm</b>\n"
            f"➕ Balansga qo'shildi: <b>{credited_amount:,} so'm</b>\n"
            f"💰 Yangi balansi: <b>{new_balance:,.0f} so'm</b>"
        )


async def main():
    logger.info("🚀 Userbot ishga tushmoqda...")
    await client.start()
    me = await client.get_me()
    logger.info(f"✅ Userbot akkauntga ulandi: {me.first_name} (@{me.username or 'username_mavjud_emas'})")
    logger.info(f"👀 @{HUMOCARD_BOT_USERNAME} xabarlari kuzatuvga olindi...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    client.loop.run_until_complete(main())

"""
🤖 Telegram Bot — Asosiy ishga tushirish fayli (aiogram 3)
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from config import BOT_TOKEN, LOG_FILE
from database import init_db
from order_checker import check_orders_loop
from middlewares import BanCheckMiddleware
from handlers.admin import router as admin_router
from handlers.user import router as user_router

# ──────────────────────────────────────────
#  Logging sozlash
# ──────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────
#  Fallback router (barcha boshqa routerlardan keyin ishlaydi)
# ──────────────────────────────────────────

fallback_router = Router()

@fallback_router.message()
async def unknown_message(message: Message):
    await message.answer(
        "❓ Buyruqni tushunmadim.\n"
        "Yordam uchun /help yozing."
    )


# ──────────────────────────────────────────
#  Ishga tushirish
# ──────────────────────────────────────────

async def main():
    logger.info("🚀 Bot ishga tushmoqda...")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Ma'lumotlar bazasini tayyor qilish
    init_db()

    # Middlewarelarni ulash
    dp.message.middleware(BanCheckMiddleware())
    dp.callback_query.middleware(BanCheckMiddleware())

    # Routerlarni ulash (tartib juda muhim!)
    # 1. Admin buyruqlari
    # 2. Foydalanuvchi buyruqlari (/start, /help, menyu)
    # 3. Noma'lum xabarlar (faqat hech biri to'g'ri kelmaganda)
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(fallback_router)

    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")

    # Fon xizmati: Buyurtmalar holatini avtomatik tekshiruvchi task
    asyncio.create_task(check_orders_loop(bot, interval_seconds=30))

    # Polling boshlash
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Bot to'xtatildi.")

import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ============================================
#   BOT KONFIGURATSIYASI
# ============================================

# Telegram Bot Token (@BotFather dan oling)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Admin foydalanuvchi ID lari (Telegram ID lari vergul bilan: "12345,67890")
raw_admins = os.getenv("ADMINS", "")
ADMINS = [int(admin_id.strip()) for admin_id in raw_admins.split(",") if admin_id.strip().isdigit()]
if not ADMINS:
    ADMINS = [123456789]

# Ma'lumotlar bazasi fayli
DATABASE = os.getenv("DATABASE", "database.db")

# Bot nomi va tavsifi
BOT_NAME = os.getenv("BOT_NAME", "SMM UZ Bot")
BOT_USERNAME = os.getenv("BOT_USERNAME", "@smm_uz_1bot")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@Sergelidanman")

# Kanal / Guruh (majburiy obuna uchun, kerak bo'lmasa None)
raw_channel_id = os.getenv("CHANNEL_ID", "").strip()
CHANNEL_ID = int(raw_channel_id) if raw_channel_id.lstrip("-").isdigit() else None
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "").strip() or None

# Xabar cheklovi (soniyada)
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "1"))

# Log fayli
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# ============================================
#   GrandSMM API SOZLAMALARI
# ============================================
SMM_API_URL = os.getenv("SMM_API_URL", "https://grandsmm.surkhandc2.uz/api/v2")
NUMBER_API_URL = os.getenv("NUMBER_API_URL", "https://grandsmm.surkhandc2.uz/api/v2/nomer")
SMM_API_KEY = os.getenv("SMM_API_KEY") or os.getenv("api", "")
PRICE_MARGIN_PERCENT = float(os.getenv("PRICE_MARGIN_PERCENT", "20"))  # APIdagi narxga 20% ustama qo'shish
STAR_PRICE_UZS = float(os.getenv("STAR_PRICE_UZS", "260"))  # 1 dona Telegram Star narxi (so'mda)

# ============================================
#   USERBOT VA TO'LOV SOZLAMALARI
# ============================================
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "24412350"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "ffee904f060c14e69a6e0d56606fd0ca")
CARD_NUMBER = os.getenv("CARD_NUMBER", "9860350149788134")
CARD_HOLDER = os.getenv("CARD_HOLDER", "MUHAMMAD ISO IKROMIDDINOV")
HUMOCARD_BOT_USERNAME = os.getenv("HUMOCARD_BOT_USERNAME", "humocardbot")

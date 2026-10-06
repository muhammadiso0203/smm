# 🤖 Telegram Bot

Python + aiogram 3.x yordamida yozilgan professional Telegram bot.

---

## 📁 Fayl strukturasi

```
smm bot/
├── .env              # Maxfiy token va sozlamalar (muhit o'zgaruvchilari)
├── .env.example      # Namuna sozlamalar fayli
├── .gitignore        # Git uchun e'tiborga olinmaydigan fayllar
├── main.py           # Asosiy ishga tushirish fayli
├── config.py         # Konfiguratsiya (.env dan o'qiydi)
├── database.py       # SQLite ma'lumotlar bazasi
├── keyboards.py      # Reply & Inline klaviaturalar
├── middlewares.py    # Ban tekshirish middleware
├── requirements.txt  # Kerakli kutubxonalar
└── handlers/
    ├── __init__.py
    ├── user.py       # Foydalanuvchi handlerlari
    └── admin.py      # Admin handlerlari
```

---

## ⚙️ O'rnatish va Ishga tushirish

### 1. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 2. Sozlamalarni `.env` fayliga kiritish

[`.env`](file:///c:/Users/user/Desktop/botlar/smm%20bot/.env) faylini oching va bot tokeningizni kiriting:

```env
BOT_TOKEN=1234567890:AAF...
ADMINS=123456789
```

> **Telegram ID ni bilmaysizmi?** Botni ishga tushirib `/id` buyrug'ini yuboring.

### 3. Botni ishga tushirish

```bash
python main.py
```

---

## 🛠 Funksiyalar

| Funksiya | Tavsif |
|---|---|
| `/start` | Botni ishga tushirish, xush kelibsiz xabari |
| `/help` | Yordam xabari |
| `/id` | Telegram ID ni ko'rish |
| `/admin` | Admin panelga kirish |
| `/user [ID]` | Foydalanuvchi ma'lumotlarini ko'rish |
| `/cancel` | Joriy amalni bekor qilish |
| 📊 Statistika | Foydalanuvchilar statistikasi |
| 📢 Broadcast | Barcha foydalanuvchilarga xabar yuborish |
| 🚫 Ban | Foydalanuvchini bloklash / blokdan chiqarish |

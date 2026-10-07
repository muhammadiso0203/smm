"""
🤖 SMM Bot — Userbot Sessiyasini Faollashtirish Skripti
Bu skript orqali Telegram akkauntingizga ulanib, smm_userbot_session.session faylini yaratasiz.
"""
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH


async def main():
    print("\n" + "=" * 55)
    print("📲 TELEGRAM USERBOTNI FAOLLASHTIRISH")
    print("=" * 55)

    client = TelegramClient("smm_userbot_session", TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"✅ Akkaunt allaqachon ulangan: {me.first_name} (@{me.username or 'username_yoq'})")
        print("Sessiya fayli mavjud va faol!")
        await client.disconnect()
        return

    phone = input("\n📞 Telefon raqamingizni kiriting (+998...): ").strip().replace(" ", "")
    
    print("⏳ Kod yuborilmoqda...")
    sent = await client.send_code_request(phone)

    print("\n" + "─" * 55)
    print("👉 DIQQAT: Kod telefoningizdagi TELEGRAM ILOVASIGA yuborildi!")
    print("   (Telegram ichidagi 'Telegram' degan rasmiy xabarni oching)")
    print("─" * 55)

    code = input("\n🔑 Telegram ilovangizga kelgan kodni kiriting: ").strip().replace(" ", "")

    try:
        await client.sign_in(phone=phone, code=code)
    except SessionPasswordNeededError:
        print("\n🔐 Ushbu akkauntda 2FA (Ikki bosqichli parol) o'rnatilgan.")
        password = input("2FA Parolingizni kiriting: ").strip()
        await client.sign_in(password=password)
    except Exception as e:
        print(f"\n❌ Kirishda xatolik yuz berdi: {e}")
        await client.disconnect()
        return

    me = await client.get_me()
    print("\n" + "=" * 55)
    print(f"🎉 TABRIKLAYMIZ! Akkaunt muvaffaqiyatli ulandi:")
    print(f"👤 Ism: {me.first_name}")
    print(f"🔗 Username: @{me.username or 'yoq'}")
    print(f"🆔 Telegram ID: {me.id}")
    print("💾 Sessiya fayli yaratildi: smm_userbot_session.session")
    print("=" * 55 + "\n")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

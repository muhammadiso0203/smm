"""
🤖 SMM Bot — Userbot Sessiyasini Faollashtirish Skripti
"""
import os
import asyncio
from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError, 
    FloodWaitError, 
    PhoneNumberInvalidError, 
    PhoneCodeInvalidError, 
    PhoneCodeExpiredError
)
from telethon.tl.types.auth import (
    SentCodeTypeApp, 
    SentCodeTypeSms, 
    SentCodeTypeCall, 
    SentCodeTypeFlashCall, 
    SentCodeTypeMissedCall, 
    SentCodeTypeEmailCode
)
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH


async def main():
    print("\n" + "=" * 60)
    print("📲 TELEGRAM USERBOTNI FAOLLASHTIRISH")
    print("=" * 60)

    session_name = "smm_userbot_session"
    client = TelegramClient(
        session_name, 
        TELEGRAM_API_ID, 
        TELEGRAM_API_HASH,
        device_model="Desktop PC",
        system_version="Linux x86_64",
        app_version="4.16.8",
        lang_code="uz"
    )

    try:
        await client.connect()
    except Exception as e:
        if "AuthKeyDuplicated" in str(e) or "AuthKeyDuplicatedError" in str(e.__class__.__name__):
            print("\n⚠️ Eski sessiya IP-manzil o'zgargani uchun bekor qilingan. Yangi toza sessiya yaratilmoqda...")
            try:
                await client.disconnect()
            except Exception:
                pass
            for ext in ["", ".session", ".session-journal"]:
                fname = session_name + ext
                if os.path.exists(fname):
                    try:
                        os.remove(fname)
                    except Exception:
                        pass
            client = TelegramClient(
                session_name, 
                TELEGRAM_API_ID, 
                TELEGRAM_API_HASH,
                device_model="Desktop PC",
                system_version="Linux x86_64",
                app_version="4.16.8",
                lang_code="uz"
            )
            await client.connect()
        else:
            print(f"❌ Ulanishda xatolik: {e}")
            return

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"\n✅ Akkaunt allaqachon ulangan: {me.first_name} (@{me.username or 'yoq'})")
        print("Sessiya fayli mavjud va tayyor: smm_userbot_session.session")
        await client.disconnect()
        return

    phone = input("\n📞 Telefon raqamingizni kiriting (+99890... shaklida): ").strip().replace(" ", "")
    if not phone.startswith("+"):
        phone = "+" + phone

    print(f"\n⏳ Telegram serveriga kod so'rovi yuborilmoqda ({phone})...")
    
    try:
        sent = await client.send_code_request(phone)
    except FloodWaitError as e:
        print(f"\n⚠️ Telegram vaqtinchalik cheklov qo'ydi. Iltimos {e.seconds} soniyadan keyin qayta urinib ko'ring.")
        await client.disconnect()
        return
    except PhoneNumberInvalidError:
        print("\n❌ Noto'g'ri telefon raqami kiritildi. Iltimos +998... formatida to'g'ri kiriting.")
        await client.disconnect()
        return
    except Exception as e:
        print(f"\n❌ Kod so'rashda xatolik: {e}")
        await client.disconnect()
        return

    # Kod qayerga ketganini aniqlaymiz
    code_type_name = type(sent.type).__name__
    print("\n" + "─" * 60)
    if isinstance(sent.type, SentCodeTypeApp):
        print("📨 KOD TELEGRAM ILOVASIGA YUBORILDI!")
        print("👉 Telefoningizdagi yoki kompyuterdagi Telegram ilovasini oching.")
        print("👉 'Telegram' (yoki 777000) nomli rasmiy chatga kelgan 5 xonali kodni oling.")
    elif isinstance(sent.type, SentCodeTypeSms):
        print("📱 KOD TELEFONINGIZGA ODDIY SMS ORQALI YUBORILDI!")
        print("👉 Telefoningizning SMS qutisini tekshiring.")
    elif isinstance(sent.type, SentCodeTypeEmailCode):
        print("📧 KOD EMAIL POCHANGIZGA YUBORILDI!")
        print("👉 Telegram akkauntingizga ulangan elektron pochtangizni tekshiring.")
    elif isinstance(sent.type, (SentCodeTypeCall, SentCodeTypeFlashCall, SentCodeTypeMissedCall)):
        print("📞 TELEFONINGIZGA QO'NG'IROQ BO'LMOQDA!")
        print("👉 Qo'ng'iroq orqali aytilgan kodni tinglang yoki oxirgi raqamlarini kiriting.")
    else:
        print(f"ℹ️ Kod yuborildi (Turi: {code_type_name}). Telegram ilovangizni yoki SMS ni tekshiring.")
    print("─" * 60)

    code = input("\n🔑 Kelgan kodni kiriting: ").strip().replace(" ", "").replace("-", "")

    try:
        await client.sign_in(phone=phone, code=code)
    except SessionPasswordNeededError:
        print("\n🔐 Ushbu akkauntda 2FA (Ikki bosqichli parol) mavjud.")
        password = input("2FA Parolingizni kiriting: ").strip()
        try:
            await client.sign_in(password=password)
        except Exception as p_err:
            print(f"❌ Parol noto'g'ri: {p_err}")
            await client.disconnect()
            return
    except PhoneCodeInvalidError:
        print("\n❌ Kiritilgan kod noto'g'ri! Iltimos, qaytadan urinib ko'ring.")
        await client.disconnect()
        return
    except PhoneCodeExpiredError:
        print("\n❌ Kodning muddati o'tgan. Iltimos, qaytadan urinib ko'ring.")
        await client.disconnect()
        return
    except Exception as e:
        print(f"\n❌ Kirishda xatolik: {e}")
        await client.disconnect()
        return

    me = await client.get_me()
    print("\n" + "=" * 60)
    print(f"🎉 TABRIKLAYMIZ! Akkaunt muvaffaqiyatli ulandi:")
    print(f"👤 Ism: {me.first_name}")
    print(f"🔗 Username: @{me.username or 'yoq'}")
    print(f"🆔 Telegram ID: {me.id}")
    print("💾 Sessiya fayli muvaffaqiyatli yaratildi: smm_userbot_session.session")
    print("=" * 60 + "\n")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

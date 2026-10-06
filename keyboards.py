from typing import Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def my_inline_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="SMM Xizmati",
            callback_data="smm",
            icon_custom_emoji_id="6028346797368283073",
            style="success"
        ),
        InlineKeyboardButton(
            text="Nomer Olish",
            callback_data="number",
            icon_custom_emoji_id="5444965061749644170",
            style="success"
        )
    )

    builder.row(
        InlineKeyboardButton(
            text="Stars Xizmati",
            callback_data="stars",
            icon_custom_emoji_id="5897792062291449826",
            style="danger"
        ),
        # InlineKeyboardButton(
        #     text="Premium Olish",
        #     callback_data="premium",
        #     icon_custom_emoji_id="5204141284775697953",
        #     style="danger"
        # ),
        InlineKeyboardButton(
            text="Buyurtmalarim",
            callback_data="buyurtmalarim",
            icon_custom_emoji_id="5864114012542736772",
            style="primary"
        ),
    )

    # builder.row(
    #     InlineKeyboardButton(
    #         text="UC Olish",
    #         callback_data="uc",
    #         icon_custom_emoji_id="5314544952422704045",
    #         style="primary"
    #     ),
    # )
    builder.row(
        InlineKeyboardButton(
            text="Hisobim",
            callback_data="hisobim",
            icon_custom_emoji_id="5444856076954520455",
            style="success"
        ),
        InlineKeyboardButton(
            text="Qo'llab Quvvatlash",
            callback_data="support",
            icon_custom_emoji_id="5202075822118166834",
            style="success"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Hisob To'ldirish",
            callback_data="hisob_to'ldirish",
            icon_custom_emoji_id="6025976946083500432",
            style="danger"
        )
    )

    if is_admin:
        builder.row(
            InlineKeyboardButton(
                text="👑 Admin Panel",
                callback_data="adm:main",
                icon_custom_emoji_id="5444856076954520455",
                style="primary"
            )
        )

    return builder.as_markup()


def smm_social_menu() -> InlineKeyboardMarkup:
    """SMM ijtimoiy tarmoqlar menyusi"""
    builder = InlineKeyboardBuilder()

    # 1-qator: Telegram va Instagram
    builder.row(
        InlineKeyboardButton(
            text="Telegram", 
            callback_data="smm_telegram",
            icon_custom_emoji_id="5866355487255039002",
            style="success"
        ),
        InlineKeyboardButton(
            text="Instagram", 
            callback_data="smm_instagram", 
            icon_custom_emoji_id="5319160079465857105",
            style="success"
        )
    )

    # 2-qator: TikTok va YouTube
    builder.row(
        InlineKeyboardButton(
            text="TikTok", 
            callback_data="smm_tiktok",
            icon_custom_emoji_id="5940686918583849152",
            style="danger"
        ),
        InlineKeyboardButton(
            text="YouTube", 
            callback_data="smm_youtube",
            icon_custom_emoji_id="5368482410151295168",
            style="danger"
        )
    )

    # 3-qator: Orqaga
    builder.row(
        InlineKeyboardButton(
            text="Orqaga", 
            callback_data="back_to_main",
            icon_custom_emoji_id="5416113713428057601",
            style="primary"
        )
    )

    return builder.as_markup()


def telegram_services_menu() -> InlineKeyboardMarkup:
    """Telegram xizmatlari menyusi (1 tadan qator)"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(
        text="Telegram Obunachi", 
        callback_data="tg_subs",
        icon_custom_emoji_id="6032609071373226027",
        )
    )
    builder.row(InlineKeyboardButton(
        text="Premium Obunachi", 
        callback_data="tg_premium_subs",
        icon_custom_emoji_id="6026011288641998567",
        )
    )
    builder.row(InlineKeyboardButton(
        text="Bot uchun Obunachi", 
        callback_data="tg_bot_subs",
        icon_custom_emoji_id="6030400221232501136",
        )
    )
    builder.row(InlineKeyboardButton(
        text="Telegram Ko'rishlar", 
        callback_data="tg_views",
        icon_custom_emoji_id="5325847485279652235",
        )
    )
    builder.row(InlineKeyboardButton(
        text="Telegram Reaksiyalar", 
        callback_data="tg_reactions",
        icon_custom_emoji_id="5373005951311812951",
        )
    )
    builder.row(InlineKeyboardButton(
        text="Telegram coment", 
        callback_data="tg_comments",
        icon_custom_emoji_id="5767258028956978383",
        )
    )
    builder.row(InlineKeyboardButton(
        text="POST Ulashishlar", 
        callback_data="tg_shares",
        icon_custom_emoji_id="5852830669599674051",
        )
    )
    builder.row(InlineKeyboardButton(
        text="Telegram BOOST", 
        callback_data="tg_boost",
        icon_custom_emoji_id="5884428842780594914",
        )
    )
    builder.row(InlineKeyboardButton(
        text="So'rovnomaga ovoz", 
        callback_data="tg_poll",
        icon_custom_emoji_id="5936143551854285132",
        )
    )
    builder.row(InlineKeyboardButton(
        text="Telegram STORY", 
        callback_data="tg_story",
        icon_custom_emoji_id="6028346797368283073",
        )
    )
    builder.row(InlineKeyboardButton(
        text="O'zbek xizmatlar", 
        callback_data="tg_uzbek",
        icon_custom_emoji_id="5224417984293938277",
        )
    )
    builder.row(InlineKeyboardButton(
        text="Orqaga", 
        callback_data="smm",
        icon_custom_emoji_id="5416113713428057601",
        )
    )

    return builder.as_markup()


def telegram_subscribers_menu() -> InlineKeyboardMarkup:
    """Telegram Obunachi xizmatlari menyusi"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(
        text="Obunachi (Arzon-sekin)", 
        callback_data="tg_sub_cheap",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Obunachi (tezkor kafolatli)", 
        callback_data="tg_sub_fast_guaranteed",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Obunachi tezkor (kanal uchun)", 
        callback_data="tg_sub_fast_channel",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Obunachi (Online+sharx)", 
        callback_data="tg_sub_online_reviews",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Obunachi (Aqilli-Ai)", 
        callback_data="tg_sub_ai",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Obunachi (haqiqiy account)", 
        callback_data="tg_sub_real",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Obunachi (jonli/aktiv)", 
        callback_data="tg_sub_active"   ,
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Obunachi (zayafka)", 
        callback_data="tg_sub_request",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga", 
        callback_data="smm_telegram",
        icon_custom_emoji_id="5416113713428057601"
    ))

    return builder.as_markup()


def tg_sub_cheap_menu() -> InlineKeyboardMarkup:
    """Telegram Arzon-sekin obunachilar tariflari menyusi"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(
        text="TG Obunachi 1-kun kafolatli - 500 so'm", 
        callback_data="buy_tg_1d",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 7-kun kafolatli - 1 495 so'm", 
        callback_data="buy_tg_7d",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 14-kun kafolatli - 1 995 so'm", 
        callback_data="buy_tg_14d",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 30-kun kafolatli - 2 985 so'm", 
        callback_data="buy_tg_30d",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 60-kun kafolatli - 3 975 so'm", 
        callback_data="buy_tg_60d",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 90-kun kafolatli - 4 755 so'm", 
        callback_data="buy_tg_90d",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 180-kun kafolatli - 6 690 so'm", 
        callback_data="buy_tg_180d",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 365-kun kafolatli - 9 410 so'm", 
        callback_data="buy_tg_365d",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi butun umr kafolatli - 13 650 so'm", 
        callback_data="buy_tg_lifetime",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Rus Obunachi 30 kunlik kafolatli - 15 450 so'm", 
        callback_data="buy_tg_rus30d",
        icon_custom_emoji_id="5262866437038421122"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga", 
        callback_data="tg_subs",
        icon_custom_emoji_id="5416113713428057601"
    ))

    return builder.as_markup()


def service_detail_keyboard(service_code: Any, back_callback: str = "tg_sub_cheap") -> InlineKeyboardMarkup:
    """Xizmat tafsilotlari ostidagi tugmalar"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(
        text='Buyurtma berish',
        callback_data=f"order_{service_code}",
        icon_custom_emoji_id="5456432998092133477"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data=back_callback,
        icon_custom_emoji_id="5416113713428057601"
    ))

    return builder.as_markup()


def confirm_order_keyboard() -> InlineKeyboardMarkup:
    """Buyurtmani tasdiqlash tugmalari"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Tasdiqlash",
            callback_data="confirm_order",
            icon_custom_emoji_id="5456432998092133477"
        ),
        InlineKeyboardButton(
            text="Bekor qilish",
            callback_data="cancel_order",
            icon_custom_emoji_id="6032903688949862892"
        )
    )
    return builder.as_markup()


def telegram_views_menu() -> InlineKeyboardMarkup:
    """Telegram Ko'rishlar xizmatlari menyusi"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(
        text="Telegram ko'rishlar (prasmotr)",
        callback_data="tg_views_prasmotr",
        icon_custom_emoji_id="5325847485279652235"
    ))
    builder.row(InlineKeyboardButton(
        text="Telegram Avto ko'rishlar (eski post)",
        callback_data="tg_views_auto_old",
        icon_custom_emoji_id="5233246225146332642"
    ))
    builder.row(InlineKeyboardButton(
        text="Telegram avto ko'rishlar (yangi post)",
        callback_data="tg_views_auto_new",
        icon_custom_emoji_id="5210956306952758910"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="smm_telegram",
        icon_custom_emoji_id="5416113713428057601"
    ))

    return builder.as_markup()


def tg_views_prasmotr_menu() -> InlineKeyboardMarkup:
    """Telegram Bir martalik ko'rishlar (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Bir post uchun [tezkor] - 251 so'm",
        callback_data="buy_service_740",
        icon_custom_emoji_id="5325847485279652235"
    ))
    builder.row(InlineKeyboardButton(
        text="TG ko'rishlar [API+] - 1 739 so'm",
        callback_data="buy_service_750",
        icon_custom_emoji_id="5325847485279652235"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="tg_views",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_views_auto_old_menu() -> InlineKeyboardMarkup:
    """Telegram Avto ko'rishlar eski post (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Avto ko'rishlar 5 post (Eski) - 166 so'm",
        callback_data="buy_service_63",
        icon_custom_emoji_id="5233246225146332642"
    ))
    builder.row(InlineKeyboardButton(
        text="Avto ko'rishlar 10 post (Eski) - 336 so'm",
        callback_data="buy_service_64",
        icon_custom_emoji_id="5233246225146332642"
    ))
    builder.row(InlineKeyboardButton(
        text="Avto ko'rishlar 20 post (Eski) - 668 so'm",
        callback_data="buy_service_65",
        icon_custom_emoji_id="5233246225146332642"
    ))
    builder.row(InlineKeyboardButton(
        text="Avto ko'rishlar 100 post (Eski) - 3 343 so'm",
        callback_data="buy_service_73",
        icon_custom_emoji_id="5233246225146332642"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="tg_views",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_views_auto_new_menu() -> InlineKeyboardMarkup:
    """Telegram Avto ko'rishlar yangi post (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Avto ko'rishlar 5 post (Yangi) - 2 174 so'm",
        callback_data="buy_service_714",
        icon_custom_emoji_id="5210956306952758910"
    ))
    builder.row(InlineKeyboardButton(
        text="Avto ko'rishlar 10 post (Yangi) - 4 347 so'm",
        callback_data="buy_service_715",
        icon_custom_emoji_id="5210956306952758910"
    ))
    builder.row(InlineKeyboardButton(
        text="Avto ko'rishlar 100 post (Yangi) - 38 641 so'm",
        callback_data="buy_service_719",
        icon_custom_emoji_id="5210956306952758910"
    ))
    builder.row(InlineKeyboardButton(
        text="Avto ko'rishlar 1000 post (Yangi) - 282 567 so'm",
        callback_data="buy_service_721",
        icon_custom_emoji_id="5210956306952758910"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="tg_views",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_premium_subs_menu() -> InlineKeyboardMarkup:
    """Telegram Premium Obunachi xizmatlari (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="TG Premium 7 kunlik (+10% Bonus🎁)",
        callback_data="buy_service_1973",
        icon_custom_emoji_id="6026011288641998567"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Premium 15 kunlik (+10% Bonus🎁)",
        callback_data="buy_service_1974",
        icon_custom_emoji_id="6026011288641998567"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Premium 30 kunlik (+200% Bonus🎁💥)",
        callback_data="buy_service_1976",
        icon_custom_emoji_id="6026011288641998567"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Premium 60 kunlik (+10% Bonus🎁)",
        callback_data="buy_service_2007",
        icon_custom_emoji_id="6026011288641998567"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Premium 30 kunlik (Kafolatli-tezkor)",
        callback_data="buy_service_1888",
        icon_custom_emoji_id="6026011288641998567"
    ))
    builder.row(InlineKeyboardButton(
        text="🇺🇿 TG premium 🧠Aqilli AI",
        callback_data="buy_service_1718",
        icon_custom_emoji_id="6026011288641998567"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="smm_telegram",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_bot_subs_menu() -> InlineKeyboardMarkup:
    """Telegram Bot uchun Obunachi xizmatlari (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="TG bot Obunachi + qidiruv orqali",
        callback_data="buy_service_1172",
        icon_custom_emoji_id="6030400221232501136"
    ))
    builder.row(InlineKeyboardButton(
        text="TG 🇷🇺[RUS] Bot Start + Statistika📊",
        callback_data="buy_service_1176",
        icon_custom_emoji_id="6030400221232501136"
    ))
    builder.row(InlineKeyboardButton(
        text="TG 🇺🇸[USA] Bot Start + Statistika📊",
        callback_data="buy_service_1177",
        icon_custom_emoji_id="6030400221232501136"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Premium 30 kunlik - Bot start 🤖",
        callback_data="buy_service_1292",
        icon_custom_emoji_id="6030400221232501136"
    ))
    builder.row(InlineKeyboardButton(
        text="🇺🇿 Bot Start (aqilli-Ai🧠) O'zbek",
        callback_data="buy_service_1673",
        icon_custom_emoji_id="6030400221232501136"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="smm_telegram",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_sub_fast_channel_menu() -> InlineKeyboardMarkup:
    """Telegram Tezkor kanal obunachisi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="30 kun kafolat tezkor (kanal)",
        callback_data="buy_service_1365",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="60 kun kafolat tezkor (kanal)",
        callback_data="buy_service_1366",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="90 kun kafolat tezkor (kanal)",
        callback_data="buy_service_1367",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="tg_subs",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_sub_online_reviews_menu() -> InlineKeyboardMarkup:
    """Telegram Online + sharxlar (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🇺🇿 Online + O'zbek sharxlar",
        callback_data="buy_service_1764",
        icon_custom_emoji_id="5224417984293938277"
    ))
    builder.row(InlineKeyboardButton(
        text="🇺🇲 Online + English sharxlar",
        callback_data="buy_service_1765",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="🇹🇷 Online + Turkey sharxlar",
        callback_data="buy_service_1766",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="tg_subs",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_sub_ai_menu() -> InlineKeyboardMarkup:
    """Telegram Aqilli AI Obunachi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="TG (aqlli Ai) 3 kunlik",
        callback_data="buy_service_1682",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG (aqlli Ai) 7 kunlik",
        callback_data="buy_service_1683",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG (aqlli Ai) 15 kunlik",
        callback_data="buy_service_1684",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG (aqlli Ai) 30 kunlik",
        callback_data="buy_service_1685",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="tg_subs",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_sub_real_menu() -> InlineKeyboardMarkup:
    """Telegram Haqiqiy Obunachi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 30 kunlik (haqiqiy)",
        callback_data="buy_service_1572",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 60 kunlik (haqiqiy)",
        callback_data="buy_service_1573",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 90 kunlik (haqiqiy)",
        callback_data="buy_service_1574",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 365 kunlik (haqiqiy)",
        callback_data="buy_service_1576",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="tg_subs",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_sub_active_menu() -> InlineKeyboardMarkup:
    """Telegram Jonli/Aktiv Obunachi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="TG 🇷🇺Rus Obunachi (jonli/aktiv)",
        callback_data="buy_service_10",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG 🇷🇺Rus Ayol Obunachi (jonli/aktiv)",
        callback_data="buy_service_11",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG 🇺🇦Ukraina Obunachi (jonli/aktiv)",
        callback_data="buy_service_14",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="tg_subs",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_sub_request_menu() -> InlineKeyboardMarkup:
    """Telegram Zayafka Obunachi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="TG Obunachi tezkor (zayafka)",
        callback_data="buy_service_810",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 60-kun kafolat (zayafka)",
        callback_data="buy_service_1370",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Obunachi 90-kun kafolat (zayafka)",
        callback_data="buy_service_1372",
        icon_custom_emoji_id="5438278356015528516"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="tg_subs",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_reactions_menu() -> InlineKeyboardMarkup:
    """Telegram Reaksiyalar menyusi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👍 Like", callback_data="buy_service_80"),
        InlineKeyboardButton(text="❤️ Yurak", callback_data="buy_service_83")
    )
    builder.row(
        InlineKeyboardButton(text="🔥 Olov", callback_data="buy_service_82"),
        InlineKeyboardButton(text="⚡ Chaqmoq", callback_data="buy_service_1056")
    )
    builder.row(InlineKeyboardButton(
        text="👍🤩🎉🔥🥰 Aralash ijobiy reaksiyalar",
        callback_data="buy_service_74"
    ))
    builder.row(InlineKeyboardButton(
        text="10 ta postga avto reaksiya",
        callback_data="buy_service_76"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="smm_telegram"
    ))
    return builder.as_markup()


def tg_comments_menu() -> InlineKeyboardMarkup:
    """Telegram Izohlar (coment) menyusi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="TG 🇷🇺 Rus Izohlari (coment)",
        callback_data="buy_service_191",
        icon_custom_emoji_id="5767258028956978383"
    ))
    builder.row(InlineKeyboardButton(
        text="TG 🇬🇧 Inglizcha izohlar (coment)",
        callback_data="buy_service_192",
        icon_custom_emoji_id="5767258028956978383"
    ))
    builder.row(InlineKeyboardButton(
        text="TG 🇸🇦 Arabcha izohlar (coment)",
        callback_data="buy_service_193",
        icon_custom_emoji_id="5767258028956978383"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="smm_telegram",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_uzbek_menu() -> InlineKeyboardMarkup:
    """O'zbek xizmatlar menyusi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Online Obunachi + o'zbek sharxlar",
        callback_data="buy_service_1764",
        icon_custom_emoji_id="5224417984293938277"
    ))
    builder.row(InlineKeyboardButton(
        text="TG premium obunachi 🧠Aqilli AI",
        callback_data="buy_service_1718",
        icon_custom_emoji_id="5224417984293938277"
    ))
    builder.row(InlineKeyboardButton(
        text="Bot Start (aqilli-Ai🧠) O'zbek",
        callback_data="buy_service_1673",
        icon_custom_emoji_id="5224417984293938277"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="smm_telegram",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_shares_menu() -> InlineKeyboardMarkup:
    """POST Ulashishlar menyusi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="TG post uchun ulashishlar",
        callback_data="buy_service_845",
        icon_custom_emoji_id="5852830669599674051"
    ))
    builder.row(InlineKeyboardButton(
        text="TG post uchun ulashishlar + Ko'rishlar",
        callback_data="buy_service_865",
        icon_custom_emoji_id="5852830669599674051"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Postni ulashish (Statistika + Ko'rishlar)",
        callback_data="buy_service_866",
        icon_custom_emoji_id="5852830669599674051"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="smm_telegram",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_boost_menu() -> InlineKeyboardMarkup:
    """Telegram BOOST menyusi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="TG Boost 1 kunlik (avto qayta tiklanish)",
        callback_data="buy_service_1780",
        icon_custom_emoji_id="5884428842780594914"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Boost 3 kunlik (avto qayta tiklanish)",
        callback_data="buy_service_2107",
        icon_custom_emoji_id="5884428842780594914"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Boost 7 kunlik (avto qayta tiklanish)",
        callback_data="buy_service_1781",
        icon_custom_emoji_id="5884428842780594914"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Boost 15 kunlik (avto qayta tiklanish)",
        callback_data="buy_service_1782",
        icon_custom_emoji_id="5884428842780594914"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Boost 30 kunlik (avto qayta tiklanish)",
        callback_data="buy_service_1783",
        icon_custom_emoji_id="5884428842780594914"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Boost 60 kunlik (avto qayta tiklanish)",
        callback_data="buy_service_2110",
        icon_custom_emoji_id="5884428842780594914"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Boost 365 kunlik (avto qayta tiklanish)",
        callback_data="buy_service_2115",
        icon_custom_emoji_id="5884428842780594914"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="smm_telegram",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_poll_menu() -> InlineKeyboardMarkup:
    """So'rovnomaga ovoz menyusi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="TG 🇺🇿 Sorovnoma uchun Ovoz (O'zbek)",
        callback_data="buy_service_176",
        icon_custom_emoji_id="5936143551854285132"
    ))
    builder.row(InlineKeyboardButton(
        text="TG 🇷🇺 Sorovnoma uchun Ovoz (Rus)",
        callback_data="buy_service_110",
        icon_custom_emoji_id="5936143551854285132"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="smm_telegram",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


def tg_story_menu() -> InlineKeyboardMarkup:
    """Telegram STORY menyusi (APIdan)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="TG Story ko'rishlar",
        callback_data="buy_service_1115",
        icon_custom_emoji_id="6028346797368283073"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Story Premium ko'rishlar",
        callback_data="buy_service_1241",
        icon_custom_emoji_id="6028346797368283073"
    ))
    builder.row(InlineKeyboardButton(
        text="STORY Ko'rishlar (🇺🇿 O'zbek)",
        callback_data="buy_service_2133",
        icon_custom_emoji_id="6028346797368283073"
    ))
    builder.row(InlineKeyboardButton(
        text="TG Story ❤️ Like (reaksiya)",
        callback_data="buy_service_1818",
        icon_custom_emoji_id="6028346797368283073"
    ))
    builder.row(InlineKeyboardButton(
        text="STORY yoqtirish (Like 🇺🇿 O'zbek)",
        callback_data="buy_service_2134",
        icon_custom_emoji_id="6028346797368283073"
    ))
    builder.row(InlineKeyboardButton(
        text="Orqaga",
        callback_data="smm_telegram",
        icon_custom_emoji_id="5416113713428057601"
    ))
    return builder.as_markup()


# ──────────────────────────────────────────
#  Instagram menyulari
# ──────────────────────────────────────────

def instagram_services_menu() -> InlineKeyboardMarkup:
    """Instagram asosiy xizmatlar menyusi"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Instagram Obunachi", callback_data="insta_followers", icon_custom_emoji_id="6032609071373226027"))
    builder.row(InlineKeyboardButton(text="Instagram Like", callback_data="insta_likes", icon_custom_emoji_id="5373005951311812951"))
    builder.row(InlineKeyboardButton(text="Ko'rishlar & Reels", callback_data="insta_views", icon_custom_emoji_id="5325847485279652235"))
    builder.row(InlineKeyboardButton(text="Story Ko'rish & Like", callback_data="insta_story", icon_custom_emoji_id="6028346797368283073"))
    builder.row(InlineKeyboardButton(text="Jonli Efir (Tomoshabinlar)", callback_data="insta_live", icon_custom_emoji_id="5884428842780594914"))
    builder.row(InlineKeyboardButton(text="Izohlar (Coment) & Repost", callback_data="insta_comments", icon_custom_emoji_id="5767258028956978383"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def insta_followers_menu() -> InlineKeyboardMarkup:
    """Instagram Obunachi tariflari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Obunachi 30 kunlik (0-4% kamayish)", callback_data="buy_service_1809"))
    builder.row(InlineKeyboardButton(text="Obunachi 60 kunlik (0-4% kamayish)", callback_data="buy_service_1810"))
    builder.row(InlineKeyboardButton(text="Obunachi 90 kunlik (0-4% kamayish)", callback_data="buy_service_1811"))
    builder.row(InlineKeyboardButton(text="Obunachi 365 kunlik (0-4% kamayish)", callback_data="buy_service_1812"))
    builder.row(InlineKeyboardButton(text="🇺🇿 O'zbek Obunachi (Strategik)", callback_data="buy_service_1662"))
    builder.row(InlineKeyboardButton(text="Kafolatli Obunachi 30 kun", callback_data="buy_service_1997"))
    builder.row(InlineKeyboardButton(text="Kafolatli Obunachi 60 kun", callback_data="buy_service_1998"))
    builder.row(InlineKeyboardButton(text="Kafolatli Obunachi 90 kun", callback_data="buy_service_1999"))
    builder.row(InlineKeyboardButton(text="Kafolatli Obunachi 365 kun", callback_data="buy_service_2000"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_instagram", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def insta_likes_menu() -> InlineKeyboardMarkup:
    """Instagram Like tariflari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Like 30 kunlik (0-5% kamayish)", callback_data="buy_service_590"))
    builder.row(InlineKeyboardButton(text="Like 60 kunlik (0-5% kamayish)", callback_data="buy_service_257"))
    builder.row(InlineKeyboardButton(text="Like 90 kunlik", callback_data="buy_service_249"))
    builder.row(InlineKeyboardButton(text="Like 365 kunlik", callback_data="buy_service_1080"))
    builder.row(InlineKeyboardButton(text="Kafolatli Like 30 kun", callback_data="buy_service_1589"))
    builder.row(InlineKeyboardButton(text="Kafolatli Like 60 kun", callback_data="buy_service_1590"))
    builder.row(InlineKeyboardButton(text="Kafolatli Like 90 kun", callback_data="buy_service_1591"))
    builder.row(InlineKeyboardButton(text="Kafolatli Like 365 kun", callback_data="buy_service_1592"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_instagram", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def insta_views_menu() -> InlineKeyboardMarkup:
    """Instagram Ko'rishlar tariflari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Reels Ko'rishlar (Arzon)", callback_data="buy_service_275"))
    builder.row(InlineKeyboardButton(text="Ko'rishlar (Super Tez)", callback_data="buy_service_278"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_instagram", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def insta_story_menu() -> InlineKeyboardMarkup:
    """Instagram Story xizmatlari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Istoriya Ko'rishlar", callback_data="buy_service_581"))
    builder.row(InlineKeyboardButton(text="Istoriya Like", callback_data="buy_service_1158"))
    builder.row(InlineKeyboardButton(text="Istoriya Doimiy Ko'rishlar", callback_data="buy_service_287"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_instagram", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def insta_live_menu() -> InlineKeyboardMarkup:
    """Instagram Jonli Efir tariflari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Jonli Efir 15 daqiqa", callback_data="buy_service_280"))
    builder.row(InlineKeyboardButton(text="Jonli Efir 30 daqiqa", callback_data="buy_service_1159"))
    builder.row(InlineKeyboardButton(text="Jonli Efir 60 daqiqa", callback_data="buy_service_1160"))
    builder.row(InlineKeyboardButton(text="Jonli Efir 90 daqiqa", callback_data="buy_service_1161"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_instagram", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def insta_comments_menu() -> InlineKeyboardMarkup:
    """Instagram Sharxlar & Repost"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Ijobiy Sharxlar 👍🔥😍", callback_data="buy_service_620"))
    builder.row(InlineKeyboardButton(text="Online Do'kon Sharxlari", callback_data="buy_service_306"))
    builder.row(InlineKeyboardButton(text="Sayohat Uchun Sharxlar", callback_data="buy_service_307"))
    builder.row(InlineKeyboardButton(text="Qizlar/Modellar Sharxlari", callback_data="buy_service_308"))
    builder.row(InlineKeyboardButton(text="Repost (30 kun kafolat) 🔄", callback_data="buy_service_1779"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_instagram", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


# ──────────────────────────────────────────
#  TikTok menyulari
# ──────────────────────────────────────────

def tiktok_services_menu() -> InlineKeyboardMarkup:
    """TikTok asosiy xizmatlar menyusi"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="TikTok Obunachi", callback_data="tt_followers", icon_custom_emoji_id="6032609071373226027"))
    builder.row(InlineKeyboardButton(text="TikTok Like", callback_data="tt_likes", icon_custom_emoji_id="5373005951311812951"))
    builder.row(InlineKeyboardButton(text="TikTok Ko'rishlar", callback_data="tt_views", icon_custom_emoji_id="5325847485279652235"))
    builder.row(InlineKeyboardButton(text="Jonli Efir & Coment", callback_data="tt_live", icon_custom_emoji_id="5884428842780594914"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def tt_followers_menu() -> InlineKeyboardMarkup:
    """TikTok Obunachi tariflari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Obunachi (7 kun kafolat)", callback_data="buy_service_1642"))
    builder.row(InlineKeyboardButton(text="Obunachi (15 kun kafolat)", callback_data="buy_service_1643"))
    builder.row(InlineKeyboardButton(text="Obunachi (30 kun kafolat)", callback_data="buy_service_1644"))
    builder.row(InlineKeyboardButton(text="Obunachi (60 kun kafolat)", callback_data="buy_service_1645"))
    builder.row(InlineKeyboardButton(text="Obunachi (90 kun kafolat)", callback_data="buy_service_1646"))
    builder.row(InlineKeyboardButton(text="Obunachi (365 kun kafolat)", callback_data="buy_service_1647"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_tiktok", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def tt_likes_menu() -> InlineKeyboardMarkup:
    """TikTok Like tariflari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Like (7 kun kafolat)", callback_data="buy_service_1554"))
    builder.row(InlineKeyboardButton(text="Like (15 kun kafolat)", callback_data="buy_service_1555"))
    builder.row(InlineKeyboardButton(text="Like (30 kun kafolat)", callback_data="buy_service_1550"))
    builder.row(InlineKeyboardButton(text="Like (60 kun kafolat)", callback_data="buy_service_1551"))
    builder.row(InlineKeyboardButton(text="Like (90 kun kafolat)", callback_data="buy_service_1552"))
    builder.row(InlineKeyboardButton(text="Like (365 kun kafolat)", callback_data="buy_service_1553"))
    builder.row(InlineKeyboardButton(text="Jonli Efir Uchun Like", callback_data="buy_service_1447"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_tiktok", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def tt_views_menu() -> InlineKeyboardMarkup:
    """TikTok Ko'rishlar tariflari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Ko'rishlar (30-60 kun kafolat)", callback_data="buy_service_611"))
    builder.row(InlineKeyboardButton(text="Post Uchun Ko'rishlar", callback_data="buy_service_749"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_tiktok", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def tt_live_menu() -> InlineKeyboardMarkup:
    """TikTok Jonli Efir tariflari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Jonli Efir 15 daqiqa", callback_data="buy_service_679"))
    builder.row(InlineKeyboardButton(text="Jonli Efir 30 daqiqa", callback_data="buy_service_1150"))
    builder.row(InlineKeyboardButton(text="Jonli Efir 60 daqiqa", callback_data="buy_service_1151"))
    builder.row(InlineKeyboardButton(text="Jonli Efir 90 daqiqa", callback_data="buy_service_1152"))
    builder.row(InlineKeyboardButton(text="Jonli Efir Coment 😍😁🥰", callback_data="buy_service_1308"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_tiktok", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


# ──────────────────────────────────────────
#  YouTube menyulari
# ──────────────────────────────────────────

def youtube_services_menu() -> InlineKeyboardMarkup:
    """YouTube asosiy xizmatlar menyusi"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="YouTube Obunachi", callback_data="yt_subs", icon_custom_emoji_id="6032609071373226027"))
    builder.row(InlineKeyboardButton(text="YouTube Like & Dislike", callback_data="yt_likes", icon_custom_emoji_id="5373005951311812951"))
    builder.row(InlineKeyboardButton(text="Ko'rishlar & Shorts", callback_data="yt_views", icon_custom_emoji_id="5325847485279652235"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def yt_subs_menu() -> InlineKeyboardMarkup:
    """YouTube Obunachi tariflari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Tezkor Obunachi", callback_data="buy_service_353"))
    builder.row(InlineKeyboardButton(text="Obunachi (Bot baza)", callback_data="buy_service_1076"))
    builder.row(InlineKeyboardButton(text="Obunachi (30 kun kafolat 0% kamayish)", callback_data="buy_service_1068"))
    builder.row(InlineKeyboardButton(text="Obunachi (60 kun kafolat 0% kamayish)", callback_data="buy_service_352"))
    builder.row(InlineKeyboardButton(text="Obunachi (90 kun kafolat 0% kamayish)", callback_data="buy_service_355"))
    builder.row(InlineKeyboardButton(text="Obunachi (180 kun kafolat 0% kamayish)", callback_data="buy_service_354"))
    builder.row(InlineKeyboardButton(text="Obunachi (365 kun kafolat 0% kamayish)", callback_data="buy_service_1344"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_youtube", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def yt_likes_menu() -> InlineKeyboardMarkup:
    """YouTube Like & Dislike tariflari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Like (30 kun kafolat)", callback_data="buy_service_344"))
    builder.row(InlineKeyboardButton(text="Like (60 kun kafolat)", callback_data="buy_service_1453"))
    builder.row(InlineKeyboardButton(text="Like (90 kun kafolat)", callback_data="buy_service_1454"))
    builder.row(InlineKeyboardButton(text="Like (365 kun kafolat)", callback_data="buy_service_1498"))
    builder.row(InlineKeyboardButton(text="Dislike Xizmati 👎", callback_data="buy_service_349"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_youtube", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


def yt_views_menu() -> InlineKeyboardMarkup:
    """YouTube Ko'rishlar & Shorts tariflari"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Ko'rishlar (30 kun)", callback_data="buy_service_1234"))
    builder.row(InlineKeyboardButton(text="Shorts Ko'rishlar (+2% Like)", callback_data="buy_service_362"))
    builder.row(InlineKeyboardButton(text="Ko'rishlar 365 kunlik", callback_data="buy_service_360"))
    builder.row(InlineKeyboardButton(text="Orqaga", callback_data="smm_youtube", icon_custom_emoji_id="5416113713428057601"))
    return builder.as_markup()


# ──────────────────────────────────────────
#  Virtual Nomer (SMS) klaviaturalari
# ──────────────────────────────────────────

def number_servers_menu() -> InlineKeyboardMarkup:
    """Nomer olish serverlarini tanlash"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Server 1 (Tezkor va Barqaror)",
            callback_data="num_srv_1",
            icon_custom_emoji_id="5456432998092133477"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Server 2 (Keng davlatlar tanlovi)",
            callback_data="num_srv_2",
            icon_custom_emoji_id="5447410659077661506"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Orqaga",
            callback_data="back_to_main",
            icon_custom_emoji_id="5416113713428057601"
        )
    )
    return builder.as_markup()


def number_countries_keyboard(server: int, countries: dict, page: int = 1, per_page: int = 8, sort_by_price: bool = False) -> InlineKeyboardMarkup:
    """Server bo'yicha davlatlarni sahifalab chiqarish (standart yoki arzon narxlar bo'yicha)"""
    builder = InlineKeyboardBuilder()
    from number_api import get_country_display, format_country_button_text

    items = list(countries.items())

    if sort_by_price:
        def price_sort_key(item):
            try:
                return (float(item[1].get("price", 999999)), item[0])
            except (ValueError, TypeError):
                return (999999, item[0])
        sorted_items = sorted(items, key=price_sort_key)
    else:
        priority = ["UZ", "RU", "KZ", "KG", "TJ", "US", "GB", "TR"]
        def sort_key(item):
            code = item[0].upper()
            if code in priority:
                return (0, priority.index(code))
            return (1, code)
        sorted_items = sorted(items, key=sort_key)

    total_pages = max(1, (len(sorted_items) + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page
    page_items = sorted_items[start:end]

    from_tag = ":cheap" if sort_by_price else ""
    for code, info in page_items:
        flag, name = get_country_display(code)
        price = float(info.get("price", 0))
        btn_text = format_country_button_text(flag, name, price)
        builder.row(
            InlineKeyboardButton(
                text=btn_text,
                callback_data=f"num_buy:{server}:{code}{from_tag}"
            )
        )

    # Navigatsiya
    nav_prefix = f"num_cheap:{server}" if sort_by_price else f"num_p:{server}"
    nav_row = []
    if page > 1:
        nav_row.append(
            InlineKeyboardButton(
                text="Oldingi", 
                callback_data=f"{nav_prefix}:{page-1}",
                icon_custom_emoji_id="5416113713428057601"
                )
        )
    nav_row.append(
        InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop")
    )
    if page < total_pages:
        nav_row.append(
            InlineKeyboardButton(
                text="Keyingi", 
                callback_data=f"{nav_prefix}:{page+1}",
                icon_custom_emoji_id="5415758949129404605"
                )
        )
    if nav_row:
        builder.row(*nav_row)

    # Rejimni almashtirish tugmasi (pastda ham qulaylik uchun)
    if sort_by_price:
        builder.row(
            InlineKeyboardButton(
                text="Barcha davlatlar",
                callback_data=f"num_srv_{server}",
                icon_custom_emoji_id="5201989772448381592"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="Arzon nomerlar",
                callback_data=f"num_cheap:{server}:1",
                icon_custom_emoji_id="6032678155922181525"
            )
        )

    builder.row(
        InlineKeyboardButton(
            text="Serverni almashtirish",
            callback_data="number",
            icon_custom_emoji_id="5416113713428057601"
        )
    )
    return builder.as_markup()


def number_confirm_keyboard(server: int, country: str, from_cheap: bool = False) -> InlineKeyboardMarkup:
    """Raqam sotib olishni tasdiqlash"""
    cancel_cb = f"num_cheap:{server}:1" if from_cheap else f"num_srv_{server}"
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Sotib olish",
            callback_data=f"num_do_buy:{server}:{country}",
            icon_custom_emoji_id="5456432998092133477"
        ),
        InlineKeyboardButton(
            text="Bekor qilish",
            callback_data=cancel_cb,
            icon_custom_emoji_id="6032903688949862892"
        )
    )
    return builder.as_markup()


def active_number_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Faol raqam tugmalari"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="SMS kodni olish",
            callback_data=f"num_sms:{order_id}",
            icon_custom_emoji_id="5954224165874569584"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Qayta tekshirish",
            callback_data=f"num_sms:{order_id}",
            icon_custom_emoji_id="5346269127059196142"
        ),
        InlineKeyboardButton(
            text="Asosiy menyu",
            callback_data="back_to_main",
            icon_custom_emoji_id="5416113713428057601"
        )
    )
    return builder.as_markup()


# ──────────────────────────────────────────
#  Telegram Stars klaviaturalari
# ──────────────────────────────────────────

def stars_menu(star_price: float = 260.0) -> InlineKeyboardMarkup:
    """Telegram Stars tariflari menyusi (2 tadan qatorda)"""
    builder = InlineKeyboardBuilder()
    
    packages = [
        (50, int(50 * star_price)),
        (100, int(100 * star_price)),
        (150, int(150 * star_price)),
        (250, int(250 * star_price)),
        (350, int(350 * star_price)),
        (500, int(500 * star_price)),
        (750, int(750 * star_price)),
        (1000, int(1000 * star_price)),
        (1500, int(1500 * star_price)),
        (2500, int(2500 * star_price)),
        (5000, int(5000 * star_price)),
        (10000, int(10000 * star_price)),
    ]

    for i in range(0, len(packages), 2):
        row_buttons = []
        for amount, price in packages[i:i+2]:
            row_buttons.append(
                InlineKeyboardButton(
                    text=f"{amount:,} — {price:,} so'm",
                    callback_data=f"stars_buy:{amount}",
                    icon_custom_emoji_id="5897792062291449826"
                )
            )
        builder.row(*row_buttons)

    builder.row(
        InlineKeyboardButton(
            text="Boshqa miqdor kiritish",
            callback_data="stars_custom",
            icon_custom_emoji_id="5447410659077661506"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Asosiy menyu",
            callback_data="back_to_main",
            icon_custom_emoji_id="5416113713428057601"
        )
    )
    return builder.as_markup()


def stars_confirm_keyboard() -> InlineKeyboardMarkup:
    """Stars buyurtmasini tasdiqlash tugmalari"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Tasdiqlash",
            callback_data="stars_confirm",
            icon_custom_emoji_id="5456432998092133477"
        ),
        InlineKeyboardButton(
            text="Bekor qilish",
            callback_data="stars_cancel",
            icon_custom_emoji_id="6032903688949862892"
        )
    )
    return builder.as_markup()



import logging
from aiogram import types, Router, F, Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMINS, CARD_NUMBER, CARD_HOLDER, ADMIN_USERNAME, STAR_PRICE_UZS
from database import (
    add_user, get_user_balance, add_user_balance, create_pending_deposit,
    add_order_record, update_order_status, get_user_orders, get_order_by_id,
    add_virtual_number, get_virtual_number_by_id, update_virtual_number_sms, get_user_virtual_numbers,
    get_user_orders_count, get_user_unified_orders,
    get_star_price
)
from smm_api import smm_api
from number_api import number_api, get_country_display
from keyboards import (
    my_inline_menu, 
    smm_social_menu, 
    telegram_services_menu, 
    telegram_subscribers_menu,
    tg_sub_cheap_menu,
    service_detail_keyboard,
    confirm_order_keyboard,
    telegram_views_menu,
    tg_views_prasmotr_menu,
    tg_views_auto_old_menu,
    tg_views_auto_new_menu,
    tg_premium_subs_menu,
    tg_bot_subs_menu,
    tg_sub_fast_channel_menu,
    tg_sub_online_reviews_menu,
    tg_sub_ai_menu,
    tg_sub_real_menu,
    tg_sub_active_menu,
    tg_sub_request_menu,
    tg_reactions_menu,
    tg_comments_menu,
    tg_uzbek_menu,
    tg_shares_menu,
    tg_boost_menu,
    tg_poll_menu,
    tg_story_menu,
    instagram_services_menu,
    insta_followers_menu,
    insta_likes_menu,
    insta_views_menu,
    insta_story_menu,
    insta_live_menu,
    insta_comments_menu,
    tiktok_services_menu,
    tt_followers_menu,
    tt_likes_menu,
    tt_views_menu,
    tt_live_menu,
    youtube_services_menu,
    yt_subs_menu,
    yt_likes_menu,
    yt_views_menu,
    number_servers_menu,
    number_countries_keyboard,
    number_confirm_keyboard,
    active_number_keyboard,
    stars_menu,
    stars_confirm_keyboard,
    subscription_required_kb,
    user_orders_keyboard,
    user_empty_orders_keyboard
)
from middlewares import check_user_subscription

logger = logging.getLogger(__name__)
router = Router()


# ──────────────────────────────────────────
#  FSM Holatlari
# ──────────────────────────────────────────
class OrderFlow(StatesGroup):
    waiting_for_link = State()
    waiting_for_quantity = State()

class DepositFlow(StatesGroup):
    waiting_for_amount = State()

class StarsOrderFlow(StatesGroup):
    waiting_for_custom_amount = State()
    waiting_for_username = State()

# Telegram tariflari uchun GrandSMM API service ID xaritasi
TG_SUB_ID_MAP = {
    "buy_tg_1d": 2123,
    "buy_tg_7d": 2124,
    "buy_tg_14d": 2125,
    "buy_tg_30d": 2126,
    "buy_tg_60d": 2127,
    "buy_tg_90d": 2128,
    "buy_tg_180d": 2129,
    "buy_tg_365d": 2130,
    "buy_tg_lifetime": 2131,
    "buy_tg_rus30d": 837,
}


# ──────────────────────────────────────────
#  /start buyrug'i (Inline menyu bilan)
# ──────────────────────────────────────────
@router.message(Command("start"))
async def cmd_start(message: types.Message, bot: Bot):
    user = message.from_user
    add_user(user.id, user.username, user.full_name)

    # Xabar matnida bir nechta premium emojilar:
    text = (
        f'<tg-emoji emoji-id="6006107551198874621">👋</tg-emoji> Salom, <b>{user.full_name}</b>!\n\n'
        f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <b>SMM Botimizga xush kelibsiz!</b>\n\n'
        f'<tg-emoji emoji-id="5231102735817918643">⚡️</tg-emoji> Quyidagi xizmatlardan birini tanlang:'
    )

    await message.answer(
        text=text,
        reply_markup=my_inline_menu(is_admin=(user.id in ADMINS)),
        parse_mode="HTML"
    )


# ──────────────────────────────────────────
#  Majburiy Obuna tekshirish tugmasi
# ──────────────────────────────────────────
@router.callback_query(F.data == "check_subscription")
async def cb_check_subscription(callback: types.CallbackQuery, bot: Bot):
    user = callback.from_user
    is_sub, unsub = await check_user_subscription(bot, user.id)

    if is_sub:
        await callback.answer("✅ Obunangiz muvaffaqiyatli tasdiqlandi! Xush kelibsiz.", show_alert=True)
        text = (
            f'<tg-emoji emoji-id="6006107551198874621">👋</tg-emoji> Salom, <b>{user.full_name}</b>!\n\n'
            f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <b>SMM Botimizga xush kelibsiz!</b>\n\n'
            f'<tg-emoji emoji-id="5231102735817918643">⚡️</tg-emoji> Quyidagi xizmatlardan birini tanlang:'
        )
        try:
            await callback.message.edit_text(
                text=text,
                reply_markup=my_inline_menu(is_admin=(user.id in ADMINS)),
                parse_mode="HTML"
            )
        except Exception:
            await callback.message.answer(
                text=text,
                reply_markup=my_inline_menu(is_admin=(user.id in ADMINS)),
                parse_mode="HTML"
            )
    else:
        await callback.answer("❌ Siz hali barcha homiy kanallarga a'zo bo'lmadingiz!", show_alert=True)
        text = (
            f'<tg-emoji emoji-id="6025976301838405549">⚠️</tg-emoji> <b>Botdan foydalanish uchun homiy kanallarga obuna bo\'ling!</b>\n\n'
            f'Quyidagi qolgan kanallarga a\'zo bo\'ling va yana <b>"✅ Obunani tekshirish"</b> tugmasini bosing:'
        )
        try:
            await callback.message.edit_text(
                text=text,
                reply_markup=subscription_required_kb(unsub),
                parse_mode="HTML"
            )
        except Exception:
            pass


# ──────────────────────────────────────────
#  Inline tugmalar bosilgandagi javoblar
# ──────────────────────────────────────────
@router.callback_query(F.data == "smm")
async def callback_smm(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "👇 <b>Quyidagi ijtimoiy tarmoqlardan birini tanlang:</b>",
        reply_markup=smm_social_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "smm_telegram")
async def callback_smm_telegram(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "👇 <b>Telegram xizmatlaridan birini tanlang:</b>",
        reply_markup=telegram_services_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_subs")
async def callback_tg_subs(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "👇 <b>Telegram obunachi xizmat turini tanlang:</b>",
        reply_markup=telegram_subscribers_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_views")
async def callback_tg_views(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Telegram Ko'rishlar]</b> bo'limidan kerakli ro'yxatni tanlang!",
        reply_markup=telegram_views_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_views_prasmotr")
async def callback_tg_views_prasmotr(callback: types.CallbackQuery):
    await callback.answer()
    await smm_api.get_services()
    await callback.message.edit_text(
        "<b>[Telegram ko'rishlar (prasmotr)]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=tg_views_prasmotr_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_views_auto_old")
async def callback_tg_views_auto_old(callback: types.CallbackQuery):
    await callback.answer()
    await smm_api.get_services()
    await callback.message.edit_text(
        "<b>[Telegram Avto ko'rishlar (eski post)]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=tg_views_auto_old_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_views_auto_new")
async def callback_tg_views_auto_new(callback: types.CallbackQuery):
    await callback.answer()
    await smm_api.get_services()
    await callback.message.edit_text(
        "<b>[Telegram avto ko'rishlar (yangi post)]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=tg_views_auto_new_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_sub_cheap")
async def callback_tg_sub_cheap(callback: types.CallbackQuery):
    await callback.answer()
    await smm_api.get_services()
    await callback.message.edit_text(
        "👇 <b>Kerakli tarifni tanlang:</b>",
        reply_markup=tg_sub_cheap_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_premium_subs")
async def callback_tg_premium_subs(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Telegram Premium Obunachi]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=tg_premium_subs_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_bot_subs")
async def callback_tg_bot_subs(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Bot uchun Obunachi]</b> bo'limidan kerakli xizmatni tanlang:",
        reply_markup=tg_bot_subs_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.in_(["tg_sub_fast_guaranteed", "tg_sub_fast_channel"]))
async def callback_tg_sub_fast_channel(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Obunachi tezkor (kanal uchun)]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=tg_sub_fast_channel_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_sub_online_reviews")
async def callback_tg_sub_online_reviews(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Obunachi (Online + sharx)]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=tg_sub_online_reviews_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_sub_ai")
async def callback_tg_sub_ai(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Obunachi (Aqilli-Ai)]</b> bo'limidan kerakli muddatni tanlang:",
        reply_markup=tg_sub_ai_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_sub_real")
async def callback_tg_sub_real(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Obunachi (haqiqiy account)]</b> bo'limidan kerakli muddatni tanlang:",
        reply_markup=tg_sub_real_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_sub_active")
async def callback_tg_sub_active(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Obunachi (jonli/aktiv)]</b> bo'limidan kerakli xizmatni tanlang:",
        reply_markup=tg_sub_active_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_sub_request")
async def callback_tg_sub_request(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Obunachi (zayafka)]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=tg_sub_request_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_reactions")
async def callback_tg_reactions(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Telegram Reaksiyalar]</b> bo'limidan kerakli reaksiyani tanlang:",
        reply_markup=tg_reactions_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_comments")
async def callback_tg_comments(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Telegram Izohlar (coment)]</b> bo'limidan kerakli tilni tanlang:",
        reply_markup=tg_comments_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_uzbek")
async def callback_tg_uzbek(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[O'zbek xizmatlar]</b> bo'limidan kerakli xizmatni tanlang:",
        reply_markup=tg_uzbek_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_shares")
async def callback_tg_shares(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[POST Ulashishlar]</b> bo'limidan kerakli xizmatni tanlang:",
        reply_markup=tg_shares_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_boost")
async def callback_tg_boost(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Telegram BOOST]</b> bo'limidan kerakli muddatni tanlang:",
        reply_markup=tg_boost_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_poll")
async def callback_tg_poll(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[So'rovnomaga ovoz]</b> bo'limidan kerakli xizmatni tanlang:",
        reply_markup=tg_poll_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tg_story")
async def callback_tg_story(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Telegram STORY]</b> bo'limidan kerakli xizmatni tanlang:",
        reply_markup=tg_story_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("buy_"))
async def callback_show_service_detail(callback: types.CallbackQuery):
    await callback.answer()
    cb_data = callback.data
    if cb_data in TG_SUB_ID_MAP:
        service_id = TG_SUB_ID_MAP[cb_data]
        back_cb = "tg_sub_cheap"
    elif cb_data.startswith("buy_service_"):
        service_id = int(cb_data.replace("buy_service_", ""))
        # Telegram
        if service_id in [740, 750]:
            back_cb = "tg_views_prasmotr"
        elif service_id in [63, 64, 65, 73]:
            back_cb = "tg_views_auto_old"
        elif service_id in [714, 715, 719, 721]:
            back_cb = "tg_views_auto_new"
        elif service_id in [1973, 1974, 1976, 2007, 1888, 1718]:
            back_cb = "tg_premium_subs"
        elif service_id in [1172, 1176, 1177, 1292, 1673]:
            back_cb = "tg_bot_subs"
        elif service_id in [1365, 1366, 1367]:
            back_cb = "tg_sub_fast_channel"
        elif service_id in [1764, 1765, 1766]:
            back_cb = "tg_sub_online_reviews"
        elif service_id in [1682, 1683, 1684, 1685]:
            back_cb = "tg_sub_ai"
        elif service_id in [1572, 1573, 1574, 1576]:
            back_cb = "tg_sub_real"
        elif service_id in [10, 11, 14]:
            back_cb = "tg_sub_active"
        elif service_id in [810, 1370, 1372]:
            back_cb = "tg_sub_request"
        elif service_id in [80, 83, 82, 1056, 74, 76]:
            back_cb = "tg_reactions"
        elif service_id in [191, 192, 193]:
            back_cb = "tg_comments"
        elif service_id in [845, 865, 866]:
            back_cb = "tg_shares"
        elif service_id in [1780, 2107, 1781, 1782, 1783, 2110, 2115]:
            back_cb = "tg_boost"
        elif service_id in [176, 110]:
            back_cb = "tg_poll"
        elif service_id in [1115, 1241, 2133, 1818, 2134]:
            back_cb = "tg_story"
        # Instagram
        elif service_id in [1809, 1810, 1811, 1812, 1662, 1997, 1998, 1999, 2000]:
            back_cb = "insta_followers"
        elif service_id in [590, 257, 249, 1080, 1589, 1590, 1591, 1592]:
            back_cb = "insta_likes"
        elif service_id in [275, 278]:
            back_cb = "insta_views"
        elif service_id in [581, 1158, 287]:
            back_cb = "insta_story"
        elif service_id in [280, 1159, 1160, 1161]:
            back_cb = "insta_live"
        elif service_id in [620, 306, 307, 308, 1779]:
            back_cb = "insta_comments"
        # TikTok
        elif service_id in [1642, 1643, 1644, 1645, 1646, 1647]:
            back_cb = "tt_followers"
        elif service_id in [1554, 1555, 1550, 1551, 1552, 1553, 1447]:
            back_cb = "tt_likes"
        elif service_id in [611, 749]:
            back_cb = "tt_views"
        elif service_id in [679, 1150, 1151, 1152, 1308]:
            back_cb = "tt_live"
        # YouTube
        elif service_id in [353, 1076, 1068, 352, 355, 354, 1344]:
            back_cb = "yt_subs"
        elif service_id in [344, 1453, 1454, 1498, 349]:
            back_cb = "yt_likes"
        elif service_id in [1234, 362, 360]:
            back_cb = "yt_views"
        else:
            back_cb = "smm"
    else:
        service_id = 2123
        back_cb = "smm"

    # GrandSMM API dan dinamik jonli ma'lumotlarni olamiz
    service = await smm_api.get_service_by_id(service_id)
    if not service:
        await callback.message.answer("⚠️ Ushbu xizmat haqida ma'lumot yuklanmadi. Qaytadan urinib ko'ring.")
        return

    desc = service.get("description", "")
    desc = desc.replace("<", "&lt;").replace(">", "&gt;")
    desc = desc.replace("⚠️", '<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji>')

    try:
        formatted_rate = f"{int(float(service['rate'])):,}".replace(",", " ")
    except Exception:
        formatted_rate = str(service["rate"])

    text = (
        f'<tg-emoji emoji-id="5373052667671093676">🛍️</tg-emoji> <b>{service["name"]}</b>\n\n'
        f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>ID:</b> <code>{service["service"]}</code>\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Narx:</b> 1000 ta uchun - <b>{formatted_rate} so\'m</b>\n'
        f'<tg-emoji emoji-id="5447410659077661506">🌐</tg-emoji> <b>Min/Max:</b> {service["min"]} - {service["max"]}\n\n'
        f'<blockquote>{desc}</blockquote>\n\n'
        f'<tg-emoji emoji-id="5231102735817918643">👇</tg-emoji> <b>Buyurtma berish tugmasini bosing!</b>'
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=service_detail_keyboard(service["service"], back_callback=back_cb),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("order_"))
async def callback_start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    raw_id = callback.data.replace("order_", "")
    service_id = TG_SUB_ID_MAP.get(raw_id, int(raw_id) if raw_id.isdigit() else 2123)
    service = await smm_api.get_service_by_id(service_id)
    if not service:
        await callback.message.answer("⚠️ Xizmat ma'lumotlari yuklanmadi. Qaytadan urinib ko'ring.")
        return

    clean_price = float(service["rate"])
    min_amount = int(service["min"])
    max_amount = int(service["max"])

    await state.update_data(
        service_id=int(service["service"]),
        service_title=service["name"],
        price_per_k=clean_price,
        min_amount=min_amount,
        max_amount=max_amount
    )
    await state.set_state(OrderFlow.waiting_for_link)

    await callback.message.answer(
        f'<tg-emoji emoji-id="5269381442864963988">📝</tg-emoji> <b>{service["name"]}</b>\n\n'
        ' <tg-emoji emoji-id="5201989772448381592">🔗</tg-emoji> Kanal, guruh yoki post havolasini yuboring:\n'
        "<i>Misol: @kanal_nomi yoki https://t.me/kanal_nomi</i>\n\n"
        '<tg-emoji emoji-id="6032903688949862892">❌</tg-emoji> Bekor qilish uchun: /cancel',
        parse_mode="HTML"
    )


@router.message(OrderFlow.waiting_for_link)
async def process_order_link(message: types.Message, state: FSMContext):
    link = message.text.strip()
    if not (link.startswith("@") or link.startswith("https://") or link.startswith("http://") or link.startswith("t.me/")):
        await message.answer(
            '<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Iltimos, to\'g\'ri havola kiriting!\n'
            "Misol: <code>@username</code> yoki <code>https://t.me/kanal</code>"
        )
        return

    await state.update_data(link=link)
    data = await state.get_data()
    await state.set_state(OrderFlow.waiting_for_quantity)

    await message.answer(
        f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji> <b>Nechta obunachi buyurtma bermoqchisiz?</b>\n\n'
        f"• Minimal miqdor: <b>{data['min_amount']}</b> ta\n"
        f"• Maksimal miqdor: <b>{data['max_amount']}</b> ta\n\n"
        f"<i>Iltimos, faqat raqam kiriting (masalan: 1000):</i>",
        parse_mode="HTML"
    )


@router.message(OrderFlow.waiting_for_quantity)
async def process_order_quantity(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer('<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Iltimos, faqat musbat raqam kiriting (masalan: 1000)!')
        return

    qty = int(text)
    data = await state.get_data()

    if qty < data["min_amount"] or qty > data["max_amount"]:
        await message.answer(
            f'<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Miqdor chegaradan tashqarida!\n'
            f"Minimal: <b>{data['min_amount']}</b> ta, Maksimal: <b>{data['max_amount']}</b> ta bo'lishi kerak."
        )
        return

    total_price = int((qty * data["price_per_k"]) / 1000)
    await state.update_data(quantity=qty, total_price=total_price)

    await message.answer(
        f'<tg-emoji emoji-id="5269381442864963988">📋</tg-emoji> <b>Buyurtma ma\'lumotlari:</b>\n\n'
        f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>Xizmat:</b> <b>{data['service_title']}</b>\n'
        f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Xizmat ID:</b> <code>{data['service_id']}</code>\n'
        f'<tg-emoji emoji-id="5201989772448381592">🔗</tg-emoji> <b>Havola:</b> <code>{data['link']}</code>\n'
        f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji> <b>Miqdor:</b> <b>{qty:,} ta</b>\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Jami to\'lov:</b> <b>{total_price:,} so\'m</b>\n\n'
        f'<b>Buyurtmani tasdiqlaysizmi?</b>',
        reply_markup=confirm_order_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "confirm_order")
async def callback_confirm_order(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data or "service_id" not in data:
        await callback.answer('<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Buyurtma ma\'lumotlari eskirgan. Qaytadan urinib ko\'ring.', show_alert=True)
        return

    user_id = callback.from_user.id
    total_price = data.get("total_price", 0)
    current_balance = get_user_balance(user_id)

    # Foydalanuvchi balansini tekshiramiz
    if current_balance < total_price:
        await state.clear()
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(
                text="Hisobni to'ldirish",
                callback_data="hisob_to'ldirish",
                icon_custom_emoji_id="6025976946083500432"
            )
        )
        keyboard.row(
            InlineKeyboardButton(
                text="« Asosiy menyu",
                callback_data="back_to_main",
                icon_custom_emoji_id="5416113713428057601"
            )
        )
        await callback.message.edit_text(
            f'<tg-emoji emoji-id="6032903688949862892">❌</tg-emoji> <b>Xizmat bekor qilindi (Mablag\' yetarli emas)</b>\n\n'
            f'<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <b>Balansingizda mablag\' yetarli emas!</b>\n\n'
            f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> Kerakli summa: <b>{total_price:,} so\'m</b>\n'
            f'<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> Sizning balansingiz: <b>{current_balance:,.0f} so\'m</b>\n\n'
            f'<i>Buyurtma berish uchun avval hisobingizni to\'ldiring 👇</i>',
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )
        return

    await state.clear()
    status_msg = await callback.message.edit_text('<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> Buyurtma GrandSMM serveriga yuborilmoqda...')

    # Balansdan mablag'ni yechamiz
    add_user_balance(user_id, -total_price)

    # GrandSMM REST API v2 ga so'rov yuborish (action=add)
    resp = await smm_api.add_order(
        service_id=data["service_id"],
        link=data["link"],
        quantity=data["quantity"]
    )

    if "order" in resp:
        order_id = resp["order"]
        rem_balance = get_user_balance(user_id)

        # Bazaga buyurtmani saqlaymiz (Avtomatik kuzatuv va xabarnoma uchun)
        add_order_record(
            order_id=int(order_id),
            user_id=user_id,
            service_id=data["service_id"],
            service_title=data.get("service_title", "Xizmat"),
            quantity=data["quantity"],
            price=total_price,
            link=data.get("link", "")
        )

        # Kanalga xabar yuboramiz
        try:
            from order_checker import send_order_to_channel
            await send_order_to_channel(callback.bot, "smm", {
                "order_id": order_id,
                "user_id": user_id,
                "user_name": callback.from_user.full_name,
                "username": callback.from_user.username,
                "service_title": data.get("service_title", "Xizmat"),
                "quantity": data["quantity"],
                "price": total_price,
                "link": data.get("link", "")
            })
        except Exception:
            pass


        await status_msg.edit_text(
            f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji><b>Buyurtmangiz muvaffaqiyatli qabul qilindi!</b>\n\n'
            f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji><b>Buyurtma ID:</b> <code>{order_id}</code>\n'
            f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji><b>Xizmat:</b> <b>{data["service_title"]}</b>\n'
            f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji><b>Miqdor:</b> <b>{data["quantity"]} ta</b>\n'
            f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji><b>To\'lov:</b> <b>{data["total_price"]:,} so\'m</b>\n'
            f'<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji><b>Qolgan balansingiz:</b> <b>{rem_balance:,.0f} so\'m</b>\n\n'
            f'<tg-emoji emoji-id="5936143551854285132">📊</tg-emoji><b>Holatni tekshirish:</b> <code>/status {order_id}</code>\n\n'
            f'<i>Buyurtmangiz bajarilishi bilan bot sizga avtomatik xabar beradi!</i>',
            parse_mode="HTML"
        )
    else:
        # Xatolik bo'lsa pulni balansga qaytaramiz
        add_user_balance(user_id, total_price)
        error_msg = resp.get("error", "Noma'lum xatolik yuz berdi")
        await status_msg.edit_text(
            f'<tg-emoji emoji-id="6028346797368283073">❌</tg-emoji><b>Buyurtma amalga oshmadi:</b>\n\n'
            f"Sabab: <i>{error_msg}</i>\n\n"
            f'<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji>Mablag\' balansingizga qaytarildi.',
            parse_mode="HTML"
        )




@router.callback_query(F.data == "back_to_main")
async def callback_back(callback: types.CallbackQuery):
    await callback.answer()
    user = callback.from_user
    text = (
        f'<tg-emoji emoji-id="6006107551198874621">👋</tg-emoji> Salom, <b>{user.full_name}</b>!\n\n'
        f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <b>SMM Botimizga xush kelibsiz!</b>\n\n'
        f'<tg-emoji emoji-id="5231102735817918643">⚡️</tg-emoji> Quyidagi xizmatlardan birini tanlang:'
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=my_inline_menu(is_admin=(user.id in ADMINS)),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("tg_"))
async def callback_tg_subservice(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        '<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> <b>Tanlangan xizmat bo\'yicha tez orada buyurtma qabul qilinadi!</b>',
        parse_mode="HTML"
    )


# ──────────────────────────────────────────
#  Instagram Handlerlari
# ──────────────────────────────────────────
@router.callback_query(F.data == "smm_instagram")
async def callback_smm_instagram(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        '<tg-emoji emoji-id="5231102735817918643">⚡</tg-emoji> <b>Instagram xizmatlaridan birini tanlang:</b>',
        reply_markup=instagram_services_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "insta_followers")
async def callback_insta_followers(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Instagram Obunachi]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=insta_followers_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "insta_likes")
async def callback_insta_likes(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Instagram Like]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=insta_likes_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "insta_views")
async def callback_insta_views(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Instagram Ko'rishlar & Reels]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=insta_views_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "insta_story")
async def callback_insta_story(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Instagram Story]</b> bo'limidan kerakli xizmatni tanlang:",
        reply_markup=insta_story_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "insta_live")
async def callback_insta_live(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Instagram Jonli Efir]</b> bo'limidan kerakli xizmatni tanlang:",
        reply_markup=insta_live_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "insta_comments")
async def callback_insta_comments(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[Instagram Izohlar & Repost]</b> bo'limidan kerakli xizmatni tanlang:",
        reply_markup=insta_comments_menu(),
        parse_mode="HTML"
    )


# ──────────────────────────────────────────
#  TikTok Handlerlari
# ──────────────────────────────────────────
@router.callback_query(F.data == "smm_tiktok")
async def callback_smm_tiktok(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        '<tg-emoji emoji-id="5231102735817918643">⚡</tg-emoji> <b>TikTok xizmatlaridan birini tanlang:</b>',
        reply_markup=tiktok_services_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tt_followers")
async def callback_tt_followers(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[TikTok Obunachi]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=tt_followers_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tt_likes")
async def callback_tt_likes(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[TikTok Like]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=tt_likes_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tt_views")
async def callback_tt_views(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[TikTok Ko'rishlar]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=tt_views_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "tt_live")
async def callback_tt_live(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[TikTok Jonli Efir & Izohlar]</b> bo'limidan kerakli xizmatni tanlang:",
        reply_markup=tt_live_menu(),
        parse_mode="HTML"
    )


# ──────────────────────────────────────────
#  YouTube Handlerlari
# ──────────────────────────────────────────
@router.callback_query(F.data == "smm_youtube")
async def callback_smm_youtube(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        '<tg-emoji emoji-id="5231102735817918643">⚡</tg-emoji> <b>YouTube xizmatlaridan birini tanlang:</b>',
        reply_markup=youtube_services_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "yt_subs")
async def callback_yt_subs(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[YouTube Obunachi]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=yt_subs_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "yt_likes")
async def callback_yt_likes(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[YouTube Like & Dislike]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=yt_likes_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "yt_views")
async def callback_yt_views(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>[YouTube Ko'rishlar & Shorts]</b> bo'limidan kerakli tarifni tanlang:",
        reply_markup=yt_views_menu(),
        parse_mode="HTML"
    )




# ──────────────────────────────────────────
#  Umumiy /cancel buyrug'i
# ──────────────────────────────────────────
@router.message(Command("cancel"))
async def cmd_cancel_user(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
    user = message.from_user
    text = (
        f'<tg-emoji emoji-id="6032903688949862892">❌</tg-emoji> <b>Jarayon bekor qilindi.</b>\n\n'
        f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <b>SMM Botimizga xush kelibsiz!</b>\n\n'
        f'<tg-emoji emoji-id="5231102735817918643">⚡️</tg-emoji> Quyidagi xizmatlardan birini tanlang:'
    )
    await message.answer(
        text=text,
        reply_markup=my_inline_menu(is_admin=(user.id in ADMINS)),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("smm_"))
async def callback_smm_network(callback: types.CallbackQuery):
    await callback.answer()
    network = callback.data.replace("smm_", "").capitalize()
    await callback.message.answer(
        f'<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> <b>{network}</b> xizmatlari tez orada to\'liq ishga tushadi!',
        parse_mode="HTML"
    )



# ──────────────────────────────────────────
#  Telegram Stars Handlerlari
# ──────────────────────────────────────────
@router.callback_query(F.data == "stars")
async def callback_stars(callback: types.CallbackQuery):
    await callback.answer()
    star_price = get_star_price()
    text = (
        f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Telegram Stars Xizmati</b>\n\n'
        f'<tg-emoji emoji-id="5258203794772085854">⚡️</tg-emoji> <b>O`zingiz yoki do\'stingiz uchun Telegram Stars</b> xarid qiling!\n\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>1 ta Star narxi:</b> <b>{star_price:,.0f} so\'m</b>\n'
        f'<tg-emoji emoji-id="5339517416995039810">⏱</tg-emoji> <b>Yetkazib berish:</b> 10-30 soniya\n\n'
        f'<tg-emoji emoji-id="5231102735817918643">👇</tg-emoji> <i>Kerakli miqdorni tanlang:</i>'
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=stars_menu(star_price),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("stars_buy:"))
async def callback_stars_buy_package(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    amount = int(callback.data.split(":")[1])
    star_price = get_star_price()
    total_price = int(amount * star_price)

    await state.update_data(
        stars_amount=amount,
        total_price=total_price
    )
    await state.set_state(StarsOrderFlow.waiting_for_username)

    build = InlineKeyboardBuilder()
    build.row(
        InlineKeyboardButton(
            text="O'zimga",
            callback_data="stars_for_me",
            icon_custom_emoji_id="6032693626394382504"
        )
    )
    build.row(
        InlineKeyboardButton(
            text="Bekor qilish",
            callback_data="cancel",
            icon_custom_emoji_id="6032903688949862892"
        )
    )

    await callback.message.answer(
        f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Tanlangan miqdor:</b> <b>{amount:,} Stars</b>\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Narxi:</b> <b>{total_price:,} so\'m</b>\n\n'
        f'<tg-emoji emoji-id="5201989772448381592">👤</tg-emoji> Stars yuborilishi kerak bo\'lgan Telegram <b>username</b> yoki profil havolasini yuboring:\n'
        f'<i>Misol: @sergelidanman yoki https://t.me/sergelidanman</i>',
        reply_markup=build.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "stars_custom")
async def callback_stars_custom(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(StarsOrderFlow.waiting_for_custom_amount)
    build = InlineKeyboardBuilder()
    build.button(
        text="Bekor qilish",
        callback_data="cancel",
        icon_custom_emoji_id="6032903688949862892"
    )
    await callback.message.answer(
        f'<tg-emoji emoji-id="5897501460509234625">⭐</tg-emoji> <b>Qancha Telegram Stars olmoqchisiz?</b>\n\n'
        f'<tg-emoji emoji-id="5985826831591281620">⭐</tg-emoji> Minimal miqdor: <b>50 ta</b>\n'
        f'<tg-emoji emoji-id="5985436290215057326">⭐</tg-emoji> Maksimal miqdor: <b>100,000 ta</b>\n'
        f'<i>Iltimos, faqat raqam kiriting (masalan: <code>300</code>):</i>\n',
        parse_mode="HTML",
        reply_markup=build.as_markup()
    )


@router.message(StarsOrderFlow.waiting_for_custom_amount)
async def process_stars_custom_amount(message: types.Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer('<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Iltimos, faqat musbat son kiriting (masalan: 300)!')
        return

    amount = int(text)
    if amount < 50 or amount > 100000:
        await message.answer('<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Miqdor <b>50</b> dan <b>100,000</b> gacha bo\'lishi kerak!')
        return

    star_price = get_star_price()
    total_price = int(amount * star_price)
    await state.update_data(stars_amount=amount, total_price=total_price)
    await state.set_state(StarsOrderFlow.waiting_for_username)

    build = InlineKeyboardBuilder()
    build.row(
        InlineKeyboardButton(
            text="O'zimga",
            callback_data="stars_for_me",
            icon_custom_emoji_id="6032693626394382504"
        )
    )
    build.row(
        InlineKeyboardButton(
            text="Bekor qilish",
            callback_data="cancel",
            icon_custom_emoji_id="6032903688949862892"
        )
    )

    await message.answer(
        f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Tanlangan miqdor:</b> <b>{amount:,} Stars</b>\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Narxi:</b> <b>{total_price:,} so\'m</b>\n\n'
        f'<tg-emoji emoji-id="5201989772448381592">👤</tg-emoji> Stars yuborilishi kerak bo\'lgan Telegram <b>username</b> yoki profil havolasini yuboring:\n'
        f'<i>Misol: @sergelidanman yoki https://t.me/sergelidanman</i>',
        reply_markup=build.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "stars_for_me")
async def callback_stars_for_me(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user = callback.from_user
    if not user.username:
        await callback.answer(
            "⚠️ Profilingizda Telegram username o'rnatilmagan!\n"
            "Iltimos, Telegram username-ingizni matn ko'rinishida yuboring (masalan: @username)",
            show_alert=True
        )
        return

    clean_user = user.username.lstrip("@").strip()
    username = f"@{clean_user}"

    await state.update_data(target_user=username)
    data = await state.get_data()
    if not data or "stars_amount" not in data:
        await callback.answer("⚠️ Ma'lumot eskirgan. Qaytadan miqdor tanlang.", show_alert=True)
        return

    text = (
        f'<tg-emoji emoji-id="5269381442864963988">📋</tg-emoji> <b>Stars buyurtmasi ma\'lumotlari:</b>\n\n'
        f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Xizmat:</b> <b>Telegram Stars</b>\n'
        f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji> <b>Miqdor:</b> <b>{data["stars_amount"]:,} ⭐</b>\n'
        f'<tg-emoji emoji-id="5201989772448381592">👤</tg-emoji> <b>Qabul qiluvchi:</b> <code>{username}</code> <i>(O\'zingiz)</i>\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Jami to\'lov:</b> <b>{data["total_price"]:,} so\'m</b>\n\n'
        f'<b>Buyurtmani tasdiqlaysizmi?</b>'
    )
    await callback.message.edit_text(text=text, reply_markup=stars_confirm_keyboard(), parse_mode="HTML")


@router.message(StarsOrderFlow.waiting_for_username)
async def process_stars_username(message: types.Message, state: FSMContext):
    raw_input = message.text.strip()
    clean_user = raw_input.replace("https://t.me/", "").replace("http://t.me/", "").replace("t.me/", "").lstrip("@").strip().rstrip("/")
    if not clean_user or not clean_user.replace("_", "").isalnum():
        await message.answer('<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Iltimos, to\'g\'ri Telegram username yoki havola kiriting!\nMasalan: <code>@username</code> yoki <code>https://t.me/username</code>')
        return

    username = f"@{clean_user}"
    await state.update_data(target_user=username)
    data = await state.get_data()

    text = (
        f'<tg-emoji emoji-id="5269381442864963988">📋</tg-emoji> <b>Stars buyurtmasi ma\'lumotlari:</b>\n\n'
        f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Xizmat:</b> <b>Telegram Stars</b>\n'
        f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji> <b>Miqdor:</b> <b>{data["stars_amount"]:,} ⭐</b>\n'
        f'<tg-emoji emoji-id="5201989772448381592">👤</tg-emoji> <b>Qabul qiluvchi:</b> <code>{username}</code>\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Jami to\'lov:</b> <b>{data["total_price"]:,} so\'m</b>\n\n'
        f'<b>Buyurtmani tasdiqlaysizmi?</b>'
    )
    await message.answer(text=text, reply_markup=stars_confirm_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "stars_confirm")
async def callback_stars_confirm(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if not data or "stars_amount" not in data:
        await callback.answer('⚠️ Buyurtma ma\'lumotlari eskirgan.', show_alert=True)
        return

    user_id = callback.from_user.id
    total_price = data.get("total_price", 0)
    stars_amount = data.get("stars_amount", 0)
    target_user = data.get("target_user", "").strip()

    clean_username = target_user.replace("https://t.me/", "").replace("http://t.me/", "").replace("t.me/", "").lstrip("@").strip().rstrip("/")
    if not clean_username:
        await callback.answer("⚠️ Noto'g'ri username ko'rsatilgan.", show_alert=True)
        return

    current_balance = get_user_balance(user_id)
    if current_balance < total_price:
        await state.clear()
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(
                text="Hisobni to'ldirish",
                callback_data="hisob_to'ldirish",
                icon_custom_emoji_id="6025976946083500432"
            )
        )
        keyboard.row(
            InlineKeyboardButton(
                text="« Asosiy menyu",
                callback_data="back_to_main",
                icon_custom_emoji_id="5416113713428057601"
            )
        )
        await callback.message.edit_text(
            f'<tg-emoji emoji-id="6032903688949862892">❌</tg-emoji> <b>Xizmat bekor qilindi</b>\n\n'
            f'<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <b>Balansingizda mablag\' yetarli emas!</b>\n\n'
            f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> Xizmat: <b>Telegram Stars ({stars_amount:,} ⭐)</b>\n'
            f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> Kerakli summa: <b>{total_price:,} so\'m</b>\n'
            f'<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> Sizning balansingiz: <b>{current_balance:,.0f} so\'m</b>\n\n'
            f'<i>Buyurtma berish uchun avval hisobingizni to\'ldiring 👇</i>',
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )
        return

    await state.clear()

    # Kutilmoqda xabari
    status_msg = await callback.message.edit_text(
        f'<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> <b>Stars buyurtmasi GrandSMM serveriga yuborilmoqda...</b>',
        parse_mode="HTML"
    )

    # Balansdan mablag'ni yechamiz
    add_user_balance(user_id, -total_price)

    # GrandSMM API orqali Stars sotib olish
    import time
    resp = await number_api.buy_stars(username=clean_username, amount=stars_amount)

    if resp.get("success"):
        api_order_id = resp.get("order_id") or f"ST-{int(time.time())}"
        order_num = int(time.time()) % 10000000

        # Bazaga buyurtmani yozish
        add_order_record(
            order_id=order_num,
            user_id=user_id,
            service_id=9999,
            service_title=f"Telegram Stars ({stars_amount} ta)",
            quantity=stars_amount,
            price=total_price,
            link=f"@{clean_username}"
        )
        update_order_status(order_num, "Completed")

        # Kanalga xabar yuborish
        try:
            from order_checker import send_order_to_channel
            await send_order_to_channel(callback.bot, "stars", {
                "order_id": api_order_id,
                "user_id": user_id,
                "user_name": callback.from_user.full_name,
                "username": callback.from_user.username,
                "quantity": stars_amount,
                "target_user": f"@{clean_username}",
                "price": total_price
            })
        except Exception:
            pass

        rem_balance = get_user_balance(user_id)

        # Adminga bildirishnoma yuboramiz
        for admin_id in ADMINS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f'🔔 <b>YANGI STARS BUYURTMASI (AVTOMATIK BAJARILDI)!</b>\n\n'
                        f'🆔 <b>API Order ID:</b> <code>{api_order_id}</code>\n'
                        f'👤 <b>Buyurtmachi:</b> {callback.from_user.full_name} (<code>{user_id}</code>)\n'
                        f'⭐ <b>Miqdor:</b> <b>{stars_amount:,} Stars</b>\n'
                        f'🎯 <b>Qabul qiluvchi:</b> <code>@{clean_username}</code>\n'
                        f'💰 <b>To\'lov:</b> <b>{total_price:,} so\'m</b>\n'
                        f'✅ <b>Holat:</b> Muvaffaqiyatli yuborildi'
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass

        text = (
            f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Stars buyurtmangiz muvaffaqiyatli bajarildi!</b>\n\n'
            f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>{api_order_id}</code>\n'
            f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Miqdor:</b> <b>{stars_amount:,} Stars</b>\n'
            f'<tg-emoji emoji-id="5201989772448381592">👤</tg-emoji> <b>Qabul qiluvchi:</b> <code>@{clean_username}</code>\n'
            f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>To\'lov:</b> <b>{total_price:,} so\'m</b>\n'
            f'<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>Qolgan balans:</b> <b>{rem_balance:,.0f} so\'m</b>\n\n'
            f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <i>Telegram Stars hisobingizga yetkazildi!</i>'
        )

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main", icon_custom_emoji_id="5416113713428057601"))
        await status_msg.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")

    else:
        # Xatolik yuz bersa: pulni qaytaramiz (refund)
        add_user_balance(user_id, total_price)
        error_msg = resp.get("error", "Noma'lum xatolik yuz berdi")

        # Adminga xatolik haqida xabar berish
        for admin_id in ADMINS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=(
                        f'⚠️ <b>STARS BUYURTMASIDA XATOLIK:</b>\n\n'
                        f'👤 <b>Foydalanuvchi:</b> {callback.from_user.full_name} (<code>{user_id}</code>)\n'
                        f'⭐ <b>Miqdor:</b> <b>{stars_amount:,} Stars</b>\n'
                        f'🎯 <b>Qabul qiluvchi:</b> <code>@{clean_username}</code>\n'
                        f'❌ <b>Xatolik:</b> <code>{error_msg}</code>\n'
                        f'💳 <i>Foydalanuvchiga {total_price:,} so\'m qaytarildi.</i>'
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main", icon_custom_emoji_id="5416113713428057601"))
        await status_msg.edit_text(
            f'<tg-emoji emoji-id="6028346797368283073">❌</tg-emoji> <b>Stars buyurtmasi amalga oshmadi:</b>\n\n'
            f'Sabab: <i>{error_msg}</i>\n\n'
            f'<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <b>{total_price:,} so\'m</b> mablag\' balansingizga to\'liq qaytarildi.',
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )


@router.callback_query(F.data.in_(["cancel", "cancel_order", "stars_cancel", "cancel_deposit"]))
async def callback_cancel_operation(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    user = callback.from_user
    text = (
        f'<tg-emoji emoji-id="6032903688949862892">❌</tg-emoji> <b>Xizmat bekor qilindi.</b>\n\n'
        f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <b>SMM Botimizga xush kelibsiz!</b>\n\n'
        f'<tg-emoji emoji-id="5231102735817918643">⚡️</tg-emoji> Quyidagi xizmatlardan birini tanlang:'
    )
    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=my_inline_menu(is_admin=(user.id in ADMINS)),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            text=text,
            reply_markup=my_inline_menu(is_admin=(user.id in ADMINS)),
            parse_mode="HTML"
        )


# @router.callback_query(F.data == "premium")
# async def callback_premium(callback: types.CallbackQuery):
#     await callback.answer()
#     await callback.message.answer(
#         '<tg-emoji emoji-id="5204141284775697953">🌟</tg-emoji> <b>Telegram Premium xarid qilish</b>\n\n'
#         '3 oylik, 6 oylik va 1 yillik rasmiy Telegram Premium obunalari.',
#         parse_mode="HTML"
#     )
# 
# 
# @router.callback_query(F.data == "uc")
# async def callback_uc(callback: types.CallbackQuery):
#     await callback.answer()
#     await callback.message.answer(
#         '<tg-emoji emoji-id="5314544952422704045">🎮</tg-emoji> <b>PUBG Mobile UC bo\'limi</b>\n\n'
#         'ID orqali tezkor va xavfsiz UC yuklash.',
#         parse_mode="HTML"
#     )


@router.callback_query(F.data == "hisobim")
async def callback_hisobim(callback: types.CallbackQuery):
    await callback.answer()
    user_bal = get_user_balance(callback.from_user.id)

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="💳 Hisobni to'ldirish", callback_data="hisob_to'ldirish"))
    keyboard.row(InlineKeyboardButton(text="« Asosiy menyu", callback_data="back_to_main"))

    await callback.message.answer(
        f'<tg-emoji emoji-id="6032693626394382504">👤</tg-emoji> <b>Sizning profilingiz:</b>\n\n'
        f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> Telegram ID: <code>{callback.from_user.id}</code>\n'
        f'<tg-emoji emoji-id="6032994772321309200">👤</tg-emoji> Ism: {callback.from_user.full_name}\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> Sizning balansingiz: <b>{user_bal:,.0f} so\'m</b>\n\n'
        f'Hisobingizni to\'ldirish uchun pastdagi tugmani bosing <tg-emoji emoji-id="5231102735817918643">👇</tg-emoji>',
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "hisob_to'ldirish")
async def callback_hisob_toldirish(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(DepositFlow.waiting_for_amount)

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_deposit"))

    await callback.message.answer(
        f'<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>Hisobni to\'ldirish</b>\n\n'
        f'Qancha summa to\'ldirmoqchisiz?\n'
        f'<i>Minimal to\'ldirish summasi: 1 000 so\'m</i>\n\n'
        f'Iltimos, faqat raqam kiriting (masalan: <code>10000</code>):\n'
        f'Bekor qilish uchun: /cancel',
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )


@router.message(DepositFlow.waiting_for_amount)
async def process_deposit_amount(message: types.Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer('<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Iltimos, faqat musbat butun son kiriting (masalan: 10000)!')
        return

    amount = int(text)
    if amount < 1000:
        await message.answer('<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Minimal to\'ldirish summasi: <b>1 000 so\'m</b>.')
        return
    if amount > 50000000:
        await message.answer('<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Juda katta summa kiritildi.')
        return

    await state.clear()
    dep = create_pending_deposit(message.from_user.id, amount, minutes=5)

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_deposit"))
    keyboard.row(InlineKeyboardButton(text="« Asosiy menyu", callback_data="back_to_main"))

    text_msg = (
        f'<b>To\'lov rekvizitlari:</b>\n\n'
        f'<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>Karta raqami:</b>\n<code>{CARD_NUMBER}</code> (nusxalash uchun bosing)\n'
        f'<tg-emoji emoji-id="6035084557378654059">👤</tg-emoji><b>Karta egasi:</b> <b>{CARD_HOLDER}</b>\n\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>To\'lashingiz kerak bo\'lgan ANIQ summa:</b>\n'
        f'<tg-emoji emoji-id="5415758949129404605">💰</tg-emoji> <code>{dep["exact_amount"]}</code> so\'m (nusxalash uchun bosing)\n\n'

        f'<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> <b>Amal qilish vaqti:</b> 5 daqiqa\n\n'
        f'<blockquote><tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <b>DIQQAT:</b>\n'
        f'Aynan <b>{dep["exact_amount"]}</b> so\'m o\'tkazing!\n'
        f'HumoCard orqali to\'lov tushishi bilan tizim avtomatik ravishda balansingizga <b>{dep["amount"]:,} so\'m</b> qo\'shadi.</blockquote>'
    )

    await message.answer(text=text_msg, reply_markup=keyboard.as_markup(), parse_mode="HTML")




async def render_user_orders(user_id: int, category: str = "all", page: int = 1):
    PAGE_SIZE = 5
    counts = get_user_orders_count(user_id)

    # Agar foydalanuvchida umuman birorta buyurtma bo'lmasa:
    if counts["total"] == 0:
        text = (
            '<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>Mening Buyurtmalarim</b>\n\n'
            '<i>Sizda hali birorta ham buyurtma mavjud emas.</i>\n\n'
            'Xizmatlarimizdan birini tanlab yangi buyurtma berishingiz mumkin 👇'
        )
        return text, user_empty_orders_keyboard()

    cat_total = counts.get(category, counts["total"]) if category != "all" else counts["total"]
    total_pages = max(1, (cat_total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * PAGE_SIZE

    orders = get_user_unified_orders(user_id=user_id, category=category, limit=PAGE_SIZE, offset=offset)

    category_names = {
        "all": "Barchasi",
        "smm": "SMM Xizmatlari",
        "number": "Virtual Raqamlar",
        "stars": "Telegram Stars"
    }
    cat_title = category_names.get(category, "Barchasi")

    header = (
        f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>Mening Buyurtmalarim</b> ({cat_title})\n\n'
        f'📊 <b>Jami:</b> <b>{counts["total"]} ta</b> (📦 SMM: <b>{counts["smm"]}</b> | 📱 Raqam: <b>{counts["number"]}</b> | ⭐ Stars: <b>{counts["stars"]}</b>)\n'
        f'━━━━━━━━━━━━━━━━━━━━\n\n'
    )

    if not orders:
        body = (
            f'<i>Ushbu bo\'limda ({cat_title}) hozircha buyurtmalar yo\'q.</i>\n\n'
            f'Pastdagi tugmalar orqali boshqa toifani tanlashingiz mumkin 👇'
        )
    else:
        items_text = []
        for item in orders:
            itype = item.get("type")
            oid = item.get("id")
            created_at = item.get("created_at") or ""
            price = float(item.get("price", 0.0) or 0.0)

            if itype == "stars":
                qty = item.get("quantity", 0)
                target = item.get("link") or ""
                st = (item.get("status") or "Completed").strip().lower()

                if st in ["completed", "bajarildi", "yakunlandi", "success", "done"]:
                    st_display = '<b>Yetkazildi</b> <tg-emoji emoji-id="5456432998092133477">✅</tg-emoji>'
                elif st in ["canceled", "cancelled", "refunded", "bekor"]:
                    st_display = '<b>Bekor qilingan</b> <tg-emoji emoji-id="6032903688949862892">❌</tg-emoji>'
                else:
                    st_display = '<b>Kutilmoqda</b> ⏳'

                card = (
                    f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Telegram Stars</b> <code>#{oid}</code>\n'
                    f'🌟 <b>Miqdor:</b> <b>{qty:,} Stars</b>\n'
                )
                if target:
                    card += f'👤 <b>Qabul qiluvchi:</b> <code>{target}</code>\n'
                card += (
                    f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>To\'lov:</b> <b>{price:,.0f} so\'m</b>\n'
                    f'🔎 <b>Holat:</b> {st_display}\n'
                )
                if created_at:
                    card += f'📅 <b>Sana:</b> <i>{created_at}</i>'
                items_text.append(card)

            elif itype == "number":
                num_id = item["id"]
                number_str = item.get("number") or "Noma'lum"
                country = item.get("country") or ""
                flag, country_name = get_country_display(country)
                sms_code = item.get("sms_code") or ""
                server = item.get("server") or 1
                st = (item.get("status") or "waiting").strip().lower()

                if sms_code or st in ["received", "completed", "success"]:
                    st_display = '<b>SMS qabul qilindi</b> <tg-emoji emoji-id="5456432998092133477">✅</tg-emoji>'
                    sms_display = f'<code>{sms_code}</code>' if sms_code else "<i>Mavjud</i>"
                elif st in ["canceled", "timeout", "refunded"]:
                    st_display = '<b>Bekor qilingan</b> <tg-emoji emoji-id="6032903688949862892">❌</tg-emoji>'
                    sms_display = '<i>Bekor qilingan</i>'
                else:
                    st_display = '<b>SMS kutilmoqda</b> ⏳'
                    sms_display = '<i>Kutilmoqda...</i>'

                card = (
                    f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> <b>Virtual Raqam</b> <code>#{num_id}</code>\n'
                    f'🌍 <b>Davlat:</b> {flag} <b>{country_name}</b> (Server {server})\n'
                    f'📞 <b>Raqam:</b> <code>{number_str}</code>\n'
                    f'<tg-emoji emoji-id="5456432998092133477">🔑</tg-emoji> <b>SMS Kod:</b> {sms_display}\n'
                    f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Narxi:</b> <b>{price:,.0f} so\'m</b>\n'
                    f'🔎 <b>Holat:</b> {st_display}\n'
                )
                if created_at:
                    card += f'📅 <b>Sana:</b> <i>{created_at}</i>'
                items_text.append(card)

            else:
                title = item.get("title") or "SMM Xizmat"
                qty = item.get("quantity", 0)
                link = item.get("link") or ""
                st = (item.get("status") or "Pending").strip().lower()

                if st in ["completed", "bajarildi", "yakunlandi", "success", "done", "выполнено"]:
                    st_display = '<b>Bajarilgan</b> <tg-emoji emoji-id="5456432998092133477">✅</tg-emoji>'
                elif st in ["canceled", "cancelled", "bekor qilindi", "bekor", "refunded", "failed", "canceled/refunded"]:
                    st_display = '<b>Bekor qilingan</b> <tg-emoji emoji-id="6032903688949862892">❌</tg-emoji>'
                elif st in ["partial", "qisman", "partial/refunded"]:
                    st_display = '<b>Qisman bajarilgan</b> <tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji>'
                elif st in ["in progress", "processing", "jarayonda", "bajarilmoqda"]:
                    st_display = '<b>Bajarilmoqda</b> <tg-emoji emoji-id="6538800872766034734">🚀</tg-emoji>'
                else:
                    st_display = '<b>Kutilmoqda</b> ⏳'

                card = (
                    f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>SMM Buyurtma</b> <code>#{oid}</code>\n'
                    f'📌 <b>Xizmat:</b> {title}\n'
                )
                if link:
                    card += f'🔗 <b>Havola:</b> <code>{link}</code>\n'
                card += (
                    f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji> <b>Miqdor:</b> <b>{qty:,} ta</b> | '
                    f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>{price:,.0f} so\'m</b>\n'
                    f'🔎 <b>Holat:</b> {st_display}\n'
                )
                if created_at:
                    card += f'📅 <b>Sana:</b> <i>{created_at}</i>'
                items_text.append(card)

        body = "\n\n━━━━━━━━━━━━━━━━━━━━\n\n".join(items_text)

    # Faol kutilayotgan virtual raqamlarni topamiz (tezkor SMS tekshirish tugmasi uchun)
    waiting_numbers = [item for item in orders if item.get("type") == "number" and item.get("status") == "waiting"]

    kb = user_orders_keyboard(
        category=category, 
        page=page, 
        total_pages=total_pages, 
        counts=counts, 
        waiting_numbers=waiting_numbers
    )
    return header + body, kb


@router.callback_query(F.data == "buyurtmalarim")
async def callback_orders(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    text, kb = await render_user_orders(user_id=user_id, category="all", page=1)
    try:
        await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text=text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("myord:"))
async def callback_orders_filter(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    category = parts[1] if len(parts) > 1 else "all"
    page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1
    
    text, kb = await render_user_orders(user_id=user_id, category=category, page=page)
    try:
        await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text=text, reply_markup=kb, parse_mode="HTML")


@router.message(Command("myorders", "buyurtmalar"))
async def cmd_my_orders(message: types.Message):
    user_id = message.from_user.id
    text, kb = await render_user_orders(user_id=user_id, category="all", page=1)
    await message.answer(text=text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "noop")
async def callback_noop(callback: types.CallbackQuery):
    await callback.answer()



@router.callback_query(F.data == "support")
async def callback_support(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        '<tg-emoji emoji-id="5395804191769763641">💬</tg-emoji> <b>Qo\'llab-quvvatlash xizmati:</b>\n\n'
        f'Savollaringiz bo\'lsa admin bilan bog\'laning: {ADMIN_USERNAME}',
        parse_mode="HTML"
    )


# ──────────────────────────────────────────
#  /status [order_id] buyrug'i (GrandSMM API)
# ──────────────────────────────────────────
@router.message(Command("status"))
async def cmd_check_status(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip().isdigit():
        await message.answer("Foydalanish: <code>/status [Buyurtma_ID]</code>\nMisol: <code>/status 23501</code>", parse_mode="HTML")
        return

    order_id = int(args[1].strip())
    status_msg = await message.answer('<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> Status tekshirilmoqda... ', parse_mode="HTML")
    resp = await smm_api.get_order_status(order_id)

    if "status" in resp:
        st_val = resp.get("status", "Noma'lum")
        charge_val = resp.get("charge", "0")
        curr_val = resp.get("currency", "UZS")
        start_cnt = resp.get("start_count", "0")
        rem_val = resp.get("remains", "0")

        await status_msg.edit_text(
            f'<tg-emoji emoji-id="5936143551854285132">📊</tg-emoji> <b>Buyurtma holati (#{order_id}):</b>\n\n'
            f'<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> Status: <b>{st_val}</b>\n'
            f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> To\'lov: {charge_val} {curr_val}\n'
            f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji> Boshlang\'ich: {start_cnt}\n'
            f'<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> Qolgan miqdor: {rem_val}',
            parse_mode="HTML"
        )
    else:
        err = resp.get("error", "Buyurtma topilmadi")
        await status_msg.edit_text(f'<tg-emoji emoji-id="6032903688949862892">❌</tg-emoji> <b>Xatolik:</b> {err}', parse_mode="HTML")


# ──────────────────────────────────────────
#  /help buyrug'i
# ──────────────────────────────────────────
@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        '<tg-emoji emoji-id="5258332798409783582">📖</tg-emoji> /start — Botni ishga tushirish\n'
        '<tg-emoji emoji-id="5841276284155467413">📖</tg-emoji> /id — Telegram ID ingizni bilish\n'
        '<tg-emoji emoji-id="5319310205752717294">📖</tg-emoji> /status [ID] — Buyurtma holatini tekshirish\n'
        '<tg-emoji emoji-id="5945122550353762154">📖</tg-emoji> /help — Yordam',
        parse_mode="HTML",
    )


# ──────────────────────────────────────────
#  /id buyrug'i
# ──────────────────────────────────────────
@router.message(Command("id"))
async def cmd_id(message: types.Message):
    await message.answer(
        f'<tg-emoji emoji-id="5319310205752717294">🆔</tg-emoji>Sizning Telegram ID ingiz: <code>{message.from_user.id}</code>',
        parse_mode="HTML",
    )


# ──────────────────────────────────────────
#  Virtual Nomer (SMS) Handlerlari
# ──────────────────────────────────────────

@router.callback_query(F.data == "number")
async def callback_number_menu(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> <b>Virtual Raqamlar (SMS qabul qilish)</b>\n\n'
        f'<tg-emoji emoji-id="5201989772448381592">🌐</tg-emoji> Telegram va boshqa ijtimoiy tarmoqlar uchun virtual raqam olishingiz mumkin.\n\n'
        f'<tg-emoji emoji-id="5258203794772085854">⚡️</tg-emoji> <b>Server 1:</b> Yuqori tezlik, sifatli va barqaror ulanish\n'
        f'<tg-emoji emoji-id="5215172337044826665">🌐</tg-emoji> <b>Server 2:</b> Keng davlatlar tanlovi va qulay narxlar\n\n'
        f'<tg-emoji emoji-id="5231102735817918643">👇</tg-emoji> <i>Kerakli serverni tanlang:</i>'
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=number_servers_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("num_srv_"))
async def callback_number_server(callback: types.CallbackQuery):
    await callback.answer()
    server = int(callback.data.replace("num_srv_", ""))

    if server not in number_api._countries_cache:
        try:
            await callback.message.edit_text(
                '<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> Davlatlar va narxlar yuklanmoqda...',
                parse_mode="HTML"
            )
        except Exception:
            pass

    res = await number_api.get_countries(server=server)
    if not res.get("success"):
        await callback.message.edit_text(
            f'<tg-emoji emoji-id="6032903688949862892">❌</tg-emoji> Server {server} bilan bog\'lanishda xatolik yuz berdi. Qaytadan urinib ko\'ring.',
            reply_markup=number_servers_menu(),
            parse_mode="HTML"
        )
        return

    countries = res.get("countries", {})
    if not countries:
        other_server = 2 if server == 1 else 1
        await callback.message.edit_text(
            f'<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <b>Server {server} da ayni paytda mavjud davlatlar yo\'q.</b>\n\n'
            f'Iltimos, <b>Server {other_server}</b> ni tanlab ko\'ring!',
            reply_markup=number_servers_menu(),
            parse_mode="HTML"
        )
        return

    countries = res["countries"]
    text = (
        f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> <b>Server {server} — Mavjud davlatlar:</b>\n\n'
        f'<tg-emoji emoji-id="5447410659077661506">🌐</tg-emoji> Jami davlatlar soni: <b>{len(countries)} ta</b>\n'
        f'<tg-emoji emoji-id="5231102735817918643">👇</tg-emoji> Kerakli davlat ustiga bosing:'
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=number_countries_keyboard(server=server, countries=countries, page=1, sort_by_price=False),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("num_cheap:"))
async def callback_number_cheap(callback: types.CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    server = int(parts[1])
    page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1

    res = await number_api.get_countries(server=server)
    countries = res.get("countries", {})
    if not res.get("success") or not countries:
        other_server = 2 if server == 1 else 1
        await callback.answer(f"Server {server} da hozirda davlatlar yo'q. Server {other_server} ni tanlang.", show_alert=True)
        return
    text = (
        f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> <b>Server {server} — 🔥 Arzon nomerlar:</b>\n\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <i>Narxlar eng arzonidan boshlab saralangan:</i>\n'
        f'<tg-emoji emoji-id="5447410659077661506">🌐</tg-emoji> Jami davlatlar soni: <b>{len(countries)} ta</b>\n\n'
        f'<tg-emoji emoji-id="5231102735817918643">👇</tg-emoji> Kerakli davlat ustiga bosing:'
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=number_countries_keyboard(server=server, countries=countries, page=page, sort_by_price=True),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("num_p:"))
async def callback_number_page(callback: types.CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    server = int(parts[1])
    page = int(parts[2])

    res = await number_api.get_countries(server=server)
    countries = res.get("countries", {})
    text = (
        f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> <b>Server {server} — Mavjud davlatlar:</b>\n\n'
        f'<tg-emoji emoji-id="5447410659077661506">🌐</tg-emoji> Jami davlatlar soni: <b>{len(countries)} ta</b>\n'
        f'<tg-emoji emoji-id="5231102735817918643">👇</tg-emoji> Kerakli davlat ustiga bosing:'
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=number_countries_keyboard(server=server, countries=countries, page=page, sort_by_price=False),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("num_buy:"))
async def callback_number_choose_country(callback: types.CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    server = int(parts[1])
    country = parts[2].upper()
    from_cheap = len(parts) > 3 and parts[3] == "cheap"

    res = await number_api.get_countries(server=server)
    countries = res.get("countries", {})
    c_info = countries.get(country, {})
    price = float(c_info.get("price", 0))

    flag, name = get_country_display(country)
    user_bal = get_user_balance(callback.from_user.id)

    text = (
        f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> <b>Virtual Raqam Sotib Olish</b>\n\n'
        f'🌍 <b>Davlat:</b> {flag} <b>{name} ({country})</b>\n'
        f'⚡️ <b>Server:</b> <b>Server {server}</b>\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Narxi:</b> <b>{price:,.0f} so\'m</b>\n'
        f'<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>Sizning balansingiz:</b> <b>{user_bal:,.0f} so\'m</b>\n\n'
        f'<i>Raqam sotib olinsinmi?</i>'
    )
    await callback.message.edit_text(
        text=text,
        reply_markup=number_confirm_keyboard(server=server, country=country, from_cheap=from_cheap),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("num_do_buy:"))
async def callback_number_do_buy(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    server = int(parts[1])
    country = parts[2].upper()

    res = await number_api.get_countries(server=server)
    countries = res.get("countries", {})
    c_info = countries.get(country, {})
    price = float(c_info.get("price", 0))

    current_balance = get_user_balance(user_id)
    if current_balance < price:
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(
                text="Hisobni to'ldirish",
                callback_data="hisob_to'ldirish",
                icon_custom_emoji_id="6025976946083500432"
            )
        )
        keyboard.row(
            InlineKeyboardButton(
                text="« Asosiy menyu",
                callback_data="back_to_main",
                icon_custom_emoji_id="5416113713428057601"
            )
        )
        flag, name = get_country_display(country)
        await callback.message.edit_text(
            f'<tg-emoji emoji-id="6032903688949862892">❌</tg-emoji> <b>Xizmat bekor qilindi (Mablag\' yetarli emas)</b>\n\n'
            f'<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <b>Balansingizda mablag\' yetarli emas!</b>\n\n'
            f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> Xizmat: <b>Virtual Raqam ({flag} {name})</b>\n'
            f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> Kerakli summa: <b>{price:,.0f} so\'m</b>\n'
            f'<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> Sizning balansingiz: <b>{current_balance:,.0f} so\'m</b>\n\n'
            f'<i>Raqam sotib olish uchun avval hisobingizni to\'ldiring 👇</i>',
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )
        return

    status_msg = await callback.message.edit_text(
        '<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> Raqam olinmoqda, iltimos kuting...',
        parse_mode="HTML"
    )

    # Balansdan mablag'ni yechamiz
    add_user_balance(user_id, -price)

    # API dan raqam olamiz
    resp = await number_api.get_number(server=server, country=country)

    if resp.get("success") and resp.get("number"):
        number_str = str(resp["number"]).strip()
        hash_code = str(resp.get("hash_code", "")).strip()
        flag, name = get_country_display(country)

        # Bazaga saqlaymiz
        order_id = add_virtual_number(
            user_id=user_id,
            server=server,
            country=country,
            number=number_str,
            hash_code=hash_code,
            price=price
        )

        # Kanalga xabar yuboramiz
        try:
            from order_checker import send_order_to_channel
            await send_order_to_channel(callback.bot, "number", {
                "order_id": order_id,
                "user_id": user_id,
                "user_name": callback.from_user.full_name,
                "username": callback.from_user.username,
                "number": number_str,
                "country_name": name,
                "flag": flag,
                "price": price
            })
        except Exception:
            pass

        rem_balance = get_user_balance(user_id)

        text = (
            f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Virtual Raqam Olingan!</b>\n\n'
            f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> <b>Raqam:</b> <code>{number_str}</code> <i>(nusxalash uchun bosing)</i>\n'
            f'🌍 <b>Davlat:</b> {flag} <b>{name} ({country})</b>\n'
            f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Narxi:</b> <b>{price:,.0f} so\'m</b>\n'
            f'<tg-emoji emoji-id="5445353829304387411">💳</tg-emoji> <b>Qolgan balans:</b> <b>{rem_balance:,.0f} so\'m</b>\n\n'
            f'<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> <b>Holat:</b> SMS kod kutilmoqda...\n\n'
            f'<i>Telegram ilovasiga kirib ushbu raqamni kiriting. Kod yuborilgach, pastdagi <b>📩 SMS kodni olish</b> tugmasini bosing!</i>'
        )
        await status_msg.edit_text(
            text=text,
            reply_markup=active_number_keyboard(order_id),
            parse_mode="HTML"
        )
    else:
        # Xatolik bo'lsa pulni balansga qaytaramiz
        add_user_balance(user_id, price)
        err = resp.get("error", "Raqam olishda xatolik yuz berdi")
        await status_msg.edit_text(
            f'<tg-emoji emoji-id="6032903688949862892">❌</tg-emoji> <b>Raqam olib bo\'lmadi:</b>\n\n'
            f'Sabab: <i>{err}</i>\n\n'
            f'<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> Mablag\' to\'liq balansingizga qaytarildi.',
            reply_markup=number_servers_menu(),
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("num_sms:"))
async def callback_number_get_sms(callback: types.CallbackQuery):
    order_id = int(callback.data.replace("num_sms:", ""))
    record = get_virtual_number_by_id(order_id)

    if not record:
        await callback.answer("⚠️ Raqam ma'lumotlari topilmadi.", show_alert=True)
        return

    if record.get("user_id") != callback.from_user.id:
        await callback.answer("⚠️ Bu raqam sizga tegishli emas!", show_alert=True)
        return

    # Agar allaqachon kod olingan bo'lsa
    if record.get("sms_code"):
        await callback.answer(f"🔑 Sizning SMS kodingiz: {record['sms_code']}", show_alert=True)
        return

    server = record["server"]
    hash_code = record.get("hash_code", "")
    number_str = record["number"]

    resp = await number_api.get_code(server=server, hash_code=hash_code, number=number_str)

    if resp.get("success") and resp.get("status") == "ok":
        code = resp.get("code", "")
        password = resp.get("password", "")

        # Bazani yangilaymiz
        update_virtual_number_sms(order_id, code, "received")

        flag, name = get_country_display(record["country"])
        text = (
            f'<tg-emoji emoji-id="6026257381678124710">🎉</tg-emoji> <b>SMS Kod Qabul Qilindi!</b>\n\n'
            f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> <b>Raqam:</b> <code>{number_str}</code>\n'
            f'🌍 <b>Davlat:</b> {flag} <b>{name}</b>\n\n'
            f'<tg-emoji emoji-id="5456432998092133477">🔑</tg-emoji> <b>SMS Kod:</b> <code>{code}</code> <i>(nusxalash uchun bosing)</i>\n'
        )
        if password:
            text += f'<tg-emoji emoji-id="5841276284155467413">🔐</tg-emoji> <b>2FA Parol:</b> <code>{password}</code>\n'

        text += '\n<i>Xizmatimizdan foydalanganingiz uchun rahmat!</i>'

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main", icon_custom_emoji_id="5416113713428057601")
        )
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    elif resp.get("status") == "waiting" or (not resp.get("success") and resp.get("status") == "waiting"):
        await callback.answer(
            "⏳ SMS kod hali kelmadi.\n\n"
            "Telegram ilovasiga kod yuborilganiga ishonch hosil qiling va 5-10 soniyadan so'ng qayta bosing!",
            show_alert=True
        )
    else:
        err = resp.get("error", "Kod tekshirishda xatolik")
        await callback.answer(f"⚠️ {err}", show_alert=True)


# ──────────────────────────────────────────
#  🔍 KANALDA BUYURTMA HOLATINI POPUP KO'RISH
# ──────────────────────────────────────────
@router.callback_query(F.data.startswith("chk_ord:"))
async def callback_check_order_status_popup(callback: types.CallbackQuery):
    raw_id = callback.data.split(":", 1)[1].strip()
    try:
        order_id = int(raw_id)
    except ValueError:
        await callback.answer("Noto'g'ri buyurtma ID", show_alert=True)
        return

    # 1. Orders jadvalidan tekshiramiz
    order = get_order_by_id(order_id)
    if order:
        status = (order.get("status") or "Pending").strip()
        status_lower = status.lower()

        # GrandSMM API orqali eng so'nggi holatni olishga urinib ko'ramiz
        if order.get("service_id") != 9999 and status_lower in ["pending", "in progress", "processing", "kutilmoqda"]:
            try:
                resp = await smm_api.get_order_status(order_id)
                if resp and "status" in resp:
                    api_status = str(resp["status"]).strip()
                    if api_status:
                        status = api_status
                        status_lower = status.lower()
            except Exception:
                pass

        if status_lower in ["completed", "bajarildi", "yakunlandi", "success", "done", "выполнено"]:
            status_text = "Bajarilgan ✅"
        elif status_lower in ["canceled", "cancelled", "bekor qilindi", "bekor", "refunded", "failed", "canceled/refunded"]:
            status_text = "Bekor qilingan ❌"
        elif status_lower in ["partial", "qisman", "partial/refunded"]:
            status_text = "Qisman bajarilgan ⚠️"
        elif status_lower in ["in progress", "processing", "jarayonda", "bajarilmoqda"]:
            status_text = "Bajarilmoqda 🚀"
        else:
            status_text = "Kutilmoqda ⏳"

        await callback.answer(text=status_text, show_alert=True)
        return

    # 2. Virtual raqamlar jadvalidan tekshiramiz
    vnum = get_virtual_number_by_id(order_id)
    if vnum:
        v_status = (vnum.get("status") or "pending").lower()
        if v_status in ["received", "completed", "success"]:
            status_text = "Bajarilgan ✅"
        elif v_status in ["canceled", "timeout", "refunded"]:
            status_text = "Bekor qilingan ❌"
        else:
            status_text = "Kutilmoqda ⏳"

        await callback.answer(text=status_text, show_alert=True)
        return

    # Test buyurtma (#7777777) yoki topilmagan
    if order_id == 7777777:
        await callback.answer(text="Kutilmoqda ⏳", show_alert=True)
        return

    await callback.answer(text="Kutilmoqda ⏳", show_alert=True)




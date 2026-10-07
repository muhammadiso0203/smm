"""
👑 Admin Panel — To'liq interaktiv boshqaruv paneli (aiogram 3)
Statistika, foydalanuvchilar, buyurtmalar nazorati, depozitlar, balans boshqaruvi,
API holati va ommaviy xabarlar (Broadcast) moduli.
"""
import asyncio
import logging
from aiogram import types, Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMINS
from database import (
    get_admin_full_stats,
    get_user,
    get_all_users,
    search_users,
    get_recent_users,
    ban_user,
    unban_user,
    is_banned,
    get_user_balance,
    add_user_balance,
    deduct_user_balance,
    set_user_balance,
    get_recent_orders,
    get_active_orders,
    get_order_by_id,
    update_order_status,
    get_user_orders,
    get_recent_deposits,
    get_pending_deposits,
    get_deposit_by_id,
    complete_deposit,
    get_star_price,
    set_star_price,
    get_orders_channel,
    set_orders_channel,
    add_mandatory_channel,
    get_mandatory_channels,
    get_mandatory_channel_by_id,
    delete_mandatory_channel,
    delete_mandatory_channel_by_channel_id,
    get_all_orders_count,
    get_all_unified_orders,
    update_virtual_number_status,
    search_order_anywhere,
    get_virtual_number_by_id,
    update_virtual_number_sms,
    get_user_unified_orders
)
from smm_api import smm_api
from number_api import number_api, get_country_display
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)
router = Router()


# ──────────────────────────────────────────
#  FSM Holatlari
# ──────────────────────────────────────────
class AdminState(StatesGroup):
    waiting_user_search = State()
    waiting_add_balance = State()
    waiting_sub_balance = State()
    waiting_set_balance = State()
    waiting_pm_message = State()
    waiting_order_search = State()
    waiting_star_price = State()
    waiting_orders_channel = State()
    waiting_mandatory_channel = State()
    waiting_broadcast_content = State()
    waiting_broadcast_button = State()
    confirm_broadcast = State()



# ──────────────────────────────────────────
#  Admin Inline Klaviaturalari
# ──────────────────────────────────────────

def admin_main_kb() -> InlineKeyboardMarkup:
    """Asosiy admin boshqaruv paneli menyusi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Statistika", 
            callback_data="adm:stats",
            icon_custom_emoji_id="5936143551854285132"
            ),
        InlineKeyboardButton(
            text="Foydalanuvchilar", 
            callback_data="adm:users",
            icon_custom_emoji_id="6032609071373226027"
            ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Buyurtmalar", 
            callback_data="adm:orders",
            icon_custom_emoji_id="5854908544712707500"
            ),
        InlineKeyboardButton(
            text="Depozitlar", 
            callback_data="adm:deposits",
            icon_custom_emoji_id="6025976946083500432"
            ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Balans Boshqarish", 
            callback_data="adm:balance",
            icon_custom_emoji_id="5415594207068822547"
            ),
        InlineKeyboardButton(
            text="API Balanslari", 
            callback_data="adm:api",
            icon_custom_emoji_id="5409048419211682843"
            ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Stars Narxi", 
            callback_data="adm:stars_price",
            icon_custom_emoji_id="5897792062291449826"
            ),
        InlineKeyboardButton(
            text="Buyurtmalar Kanali", 
            callback_data="adm:orders_channel",
            icon_custom_emoji_id="5206607081334906820"
            ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Majburiy Obuna", 
            callback_data="adm:mandatory_channels",
            icon_custom_emoji_id="5206607081334906820"
            ),
        InlineKeyboardButton(
            text="Ommaviy Xabar", 
            callback_data="adm:broadcast",
            icon_custom_emoji_id="4992560350982309130"
            ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Foydalanuvchi Menyusi", 
            callback_data="adm:to_user_menu",
            icon_custom_emoji_id="5456432998092133477"
            ),
    )
    return builder.as_markup()



def admin_users_kb() -> InlineKeyboardMarkup:
    """Foydalanuvchilar bo'limi menyusi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Qidirish", 
            callback_data="adm:search_user",
            icon_custom_emoji_id="5879939498149679716"
            ),
        InlineKeyboardButton(
            text="So'nggi a'zolar", 
            callback_data="adm:recent_users",
            icon_custom_emoji_id="5895288113537748673"
            ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Asosiy Panel", 
            callback_data="adm:main",
            icon_custom_emoji_id="5416113713428057601"
            ),
    )
    return builder.as_markup()


def admin_user_card_kb(user_id: int, user_is_banned: bool) -> InlineKeyboardMarkup:
    """Foydalanuvchi profili boshqaruv tugmalari"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Balans qo'shish", 
            callback_data=f"adm:addbal:{user_id}",
            icon_custom_emoji_id="6033108614724456536"
            ),
        InlineKeyboardButton(
            text="Balans ayirish", 
            callback_data=f"adm:subbal:{user_id}",
            icon_custom_emoji_id="5352652432008559570"
            ),
    )
    ban_text = "Blokdan chiqarish" if user_is_banned else "Bloklash"
    builder.row(
        InlineKeyboardButton(
            text="Balansni belgilash", 
            callback_data=f"adm:setbal:{user_id}",
            icon_custom_emoji_id="5370951118698339120"
            ),
        InlineKeyboardButton(
            text=ban_text, 
            callback_data=f"adm:toggleban:{user_id}",
            icon_custom_emoji_id="5456432998092133477"
            ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Xabar yozish", 
            callback_data=f"adm:pm:{user_id}",
            icon_custom_emoji_id="5305285720192079567"
            ),
        InlineKeyboardButton(
            text="Buyurtmalari", 
            callback_data=f"adm:uorders:{user_id}",
            icon_custom_emoji_id="5854908544712707500"
            ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Foydalanuvchilar", 
            callback_data="adm:users",
            icon_custom_emoji_id="5849979553556236550"
            ),
        InlineKeyboardButton(
            text="Asosiy Panel", 
            callback_data="adm:main",
            icon_custom_emoji_id="5416113713428057601"
            ),
    )
    return builder.as_markup()


def admin_orders_kb(counts: dict = None) -> InlineKeyboardMarkup:
    """Buyurtmalar bo'limi asosiy menyusi"""
    if not counts:
        counts = get_all_orders_count()
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"SMM ({counts.get('smm', 0)})", 
            callback_data="adm:ords:smm:1",
            icon_custom_emoji_id="6028346797368283073"
        ),
        InlineKeyboardButton(
            text=f"Stars ({counts.get('stars', 0)})", 
            callback_data="adm:ords:stars:1",
            icon_custom_emoji_id="5897792062291449826"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"Raqamlar ({counts.get('number', 0)})", 
            callback_data="adm:ords:number:1",
            icon_custom_emoji_id="5859232223865081255"
        ),
        InlineKeyboardButton(
            text=f"Faol ({counts.get('active', 0)})", 
            callback_data="adm:ords:active:1",
            icon_custom_emoji_id="5215522595922779944"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"Barchasi ({counts.get('total', 0)})", 
            callback_data="adm:ords:all:1",
            icon_custom_emoji_id="5895288113537748673"
        ),
        InlineKeyboardButton(
            text="Qidirish", 
            callback_data="adm:search_order",
            icon_custom_emoji_id="5879939498149679716"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Asosiy Panel", 
            callback_data="adm:main",
            icon_custom_emoji_id="5416113713428057601"
        ),
    )
    return builder.as_markup()


def admin_orders_list_kb(orders: list, category: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Buyurtmalar ro'yxati va sahifalash klaviaturasi"""
    builder = InlineKeyboardBuilder()
    for item in orders:
        itype = item.get("type", "smm")
        oid = item["id"]
        st = item.get("status", "Pending")
        price = float(item.get("price", 0.0) or 0.0)

        if itype == "stars":
            qty = item.get("quantity", 0)
            btn_text = f"⭐ #{oid} • {qty} Stars ({st})"
            emoji_id = "5897792062291449826"
        elif itype == "number":
            num_str = item.get("number") or "Noma'lum"
            btn_text = f"📱 #{oid} • {num_str} ({st})"
            emoji_id = "5859232223865081255"
        else:
            title = (item.get("title") or "SMM Xizmat")[:15]
            btn_text = f"📦 #{oid} • {title} ({st})"
            emoji_id = "6028346797368283073"

        builder.row(InlineKeyboardButton(
            text=btn_text,
            callback_data=f"adm:oview:{itype}:{oid}",
            icon_custom_emoji_id=emoji_id
        ))

    # Sahifalash
    if total_pages > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton(text="Oldingi", callback_data=f"adm:ords:{category}:{page - 1}", icon_custom_emoji_id="5416113713428057601"))
        nav_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop", icon_custom_emoji_id="6323234179555263965"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton(text="Keyingi", callback_data=f"adm:ords:{category}:{page + 1}", icon_custom_emoji_id="5415758949129404605"))
        builder.row(*nav_buttons)

    # Yangilash va orqaga
    builder.row(
        InlineKeyboardButton(text="Yangilash", callback_data=f"adm:ords:{category}:{page}", icon_custom_emoji_id="5346269127059196142"),
        InlineKeyboardButton(text="Bo'limlar", callback_data="adm:orders", icon_custom_emoji_id="6026239398650056451")
    )
    builder.row(
        InlineKeyboardButton(text="Asosiy Panel", callback_data="adm:main", icon_custom_emoji_id="5416113713428057601")
    )
    return builder.as_markup()


def admin_order_card_kb(item_type: str, item_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Alohida buyurtma boshqaruv tugmalari (SMM, Stars, Raqam)"""
    builder = InlineKeyboardBuilder()
    
    if item_type == "smm":
        builder.row(
            InlineKeyboardButton(
                text="APIdan tekshirish", 
                callback_data=f"adm:chkord:{item_id}",
                icon_custom_emoji_id="5895288113537748673"
            ),
        )
        builder.row(
            InlineKeyboardButton(
                text="Completed qilish", 
                callback_data=f"adm:setord_comp:{item_id}",
                icon_custom_emoji_id="6011046912078787676"
            ),
            InlineKeyboardButton(
                text="Bekor & Refund", 
                callback_data=f"adm:setord_ref:{item_id}",
                icon_custom_emoji_id="6040291696079575101"
            ),
        )
    elif item_type == "stars":
        builder.row(
            InlineKeyboardButton(
                text="Completed qilish", 
                callback_data=f"adm:setord_comp:{item_id}",
                icon_custom_emoji_id="6011046912078787676"
            ),
            InlineKeyboardButton(
                text="Bekor & Refund", 
                callback_data=f"adm:setord_ref:{item_id}",
                icon_custom_emoji_id="6040291696079575101"
            ),
        )
    elif item_type == "number":
        builder.row(
            InlineKeyboardButton(
                text="SMS tekshirish (API)", 
                callback_data=f"adm:chknum_sms:{item_id}",
                icon_custom_emoji_id="5456432998092133477"
            ),
        )
        builder.row(
            InlineKeyboardButton(
                text="Completed qilish", 
                callback_data=f"adm:setnum_comp:{item_id}",
                icon_custom_emoji_id="6011046912078787676"
            ),
            InlineKeyboardButton(
                text="Bekor & Refund", 
                callback_data=f"adm:setnum_ref:{item_id}",
                icon_custom_emoji_id="6040291696079575101"
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text="Foydalanuvchi profili", 
            callback_data=f"adm:uview:{user_id}",
            icon_custom_emoji_id="6032609071373226027"
        ),
        InlineKeyboardButton(
            text="Buyurtmalar", 
            callback_data="adm:orders",
            icon_custom_emoji_id="5854908544712707500"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Asosiy Panel", 
            callback_data="adm:main",
            icon_custom_emoji_id="5416113713428057601"
        ),
    )
    return builder.as_markup()


def admin_deposits_kb() -> InlineKeyboardMarkup:
    """Depozitlar bo'limi menyusi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Kutilayotgan to'lovlar", 
            callback_data="adm:pending_deps",
            icon_custom_emoji_id="5262838597060422237"
            ),
        InlineKeyboardButton(
            text="Barcha so'nggi to'lovlar", 
            callback_data="adm:recent_deps",
            icon_custom_emoji_id="5895288113537748673"
            ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Asosiy Panel", 
            callback_data="adm:main",
            icon_custom_emoji_id="5416113713428057601"
            ),
    )
    return builder.as_markup()


def admin_back_kb(target: str = "main") -> InlineKeyboardMarkup:
    """Orqaga qaytish tugmasi"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="Orqaga", 
        callback_data=f"adm:{target}",
        icon_custom_emoji_id="5307502033103915040"
        ))
    return builder.as_markup()


# ──────────────────────────────────────────
#  /cancel — Bekor qilish
# ──────────────────────────────────────────
@router.message(Command("cancel"), F.from_user.func(lambda u: u.id in ADMINS))
async def cmd_cancel(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current:
        await state.clear()
        await message.answer(
            '<tg-emoji emoji-id="5887518550197790885">❌</tg-emoji> Jarayon bekor qilindi.', 
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            '<tg-emoji emoji-id="5307502033103915040">ℹ️</tg-emoji> Hech qanday faol jarayon yo\'q.', 
            reply_markup=admin_main_kb(),
            parse_mode="HTML"
        )


# ──────────────────────────────────────────
#  /admin — Asosiy Panel
# ──────────────────────────────────────────
@router.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer('<tg-emoji emoji-id="6025976301838405549">🚫</tg-emoji> Bu buyruq faqat bot adminlari uchun!', parse_mode="HTML")
        return
    await state.clear()
    text = (
        '<tg-emoji emoji-id="5348306023889254367">👑</tg-emoji> <b>Boshqaruv Paneli (Admin Dashboard)</b>\n\n'
        '<tg-emoji emoji-id="5231102735817918643">😊</tg-emoji> Quyidagi bo\'limlardan birini tanlang:\n\n'
    )
    await message.answer(text, reply_markup=admin_main_kb(), parse_mode="HTML")


@router.callback_query(F.data == "adm:main", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_admin_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        '<tg-emoji emoji-id="5348306023889254367">👑</tg-emoji> <b>Boshqaruv Paneli (Admin Dashboard)</b>\n\n'
        '<tg-emoji emoji-id="5231102735817918643">😊</tg-emoji> Quyidagi bo\'limlardan birini tanlang:\n\n'
    )
    try:
        await callback.message.edit_text(text, reply_markup=admin_main_kb(), parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=admin_main_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:to_user_menu")
async def cb_to_user_menu(callback: types.CallbackQuery):
    from keyboards import my_inline_menu
    user = callback.from_user
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
    await callback.answer()


# ──────────────────────────────────────────
#  📊 STATISTIKA BO'LIMI
# ──────────────────────────────────────────
@router.callback_query(F.data == "adm:stats", F.from_user.func(lambda u: u.id in ADMINS))
@router.message(Command("stats"), F.from_user.func(lambda u: u.id in ADMINS))
async def show_admin_stats(event: types.Message | types.CallbackQuery):
    s = get_admin_full_stats()
    text = (
        '<tg-emoji emoji-id="5936143551854285132">📊</tg-emoji> <b>Botning To\'liq Statistikasi va Moliyaviy Tahlili</b>\n\n'
        f'<tg-emoji emoji-id="6032609071373226027">👥</tg-emoji> <b>Foydalanuvchilar:</b>\n'
        f' ├ Jami a\'zolar: <b>{s["total_users"]:,} ta</b>\n'
        f' ├ Bugun qo\'shilgan: <b>+{s["today_users"]:,} ta</b>\n'
        f' └ Bloklanganlar: <b>{s["banned_users"]:,} ta</b>\n\n'
        f'<tg-emoji emoji-id="5415594207068822547">💰</tg-emoji> <b>Foydalanuvchilar Balansi:</b>\n'
        f' └ Jami botdagi qoldiq: <b>{s["total_user_balance"]:,.0f} so\'m</b>\n\n'
        f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>SMM Buyurtmalar:</b>\n'
        f' ├ Jami buyurtmalar: <b>{s["orders_total"]:,} ta</b>\n'
        f' ├ Jami aylanma: <b>{s["total_order_sum"]:,.0f} so\'m</b>\n'
        f' ├ Bugungi buyurtmalar: <b>{s["orders_today"]:,} ta</b>\n'
        f' ├ Bugungi aylanma: <b>{s["today_order_sum"]:,.0f} so\'m</b>\n'
        f' └ Hozirda faol/kutilayotgan: <b>{s["active_orders_count"]:,} ta</b>\n\n'
        f'<tg-emoji emoji-id="6025976946083500432">💳</tg-emoji> <b>Hisob To\'ldirishlar (Depozitlar):</b>\n'
        f' ├ Jami to\'ldirilgan: <b>{s["total_deposits_sum"]:,.0f} so\'m</b>\n'
        f' ├ Bugun to\'ldirilgan: <b>{s["today_deposits_sum"]:,.0f} so\'m</b>\n'
        f' └ Kutilayotgan to\'lovlar: <b>{s["pending_deposits_count"]:,} ta</b>\n\n'
        f'<tg-emoji emoji-id="5444965061749644170">📱</tg-emoji> <b>Virtual SMS Raqamlar:</b>\n'
        f' └ Jami olingan raqamlar: <b>{s["virtual_numbers_count"]:,} ta</b>'
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Yangilash", 
            callback_data="adm:stats",
            icon_custom_emoji_id="5895288113537748673"
        ),
        InlineKeyboardButton(
            text="Asosiy Panel", 
            callback_data="adm:main",
            icon_custom_emoji_id="5416113713428057601"
        ),
    )

    if isinstance(event, types.CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
        except Exception:
            pass
        await event.answer()
    else:
        await event.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


# ──────────────────────────────────────────
#  👥 FOYDALANUVCHILAR BO'LIMI
# ──────────────────────────────────────────
@router.callback_query(F.data == "adm:users", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_users_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        '<tg-emoji emoji-id="6032609071373226027">👥</tg-emoji> <b>Foydalanuvchilarni Boshqarish</b>\n\n'
        'Foydalanuvchi profilini ko\'rish, balansini tahrirlash, bloklash yoki shaxsiy xabar yuborish uchun quyidagi imkoniyatlardan foydalaning:'
    )
    await callback.message.edit_text(text, reply_markup=admin_users_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:recent_users", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_recent_users(callback: types.CallbackQuery):
    users = get_recent_users(8)
    if not users:
        await callback.message.edit_text("Hozircha foydalanuvchilar mavjud emas.", reply_markup=admin_back_kb("users"))
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    text_lines = ["📋 <b>So'nggi ro'yxatdan o'tgan foydalanuvchilar:</b>\n"]
    for u in users:
        uid = u["user_id"]
        name = (u["full_name"] or "Foydalanuvchi")[:18]
        bal = float(u.get("balance", 0.0) or 0.0)
        status_icon = "🚫" if u.get("is_banned") else "🟢"
        text_lines.append(f"{status_icon} <code>{uid}</code> | {name} | <b>{bal:,.0f} so'm</b>")
        builder.row(InlineKeyboardButton(text=f"👤 {name} ({uid})", callback_data=f"adm:uview:{uid}"))

    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:users"))
    await callback.message.edit_text("\n".join(text_lines), reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:search_user", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_search_user_prompt(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.waiting_user_search)
    await callback.message.edit_text(
        "🔍 <b>Foydalanuvchi Qidiruvi</b>\n\n"
        "Foydalanuvchining <b>Telegram ID</b> raqamini yoki <b>@username</b>ini yuboring:",
        reply_markup=admin_back_kb("users"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminState.waiting_user_search, F.from_user.func(lambda u: u.id in ADMINS))
async def process_user_search(message: types.Message, state: FSMContext):
    query = message.text.strip()
    results = search_users(query, limit=6)
    if not results:
        await message.answer(
            f"❌ <code>{query}</code> bo'yicha hech qanday foydalanuvchi topilmadi.",
            reply_markup=admin_users_kb(),
            parse_mode="HTML"
        )
        return

    if len(results) == 1:
        await state.clear()
        await send_user_card(message, results[0]["user_id"])
        return

    builder = InlineKeyboardBuilder()
    text = "🔍 <b>Qidiruv natijalari:</b>\n"
    for u in results:
        uid = u["user_id"]
        name = (u["full_name"] or "Foydalanuvchi")[:18]
        bal = float(u.get("balance", 0.0) or 0.0)
        builder.row(InlineKeyboardButton(text=f"{name} ({bal:,.0f} so'm)", callback_data=f"adm:uview:{uid}"))
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="adm:users"))

    await state.clear()
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


async def send_user_card(event: types.Message | types.CallbackQuery, user_id: int):
    """Foydalanuvchi profil kartasini chiqarish"""
    user = get_user(user_id)
    if not user:
        err_text = "❌ Foydalanuvchi ma'lumotlari bazadan topilmadi."
        if isinstance(event, types.CallbackQuery):
            await event.message.edit_text(err_text, reply_markup=admin_back_kb("users"))
            await event.answer()
        else:
            await event.answer(err_text, reply_markup=admin_back_kb("users"))
        return

    uid = user["user_id"]
    name = user["full_name"] or "—"
    uname = f"@{user['username']}" if user.get("username") else "yo'q"
    bal = float(user.get("balance", 0.0) or 0.0)
    banned = bool(user.get("is_banned", 0))
    joined = user.get("joined_at", "—")
    last_seen = user.get("last_seen", "—")

    text = (
        f'<tg-emoji emoji-id="6032609071373226027">👤</tg-emoji> <b>Foydalanuvchi Profili</b>\n\n'
        f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Telegram ID:</b> <code>{uid}</code>\n'
        f'👤 <b>Ism:</b> <b>{name}</b>\n'
        f'🔗 <b>Username:</b> {uname}\n'
        f'<tg-emoji emoji-id="5415594207068822547">💰</tg-emoji> <b>Balans:</b> <b>{bal:,.0f} so\'m</b>\n'
        f'📊 <b>Holati:</b> {"🚫 Bloklangan" if banned else "🟢 Faol"}\n'
        f'📅 <b>Ro\'yxatdan o\'tgan:</b> {joined}\n'
        f'🕐 <b>Oxirgi faollik:</b> {last_seen}'
    )

    kb = admin_user_card_kb(uid, banned)
    if isinstance(event, types.CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("adm:uview:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_user_view(callback: types.CallbackQuery):
    uid = int(callback.data.split(":")[2])
    await send_user_card(callback, uid)


# ──────────────────────────────────────────
#  BALANS BOSHQARISH VA BAN
# ──────────────────────────────────────────
@router.callback_query(F.data == "adm:balance", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_balance_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.waiting_user_search)
    await callback.message.edit_text(
        '<tg-emoji emoji-id="5415594207068822547">💰</tg-emoji> <b>Foydalanuvchi Balansini Boshqarish</b>\n\n'
        'Balansini o\'zgartirmoqchi bo\'lgan foydalanuvchining <b>Telegram ID</b> yoki <b>@username</b>ini yuboring:',
        reply_markup=admin_back_kb("main"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm:addbal:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_add_bal_prompt(callback: types.CallbackQuery, state: FSMContext):
    uid = int(callback.data.split(":")[2])
    await state.update_data(target_user_id=uid)
    await state.set_state(AdminState.waiting_add_balance)
    await callback.message.edit_text(
        f'<tg-emoji emoji-id="6033108614724456536">➕</tg-emoji> <b>Balans qo\'shish</b>\n\n'
        f'Foydalanuvchi ID: <code>{uid}</code>\n'
        f'Qo\'shiladigan summani so\'mda kiriting (masalan: <code>10000</code>):',
        reply_markup=admin_back_kb(f"uview:{uid}"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminState.waiting_add_balance, F.from_user.func(lambda u: u.id in ADMINS))
async def process_add_balance(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    uid = data.get("target_user_id")
    await state.clear()
    try:
        amount = float(message.text.strip().replace(" ", "").replace(",", "."))
        if amount <= 0:
            await message.answer("❌ Summa 0 dan katta bo'lishi kerak.")
            return
        new_bal = add_user_balance(uid, amount)
        await message.answer(
            f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Balans muvaffaqiyatli qo\'shildi!</b>\n\n'
            f'👤 Foydalanuvchi: <code>{uid}</code>\n'
            f'➕ Qo\'shildi: <b>{amount:,.0f} so\'m</b>\n'
            f'<tg-emoji emoji-id="5415594207068822547">💰</tg-emoji> Yangi balans: <b>{new_bal:,.0f} so\'m</b>',
            reply_markup=admin_user_card_kb(uid, is_banned(uid)),
            parse_mode="HTML"
        )
        # Foydalanuvchiga bildirishnoma yuborish
        try:
            await bot.send_message(
                chat_id=uid,
                text=(
                    f'<tg-emoji emoji-id="5251203410396458957">🎁</tg-emoji> <b>Hisobingiz to\'ldirildi!</b>\n\n'
                    f'➕ <b>Qo\'shilgan summa:</b> <b>{amount:,.0f} so\'m</b>\n'
                    f'<tg-emoji emoji-id="5415594207068822547">💰</tg-emoji> <b>Joriy balansingiz:</b> <b>{new_bal:,.0f} so\'m</b>'
                ),
                parse_mode="HTML"
            )
        except Exception:
            pass
    except ValueError:
        await message.answer("❌ Noto'g'ri summa formati! Faqat raqam kiriting.", reply_markup=admin_users_kb())


@router.callback_query(F.data.startswith("adm:subbal:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_sub_bal_prompt(callback: types.CallbackQuery, state: FSMContext):
    uid = int(callback.data.split(":")[2])
    await state.update_data(target_user_id=uid)
    await state.set_state(AdminState.waiting_sub_balance)
    await callback.message.edit_text(
        f'<tg-emoji emoji-id="5352652432008559570">➖</tg-emoji> <b>Balans ayirish (yechish)</b>\n\n'
        f'Foydalanuvchi ID: <code>{uid}</code>\n'
        f'Ayiriladigan summani kiriting (masalan: <code>5000</code>):',
        reply_markup=admin_back_kb(f"uview:{uid}"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminState.waiting_sub_balance, F.from_user.func(lambda u: u.id in ADMINS))
async def process_sub_balance(message: types.Message, state: FSMContext):
    data = await state.get_data()
    uid = data.get("target_user_id")
    await state.clear()
    try:
        amount = float(message.text.strip().replace(" ", "").replace(",", "."))
        if amount <= 0:
            await message.answer("❌ Summa 0 dan katta bo'lishi kerak.")
            return
        new_bal = deduct_user_balance(uid, amount)
        await message.answer(
            f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Balansdan muvaffaqiyatli ayirildi!</b>\n\n'
            f'👤 Foydalanuvchi: <code>{uid}</code>\n'
            f'➖ Ayirildi: <b>{amount:,.0f} so\'m</b>\n'
            f'<tg-emoji emoji-id="5415594207068822547">💰</tg-emoji> Yangi balans: <b>{new_bal:,.0f} so\'m</b>',
            reply_markup=admin_user_card_kb(uid, is_banned(uid)),
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Noto'g'ri summa formati! Faqat raqam kiriting.", reply_markup=admin_users_kb())


@router.callback_query(F.data.startswith("adm:setbal:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_set_bal_prompt(callback: types.CallbackQuery, state: FSMContext):
    uid = int(callback.data.split(":")[2])
    await state.update_data(target_user_id=uid)
    await state.set_state(AdminState.waiting_set_balance)
    await callback.message.edit_text(
        f'<tg-emoji emoji-id="5370951118698339120">✏️</tg-emoji> <b>Balansni Aniq Belgilash</b>\n\n'
        f'Foydalanuvchi ID: <code>{uid}</code>\n'
        f'Yangi balans qiymatini kiriting (masalan: <code>25000</code>):',
        reply_markup=admin_back_kb(f"uview:{uid}"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminState.waiting_set_balance, F.from_user.func(lambda u: u.id in ADMINS))
async def process_set_balance(message: types.Message, state: FSMContext):
    data = await state.get_data()
    uid = data.get("target_user_id")
    await state.clear()
    try:
        amount = float(message.text.strip().replace(" ", "").replace(",", "."))
        if amount < 0:
            await message.answer("❌ Summa manfiy bo'lishi mumkin emas.")
            return
        new_bal = set_user_balance(uid, amount)
        await message.answer(
            f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Balans belgilandi!</b>\n\n'
            f'👤 Foydalanuvchi: <code>{uid}</code>\n'
            f'<tg-emoji emoji-id="5415594207068822547">💰</tg-emoji> Yangi balans: <b>{new_bal:,.0f} so\'m</b>',
            reply_markup=admin_user_card_kb(uid, is_banned(uid)),
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Noto'g'ri summa formati!", reply_markup=admin_users_kb())


@router.callback_query(F.data.startswith("adm:toggleban:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_toggle_ban(callback: types.CallbackQuery):
    uid = int(callback.data.split(":")[2])
    if uid in ADMINS:
        await callback.answer("⚠️ Adminlarni bloklash mumkin emas!", show_alert=True)
        return
    banned = is_banned(uid)
    if banned:
        unban_user(uid)
        await callback.answer("✅ Blokdan chiqarildi!", show_alert=True)
    else:
        ban_user(uid)
        await callback.answer("🚫 Foydalanuvchi bloklandi!", show_alert=True)
    await send_user_card(callback, uid)


# ──────────────────────────────────────────
#  ✉️ SHAXSIY XABAR YOZISH
# ──────────────────────────────────────────
@router.callback_query(F.data.startswith("adm:pm:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_pm_prompt(callback: types.CallbackQuery, state: FSMContext):
    uid = int(callback.data.split(":")[2])
    await state.update_data(target_user_id=uid)
    await state.set_state(AdminState.waiting_pm_message)
    await callback.message.edit_text(
        f'<tg-emoji emoji-id="5305285720192079567">✉️</tg-emoji> <b>Foydalanuvchiga xabar yuborish</b>\n\n'
        f'Qabul qiluvchi: <code>{uid}</code>\n'
        f'Xabaringizni yozing (matn, rasm yoki video):',
        reply_markup=admin_back_kb(f"uview:{uid}"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminState.waiting_pm_message, F.from_user.func(lambda u: u.id in ADMINS))
async def process_pm_message(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    uid = data.get("target_user_id")
    await state.clear()
    try:
        header_text = '<tg-emoji emoji-id="5305285720192079567">📩</tg-emoji> <b>Admin xabari:</b>\n\n'
        if message.text:
            await bot.send_message(chat_id=uid, text=header_text + message.text, parse_mode="HTML")
        elif message.caption:
            await message.copy_to(chat_id=uid, caption=header_text + message.caption, parse_mode="HTML")
        else:
            await message.copy_to(chat_id=uid)

        await message.answer(
            f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Xabar <code>{uid}</code> ga muvaffaqiyatli yetkazildi!</b>',
            reply_markup=admin_user_card_kb(uid, is_banned(uid)),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(
            f"❌ <b>Xabar yuborishda xatolik:</b> {e}",
            reply_markup=admin_user_card_kb(uid, is_banned(uid)),
            parse_mode="HTML"
        )


# ──────────────────────────────────────────
#  📦 BUYURTMALAR BO'LIMI (SMM, Stars, Raqamlar)
# ──────────────────────────────────────────
@router.callback_query(F.data == "adm:orders", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_orders_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    counts = get_all_orders_count()
    text = (
        '<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>Barcha Buyurtmalar Boshqaruvi</b>\n\n'
        'Kerakli buyurtmalar toifasini tanlang:\n\n'
        f'<tg-emoji emoji-id="6028346797368283073">📦</tg-emoji> <b>SMM Buyurtmalari:</b> <code>{counts.get("smm", 0)} ta</code>\n'
        f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Telegram Stars:</b> <code>{counts.get("stars", 0)} ta</code>\n'
        f'<tg-emoji emoji-id="5859232223865081255">📱</tg-emoji> <b>Virtual Raqamlar:</b> <code>{counts.get("number", 0)} ta</code>\n'
        f'<tg-emoji emoji-id="5215522595922779944">⏳</tg-emoji> <b>Faol / Kutilayotgan:</b> <code>{counts.get("active", 0)} ta</code>\n\n'
        f'<tg-emoji emoji-id="5444965061749644170">📊</tg-emoji> <b>Jami barcha buyurtmalar:</b> <b>{counts.get("total", 0)} ta</b>'
    )
    try:
        await callback.message.edit_text(text, reply_markup=admin_orders_kb(counts), parse_mode="HTML")
        await callback.answer()
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            await callback.answer("✅ Yangilandi")
        else:
            await callback.answer()
    except Exception:
        await callback.answer()


@router.callback_query(F.data.startswith("adm:ords:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_admin_orders_category(callback: types.CallbackQuery):
    parts = callback.data.split(":")
    category = parts[2] if len(parts) > 2 else "all"
    page = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 1

    PAGE_SIZE = 8
    counts = get_all_orders_count()
    cat_total = counts.get(category, counts.get("total", 0))
    total_pages = max(1, (cat_total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * PAGE_SIZE

    orders = get_all_unified_orders(category=category, limit=PAGE_SIZE, offset=offset)

    category_names = {
        "smm": '<tg-emoji emoji-id="6028346797368283073">📦</tg-emoji> <b>SMM Buyurtmalari</b>',
        "stars": '<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Telegram Stars Buyurtmalari</b>',
        "number": '<tg-emoji emoji-id="5859232223865081255">📱</tg-emoji> <b>Virtual Raqamlar</b>',
        "active": '<tg-emoji emoji-id="5215522595922779944">⏳</tg-emoji> <b>Faol / Kutilayotgan Buyurtmalar</b>',
        "all": '<tg-emoji emoji-id="5895288113537748673">📋</tg-emoji> <b>Barcha Buyurtmalar</b>'
    }
    cat_title = category_names.get(category, "<b>Buyurtmalar</b>")

    if not orders:
        text = f"{cat_title}\n\n<i>Ushbu bo'limda hozircha buyurtmalar yo'q.</i>"
    else:
        text = (
            f"{cat_title}\n"
            f"📊 <b>Jami:</b> <b>{cat_total} ta</b> | Sahifa: <b>{page}/{total_pages}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Batafsil ko'rish va boshqarish uchun buyurtma tugmasini bosing:</i>"
        )

    kb = admin_orders_list_kb(orders=orders, category=category, page=page, total_pages=total_pages)
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer("✅ Yangilandi")
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            await callback.answer("✅ Yangilandi")
        else:
            await callback.answer()
    except Exception:
        await callback.answer()


@router.callback_query(F.data.startswith("adm:oview:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_order_view(callback: types.CallbackQuery):
    parts = callback.data.split(":")
    if len(parts) >= 4:
        itype = parts[2]
        oid = parts[3]
        await send_order_card(callback, oid, item_type=itype)
    else:
        oid = parts[2]
        await send_order_card(callback, oid)


@router.callback_query(F.data == "adm:search_order", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_search_order_prompt(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.waiting_order_search)
    await callback.message.edit_text(
        '<tg-emoji emoji-id="6022479300876686639">🔍</tg-emoji> <b>Buyurtmani Qidirish</b>\n\n'
        'Buyurtma <b>ID raqami</b> (masalan: <code>7016513</code>) yoki <b>Telefon raqami</b>ni yuboring:',
        reply_markup=admin_back_kb("orders"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminState.waiting_order_search, F.from_user.func(lambda u: u.id in ADMINS))
async def process_order_search(message: types.Message, state: FSMContext):
    await state.clear()
    query = message.text.strip()
    item = search_order_anywhere(query)
    if not item:
        await message.answer(
            f"❌ <code>{query}</code> bo'yicha hech qanday buyurtma (SMM, Stars yoki Raqam) topilmadi.", 
            reply_markup=admin_orders_kb()
        )
        return
    await send_order_card(message, item)


async def send_order_card(event: types.Message | types.CallbackQuery, item_or_id, item_type: str = None):
    """Buyurtma kartasini chiqarish (SMM, Stars, Raqam)"""
    if isinstance(item_or_id, dict):
        item = item_or_id
        itype = item.get("type") or item_type or "smm"
    else:
        raw_id = str(item_or_id).strip().replace("#", "")
        if item_type == "number":
            v_item = get_virtual_number_by_id(int(raw_id)) if raw_id.isdigit() else None
            item = {"type": "number", **v_item} if v_item else None
        elif item_type in ["smm", "stars"]:
            o_item = get_order_by_id(int(raw_id)) if raw_id.isdigit() else None
            if o_item:
                is_stars = (o_item.get("service_id") == 9999)
                item = {"type": "stars" if is_stars else "smm", **o_item}
            else:
                item = None
        else:
            item = search_order_anywhere(raw_id)
            
    if not item:
        err_text = "❌ Buyurtma topilmadi."
        if isinstance(event, types.CallbackQuery):
            await event.message.edit_text(err_text, reply_markup=admin_back_kb("orders"), parse_mode="HTML")
            await event.answer()
        else:
            await event.answer(err_text, reply_markup=admin_back_kb("orders"), parse_mode="HTML")
        return

    itype = item.get("type", "smm")
    oid = item.get("order_id") or item.get("id")
    uid = item.get("user_id")
    price = float(item.get("price", 0.0) or 0.0)
    st = item.get("status", "Pending")
    created = item.get("created_at", "—")

    if itype == "stars":
        qty = item.get("quantity", 0)
        link = item.get("link", "—")
        text = (
            f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Telegram Stars Buyurtmasi</b>\n\n'
            f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{oid}</code>\n'
            f'👤 <b>Foydalanuvchi ID:</b> <code>{uid}</code>\n'
            f'🌟 <b>Miqdor:</b> <b>{qty:,} Stars</b>\n'
            f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>To\'lov:</b> <b>{price:,.0f} so\'m</b>\n'
            f'📊 <b>Status:</b> <code>{st}</code>\n'
            f'👤 <b>Qabul qiluvchi:</b> <code>{link}</code>\n'
            f'📅 <b>Sana:</b> {created}'
        )
    elif itype == "number":
        server = item.get("server", 1)
        country = item.get("country", "")
        flag, country_name = get_country_display(country)
        number_str = item.get("number", "—")
        sms_code = item.get("sms_code") or "<i>Kutilmoqda...</i>"
        text = (
            f'<tg-emoji emoji-id="5859232223865081255">📱</tg-emoji> <b>Virtual Raqam Buyurtmasi</b>\n\n'
            f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Raqam ID:</b> <code>#{oid}</code>\n'
            f'👤 <b>Foydalanuvchi ID:</b> <code>{uid}</code>\n'
            f'🌍 <b>Davlat:</b> {flag} <b>{country_name}</b> (Server {server})\n'
            f'📞 <b>Raqam:</b> <code>{number_str}</code>\n'
            f'<tg-emoji emoji-id="5456432998092133477">🔑</tg-emoji> <b>SMS Kod:</b> <code>{sms_code}</code>\n'
            f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Narxi:</b> <b>{price:,.0f} so\'m</b>\n'
            f'📊 <b>Status:</b> <code>{st}</code>\n'
            f'📅 <b>Sana:</b> {created}'
        )
    else: # SMM
        title = item.get("service_title") or item.get("title") or "SMM Xizmat"
        qty = item.get("quantity", 0)
        link = item.get("link", "—")
        text = (
            f'<tg-emoji emoji-id="6028346797368283073">📦</tg-emoji> <b>SMM Buyurtma Kartasi</b>\n\n'
            f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{oid}</code>\n'
            f'👤 <b>Foydalanuvchi ID:</b> <code>{uid}</code>\n'
            f'📌 <b>Xizmat:</b> <b>{title}</b>\n'
            f'<tg-emoji emoji-id="6323436631428695574">🔢</tg-emoji> <b>Miqdor:</b> <b>{qty:,} ta</b>\n'
            f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Narxi:</b> <b>{price:,.0f} so\'m</b>\n'
            f'📊 <b>Status:</b> <code>{st}</code>\n'
            f'<tg-emoji emoji-id="5201989772448381592">🔗</tg-emoji> <b>Havola:</b> {link}\n'
            f'📅 <b>Sana:</b> {created}'
        )

    kb = admin_order_card_kb(itype, oid, uid)
    if isinstance(event, types.CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("adm:chkord:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_check_order_api(callback: types.CallbackQuery):
    oid = int(callback.data.split(":")[2])
    resp = await smm_api.get_order_status(oid)
    if not resp or "status" not in resp:
        await callback.answer(f"API javob bermadi: {resp}", show_alert=True)
        return

    api_status = resp.get("status")
    remains = resp.get("remains", "0")
    charge = resp.get("charge", "—")
    if api_status:
        update_order_status(oid, str(api_status).capitalize())
    await callback.answer(
        f"GrandSMM Status: {api_status}\nQoldiq (Remains): {remains}\nAPI Charge: {charge}",
        show_alert=True
    )
    await send_order_card(callback, oid, item_type="smm")


@router.callback_query(F.data.startswith("adm:chknum_sms:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_admin_check_number_sms(callback: types.CallbackQuery):
    order_id = int(callback.data.split(":")[2])
    record = get_virtual_number_by_id(order_id)
    if not record:
        await callback.answer("⚠️ Raqam ma'lumotlari topilmadi.", show_alert=True)
        return

    server = record["server"]
    hash_code = record.get("hash_code", "")
    number_str = record["number"]

    resp = await number_api.get_code(server=server, hash_code=hash_code, number=number_str)
    if resp.get("success") and resp.get("status") == "ok":
        code = resp.get("code", "")
        update_virtual_number_sms(order_id, code, "received")
        await callback.answer(f"🎉 SMS Kod Qabul Qilindi: {code}", show_alert=True)
    elif resp.get("status") == "waiting":
        await callback.answer("⏳ SMS kod hali kelmadi (Kutilmoqda)", show_alert=True)
    else:
        err = resp.get("error", "Kod tekshirishda xatolik")
        await callback.answer(f"⚠️ {err}", show_alert=True)

    await send_order_card(callback, order_id, item_type="number")


@router.callback_query(F.data.startswith("adm:setord_comp:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_set_order_completed(callback: types.CallbackQuery):
    oid = int(callback.data.split(":")[2])
    update_order_status(oid, "Completed")
    await callback.answer("✅ Status 'Completed' ga o'zgartirildi!", show_alert=True)
    await send_order_card(callback, oid)


@router.callback_query(F.data.startswith("adm:setord_ref:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_set_order_refund(callback: types.CallbackQuery):
    oid = int(callback.data.split(":")[2])
    ord_item = get_order_by_id(oid)
    if ord_item:
        uid = ord_item["user_id"]
        price = float(ord_item.get("price", 0.0) or 0.0)
        update_order_status(oid, "Canceled/Refunded")
        add_user_balance(uid, price)
        await callback.answer(f"❌ Bekor qilindi va {price:,.0f} so'm foydalanuvchiga qaytarildi!", show_alert=True)
    await send_order_card(callback, oid)


@router.callback_query(F.data.startswith("adm:setnum_comp:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_set_number_completed(callback: types.CallbackQuery):
    oid = int(callback.data.split(":")[2])
    update_virtual_number_status(oid, "completed")
    await callback.answer("✅ Raqam statusi 'Completed' ga o'zgartirildi!", show_alert=True)
    await send_order_card(callback, oid, item_type="number")


@router.callback_query(F.data.startswith("adm:setnum_ref:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_set_number_refund(callback: types.CallbackQuery):
    oid = int(callback.data.split(":")[2])
    vnum = get_virtual_number_by_id(oid)
    if vnum:
        uid = vnum["user_id"]
        price = float(vnum.get("price", 0.0) or 0.0)
        update_virtual_number_status(oid, "canceled")
        add_user_balance(uid, price)
        await callback.answer(f"❌ Raqam bekor qilindi va {price:,.0f} so'm foydalanuvchiga qaytarildi!", show_alert=True)
    await send_order_card(callback, oid, item_type="number")


@router.callback_query(F.data.startswith("adm:uorders:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_user_orders_list(callback: types.CallbackQuery):
    uid = int(callback.data.split(":")[2])
    orders = get_user_unified_orders(uid, category="all", limit=8, offset=0)
    if not orders:
        await callback.answer("Bu foydalanuvchida buyurtmalar mavjud emas.", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    text_lines = [f'<tg-emoji emoji-id="5854908544712707500">📦</tg-emoji> <b>Foydalanuvchi <code>{uid}</code> ning barcha buyurtmalari:</b>\n']
    for o in orders:
        itype = o.get("type", "smm")
        oid = o["id"]
        st = o.get("status", "Pending")
        price = float(o.get("price", 0.0) or 0.0)

        if itype == "stars":
            qty = o.get("quantity", 0)
            btn_text = f"⭐ #{oid} • {qty} Stars ({st})"
            emoji_id = "5897792062291449826"
        elif itype == "number":
            num_str = o.get("number") or "Noma'lum"
            btn_text = f"📱 #{oid} • {num_str} ({st})"
            emoji_id = "5859232223865081255"
        else:
            title = (o.get("title") or "SMM Xizmat")[:15]
            btn_text = f"📦 #{oid} • {title} ({st})"
            emoji_id = "6028346797368283073"

        builder.row(InlineKeyboardButton(
            text=btn_text, 
            callback_data=f"adm:oview:{itype}:{oid}",
            icon_custom_emoji_id=emoji_id
        ))

    builder.row(InlineKeyboardButton(
        text="Foydalanuvchiga qaytish", 
        callback_data=f"adm:uview:{uid}",
        icon_custom_emoji_id="5307502033103915040"
    ))
    await callback.message.edit_text("\n".join(text_lines), reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ──────────────────────────────────────────
#  💳 DEPOZITLAR BO'LIMI
# ──────────────────────────────────────────
@router.callback_query(F.data == "adm:deposits", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_deposits_menu(callback: types.CallbackQuery):
    text = (
        '<tg-emoji emoji-id="6025976946083500432">💳</tg-emoji> <b>Hisob To\'ldirishlar (Depozitlar) Nazorati</b>\n\n'
        'Click/Payme to\'lovlari holatini kuzatish va kutilayotgan to\'lovlarni qo\'lda tasdiqlash:'
    )
    await callback.message.edit_text(text, reply_markup=admin_deposits_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:pending_deps", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_pending_deposits(callback: types.CallbackQuery):
    deps = get_pending_deposits(8)
    if not deps:
        await callback.message.edit_text(
            '<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> Hozirda kutilayotgan depozitlar yo\'q.', 
            reply_markup=admin_back_kb("deposits"),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    text_lines = [f'<tg-emoji emoji-id="6044796776462930061">⏳</tg-emoji> <b>Kutilayotgan to\'lovlar ({len(deps)} ta):</b>\n']
    for d in deps:
        did = d["id"]
        uid = d["user_id"]
        exact = d["exact_amount"]
        amount = d["amount"]
        text_lines.append(f"🆔 #{did} | User: <code>{uid}</code> | To'lov: <b>{exact:,.0f} so'm</b> ({amount:,.0f})")
        builder.row(InlineKeyboardButton(
            text=f"#{did} ni tasdiqlash ({exact:,.0f} so'm)", 
            callback_data=f"adm:confdep:{did}",
            icon_custom_emoji_id="6011046912078787676"
        ))

    builder.row(InlineKeyboardButton(
        text="Orqaga", 
        callback_data="adm:deposits",
        icon_custom_emoji_id="5307502033103915040"
    ))
    await callback.message.edit_text("\n".join(text_lines), reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:recent_deps", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_recent_deposits(callback: types.CallbackQuery):
    deps = get_recent_deposits(8)
    if not deps:
        await callback.message.edit_text("Hozircha depozitlar tarixi yo'q.", reply_markup=admin_back_kb("deposits"))
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    text_lines = ["📋 <b>So'nggi depozitlar tarixi:</b>\n"]
    for d in deps:
        did = d["id"]
        uid = d["user_id"]
        amount = d["amount"]
        st = d.get("status", "pending")
        icon = "✅" if st == "completed" else ("⏳" if st == "pending" else "❌")
        text_lines.append(f"{icon} #{did} | <code>{uid}</code> | <b>{amount:,.0f} so'm</b> ({st})")

    builder.row(InlineKeyboardButton(
        text="Orqaga", 
        callback_data="adm:deposits",
        icon_custom_emoji_id="5307502033103915040"
    ))
    await callback.message.edit_text("\n".join(text_lines), reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("adm:confdep:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_confirm_deposit(callback: types.CallbackQuery, bot: Bot):
    did = int(callback.data.split(":")[2])
    res = complete_deposit(did)
    if res:
        uid = res["user_id"]
        amount = res["amount"]
        new_bal = res.get("new_balance", 0.0)
        await callback.answer(f"✅ Depozit #{did} muvaffaqiyatli tasdiqlandi!", show_alert=True)
        try:
            await bot.send_message(
                chat_id=uid,
                text=(
                    f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Hisobingiz to\'ldirildi!</b>\n\n'
                    f'<tg-emoji emoji-id="5415594207068822547">💰</tg-emoji> <b>Summa:</b> <b>{amount:,.0f} so\'m</b>\n'
                    f'<tg-emoji emoji-id="6025976946083500432">💳</tg-emoji> <b>Yangi balansingiz:</b> <b>{new_bal:,.0f} so\'m</b>\n\n'
                    f'<i>Xizmatlarimizdan foydalanishingiz mumkin!</i>'
                ),
                parse_mode="HTML"
            )
        except Exception:
            pass
    else:
        await callback.answer("❌ Bu depozit allaqachon yakunlangan yoki topilmadi.", show_alert=True)
    await cb_pending_deposits(callback)


# ──────────────────────────────────────────
#  🌐 API BALANSLARI
# ──────────────────────────────────────────
@router.callback_query(F.data == "adm:api", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_api_balances(callback: types.CallbackQuery):
    loading_msg = await callback.message.edit_text("⏳ <i>API serverlaridan balanslar olinmoqda...</i>", parse_mode="HTML")
    
    # GrandSMM balansi
    smm_resp = await smm_api.get_balance()
    smm_bal_str = "Noma'lum"
    if isinstance(smm_resp, dict):
        if "balance" in smm_resp:
            curr = smm_resp.get("currency", "UZS")
            smm_bal_str = f"<b>{float(smm_resp['balance']):,.0f} {curr}</b>"
        elif "error" in smm_resp:
            smm_bal_str = f"❌ {smm_resp['error']}"

    # SMS API balansi
    num_resp = await number_api.get_balance()
    num_bal_str = "Noma'lum"
    if isinstance(num_resp, dict):
        if num_resp.get("success") and "balance" in num_resp:
            num_bal_str = f"<b>{float(num_resp['balance']):,.0f} UZS</b>"
        elif "balance" in num_resp:
            num_bal_str = f"<b>{float(num_resp['balance']):,.0f} UZS</b>"
        elif "error" in num_resp:
            num_bal_str = f"❌ {num_resp['error']}"

    text = (
        '<tg-emoji emoji-id="5409048419211682843">🌐</tg-emoji> <b>API Provayderlar Balansi</b>\n\n'
        f'🚀 <b>GrandSMM API:</b>\n'
        f' └ Balans: {smm_bal_str}\n\n'
        '<i>Eslatma: Agar API balansi tugab qolsa, foydalanuvchilar buyurtma bera olmaydi.</i>'
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Yangilash", 
            callback_data="adm:api",
            icon_custom_emoji_id="5895288113537748673"
        ),
        InlineKeyboardButton(
            text="Asosiy Panel", 
            callback_data="adm:main",
            icon_custom_emoji_id="5416113713428057601"
        ),
    )

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


# ──────────────────────────────────────────
#  ⭐ STARS NARXI SOZLAMASI
# ──────────────────────────────────────────
@router.callback_query(F.data == "adm:stars_price", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_stars_price_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    current_price = get_star_price()
    text = (
        '<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Telegram Stars Narxi Sozlamasi</b>\n\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>Joriy 1 dona Star narxi:</b> <b>{current_price:,.0f} so\'m</b>\n\n'
        '<i>Foydalanuvchilar Stars sotib olayotganda ushbu narx asosida hisob-kitob qilinadi.</i>\n\n'
        'Narxni o\'zgartirish uchun quyidagi tugmani bosing:'
    )
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Narxni O'zgartirish", 
            callback_data="adm:change_star_price",
            icon_custom_emoji_id="5370951118698339120"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="Asosiy Panel", 
            callback_data="adm:main",
            icon_custom_emoji_id="5416113713428057601"
        )
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:change_star_price", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_change_star_price_prompt(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.waiting_star_price)
    current_price = get_star_price()
    await callback.message.edit_text(
        f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Yangi Stars narxini belgilash</b>\n\n'
        f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> Joriy narx: <b>{current_price:,.0f} so\'m</b>\n\n'
        f'Yangi narxni so\'mda kiriting (masalan: <code>260</code> yoki <code>280</code>):\n',
        reply_markup=admin_back_kb("stars_price"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminState.waiting_star_price, F.from_user.func(lambda u: u.id in ADMINS))
async def process_star_price(message: types.Message, state: FSMContext):
    await state.clear()
    text = message.text.strip().replace(" ", "").replace(",", ".")
    try:
        new_price = float(text)
        if new_price <= 0:
            await message.answer("❌ Narx 0 dan katta bo'lishi kerak.", reply_markup=admin_back_kb("stars_price"))
            return
        set_star_price(new_price)
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="Stars Sozlamalari", 
                callback_data="adm:stars_price",
                icon_custom_emoji_id="5897792062291449826"
            ),
            InlineKeyboardButton(
                text="Asosiy Panel", 
                callback_data="adm:main",
                icon_custom_emoji_id="5416113713428057601"
            )
        )
        await message.answer(
            f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Telegram Stars narxi muvaffaqiyatli yangilandi!</b>\n\n'
            f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Yangi 1 dona Star narxi:</b> <b>{new_price:,.0f} so\'m</b>',
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer("❌ Noto'g'ri narx formati! Faqat raqam kiriting.", reply_markup=admin_back_kb("stars_price"))


# ──────────────────────────────────────────
#  📢 BUYURTMALAR KANALI SOZLAMASI
# ──────────────────────────────────────────
@router.callback_query(F.data == "adm:orders_channel", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_orders_channel_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    current_channel = get_orders_channel()
    channel_display = f"<code>{current_channel}</code>" if current_channel else "<i>O'rnatilmagan (O'chirilgan)</i>"

    text = (
        '<tg-emoji emoji-id="5206607081334906820">📢</tg-emoji> <b>Buyurtmalar Kanali Sozlamasi</b>\n\n'
        f'<tg-emoji emoji-id="5456432998092133477">📡</tg-emoji> <b>Joriy hisobot kanali:</b> {channel_display}\n\n'
        "<i>Barcha yangi buyurtmalar (SMM, Stars, Virtual Raqam) va ularning natijalari avtomatik ravishda ushbu kanalga premium emojilar bilan yuboriladi.</i>\n\n"
        "<b>⚠️ Muhim shart:</b> Bot ushbu kanalda <b>Administrator</b> bo'lishi va xabar yuborish huquqiga ega bo'lishi kerak!"
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Kanalni Belgilash / O'zgartirish", 
            callback_data="adm:set_orders_channel",
            icon_custom_emoji_id="5370951118698339120"
        ),
    )
    if current_channel:
        builder.row(
            InlineKeyboardButton(
                text=" Xabar Yuborish", 
                callback_data="adm:test_orders_channel",
                icon_custom_emoji_id="5895288113537748673"
            ),
            InlineKeyboardButton(
                text="Kanalni O'chirish", 
                callback_data="adm:clear_orders_channel",
                icon_custom_emoji_id="6028346797368283073"
            ),
        )
    builder.row(
        InlineKeyboardButton(
            text="Asosiy Panel", 
            callback_data="adm:main",
            icon_custom_emoji_id="5416113713428057601"
        )
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm:set_orders_channel", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_set_orders_channel_prompt(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.waiting_orders_channel)
    current_channel = get_orders_channel()
    channel_display = f"<code>{current_channel}</code>" if current_channel else "<i>O'rnatilmagan</i>"

    await callback.message.edit_text(
        f'<tg-emoji emoji-id="5206607081334906820">📢</tg-emoji> <b>Buyurtmalar Kanalini Belgilash</b>\n\n'
        f'Joriy kanal: {channel_display}\n\n'
        f"Kanal username'ini (masalan: <code>@mening_kanalim</code>) yoki kanal ID'sini (masalan: <code>-1001234567890</code>) yuboring:\n\n"
        f"<i>⚠️ Avval botni o'sha kanalga <b>Admin</b> qilib qo'shganingizga ishonch hosil qiling!</i>",
        reply_markup=admin_back_kb("orders_channel"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminState.waiting_orders_channel, F.from_user.func(lambda u: u.id in ADMINS))
async def process_orders_channel(message: types.Message, state: FSMContext):
    raw_input = message.text.strip()

    # Format tekshirish
    if not (raw_input.startswith("@") or raw_input.startswith("-100") or (raw_input.startswith("-") and raw_input[1:].isdigit())):
        if not raw_input.startswith("@"):
            raw_input = f"@{raw_input}"

    # Botning ushbu kanalda admin ekanligini tekshirish
    try:
        from datetime import datetime
        import html
        from order_checker import get_bot_username

        chat_info = await message.bot.get_chat(raw_input)
        
        time_now = datetime.now().strftime("%d.%m.%Y %H:%M")
        test_user = message.from_user
        user_name = html.escape(test_user.full_name)
        if test_user.username:
            user_link = f'<a href="https://t.me/{test_user.username}">{user_name}</a>'
        else:
            user_link = f'<a href="tg://user?id={test_user.id}">{user_name}</a>'
        user_id = test_user.id
        order_id = 7777777
        stars_amount = 100
        target_user = f"@{test_user.username}" if test_user.username else f"ID: {test_user.id}"
        price = 23000

        # Inline tugma
        bot_uname = await get_bot_username(message.bot)
        test_kb = InlineKeyboardBuilder()
        test_kb.row(
            InlineKeyboardButton(
                text="🔍 Buyurtma holati",
                callback_data=f"chk_ord:{order_id}",
                icon_custom_emoji_id="5936143551854285132"
            )
        )
        if bot_uname:
            test_kb.row(
                InlineKeyboardButton(
                    text="🚀 Bot orqali buyurtma berish",
                    url=f"https://t.me/{bot_uname}",
                    icon_custom_emoji_id="5456432998092133477"
                )
            )


        # Test xabari yuborib ko'ramiz
        await message.bot.send_message(
            chat_id=chat_info.id,
            text=(
                f'<tg-emoji emoji-id="5879939498149679716">⭐</tg-emoji> <b>YANGI BUYURTMA — TELEGRAM STARS</b>\n'
                f'━━━━━━━━━━━━━━━━━━━━\n'
                f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{order_id}</code>\n'
                f'<tg-emoji emoji-id="6032609071373226027">👤</tg-emoji> <b>Buyurtmachi:</b> {user_link}\n'
                f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Miqdori:</b> <b>{stars_amount:,} Stars</b>\n'
                f'<tg-emoji emoji-id="5201989772448381592">🎯</tg-emoji> <b>Qabul qiluvchi:</b> <code>{target_user}</code>\n'
                f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>To\'lov summasi:</b> <b>{price:,.0f} so\'m</b>\n'
                f'<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> <b>Holat:</b> <b>Kutilmoqda</b>\n'
                f'<tg-emoji emoji-id="5849724424957851226">📅</tg-emoji> <b>Sana:</b> <code>{time_now}</code>\n'
                f'━━━━━━━━━━━━━━━━━━━━\n'
                f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <i>Tezkor Telegram Stars xizmati</i>'
            ),
            reply_markup=test_kb.as_markup(),
            parse_mode="HTML"
        )

        # O'rnatamiz
        saved_val = str(f"@{chat_info.username}" if chat_info.username else chat_info.id)
        set_orders_channel(saved_val)
        await state.clear()

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="Kanal Sozlamalari", 
                callback_data="adm:orders_channel",
                icon_custom_emoji_id="5206607081334906820"
            ),
            InlineKeyboardButton(
                text="Asosiy Panel", 
                callback_data="adm:main",
                icon_custom_emoji_id="5416113713428057601"
            )
        )
        await message.answer(
            f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Buyurtmalar kanali muvaffaqiyatli o\'rnatildi!</b>\n\n'
            f'<tg-emoji emoji-id="5206607081334906820">📢</tg-emoji> <b>Kanal:</b> <b>{chat_info.title}</b> (<code>{saved_val}</code>)\n'
            f'<i>Kanalga tasdiqlovchi test xabari yuborildi.</i>',
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(
            f'<tg-emoji emoji-id="6028346797368283073">❌</tg-emoji> <b>Kanalga ulanib bo\'lmadi!</b>\n\n'
            f'<b>Xatolik:</b> <i>{e}</i>\n\n'
            f'<b>Sabablar:</b>\n'
            f'1. Bot kanalga a\'zo qilinmagan yoki <b>Admin</b> huquqi berilmagan.\n'
            f'2. Kanal username yoki ID xato kiritilgan.\n\n'
            f'Iltimos, tekshirib qaytadan kiriting:',
            reply_markup=admin_back_kb("orders_channel"),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "adm:clear_orders_channel", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_clear_orders_channel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    set_orders_channel("")
    await callback.answer("✅ Buyurtmalar kanali o'chirildi!", show_alert=True)
    await cb_orders_channel_menu(callback, state)


@router.callback_query(F.data == "adm:test_orders_channel", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_test_orders_channel(callback: types.CallbackQuery):
    channel = get_orders_channel()
    if not channel:
        await callback.answer("❌ Kanal o'rnatilmagan!", show_alert=True)
        return

    try:
        from datetime import datetime
        import html
        from order_checker import get_bot_username

        time_now = datetime.now().strftime("%d.%m.%Y %H:%M")
        test_user = callback.from_user
        user_name = html.escape(test_user.full_name)
        if test_user.username:
            user_link = f'<a href="https://t.me/{test_user.username}">{user_name}</a>'
        else:
            user_link = f'<a href="tg://user?id={test_user.id}">{user_name}</a>'
        user_id = test_user.id
        order_id = 7777777
        stars_amount = 100
        target_user = f"@{test_user.username}" if test_user.username else f"ID: {test_user.id}"
        price = 23000

        text = (
            f'<tg-emoji emoji-id="5879939498149679716">⭐</tg-emoji> <b>YANGI BUYURTMA — TELEGRAM STARS</b>\n'
            f'━━━━━━━━━━━━━━━━━━━━\n'
            f'<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji> <b>Buyurtma ID:</b> <code>#{order_id}</code>\n'
            f'<tg-emoji emoji-id="6032609071373226027">👤</tg-emoji> <b>Buyurtmachi:</b> {user_link}\n'
            f'<tg-emoji emoji-id="5897792062291449826">⭐</tg-emoji> <b>Miqdori:</b> <b>{stars_amount:,} Stars</b>\n'
            f'<tg-emoji emoji-id="5201989772448381592">🎯</tg-emoji> <b>Qabul qiluvchi:</b> <code>{target_user}</code>\n'
            f'<tg-emoji emoji-id="5379872186678914958">💰</tg-emoji> <b>To\'lov summasi:</b> <b>{price:,.0f} so\'m</b>\n'
            f'<tg-emoji emoji-id="5339517416995039810">⏳</tg-emoji> <b>Holat:</b> <b>Kutilmoqda</b>\n'
            f'<tg-emoji emoji-id="5849724424957851226">📅</tg-emoji> <b>Sana:</b> <code>{time_now}</code>\n'
            f'━━━━━━━━━━━━━━━━━━━━\n'
            f'<tg-emoji emoji-id="5251203410396458957">🌟</tg-emoji> <i>Tezkor Telegram Stars xizmati</i>'
        )


        bot_uname = await get_bot_username(callback.bot)
        test_kb = InlineKeyboardBuilder()
        test_kb.row(
            InlineKeyboardButton(
                text="🔍 Buyurtma holati",
                callback_data=f"chk_ord:{order_id}",
                icon_custom_emoji_id="5936143551854285132"
            )
        )
        if bot_uname:
            test_kb.row(
                InlineKeyboardButton(
                    text="🚀 Bot orqali buyurtma berish",
                    url=f"https://t.me/{bot_uname}",
                    icon_custom_emoji_id="5456432998092133477"
                )
            )


        await callback.bot.send_message(
            chat_id=channel,
            text=text,
            parse_mode="HTML",
            reply_markup=test_kb.as_markup()
        )
        await callback.answer("✅ Kanalga test xabari muvaffaqiyatli yuborildi!", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Xatolik yuz berdi: {e}", show_alert=True)


# ──────────────────────────────────────────
#  📢 MAJBURIY OBUNA (HOMIY KANALLAR)
# ──────────────────────────────────────────
@router.callback_query(F.data == "adm:mandatory_channels", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_mandatory_channels_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    channels = get_mandatory_channels()

    if not channels:
        ch_text = "<i>Hozircha majburiy obuna kanallari belgilanmagan (Majburiy obuna o'chiq).</i>\n"
    else:
        ch_text = "<b>📋 Ulangan homiy kanallar:</b>\n"
        for i, ch in enumerate(channels, 1):
            ch_text += (
                f"\n<b>{i}. {ch['title']}</b>\n"
                f" ├ <b>ID / User:</b> <code>{ch['channel_id']}</code>\n"
                f" └ <b>Havola:</b> <a href=\"{ch['url']}\">{ch['url']}</a>\n"
            )

    text = (
        f'<tg-emoji emoji-id="5206607081334906820">📢</tg-emoji> <b>Majburiy Obuna (Homiy Kanallar) Boshqaruvi</b>\n\n'
        f'<i>Foydalanuvchilar bot xizmatlaridan foydalanishi uchun quyidagi kanallarga a\'zo bo\'lishi shart qilinadi.</i>\n\n'
        f'📊 <b>Jami kanallar:</b> <b>{len(channels)} ta</b>\n\n'
        f'{ch_text}\n'
        f'⚠️ <b>Eslatma:</b> Bot ushbu kanallarda <b>Administrator</b> bo\'lishi shart!'
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="➕ Kanal Qo'shish",
            callback_data="adm:add_mandatory_channel",
            icon_custom_emoji_id="5370951118698339120"
        ),
    )
    if channels:
        builder.row(
            InlineKeyboardButton(
                text="➖ Kanal O'chirish",
                callback_data="adm:del_mchannel_menu",
                icon_custom_emoji_id="6028346797368283073"
            ),
            InlineKeyboardButton(
                text="🔄 Holatni Tekshirish",
                callback_data="adm:test_mandatory_channels",
                icon_custom_emoji_id="5895288113537748673"
            ),
        )
    builder.row(
        InlineKeyboardButton(
            text="Asosiy Panel",
            callback_data="adm:main",
            icon_custom_emoji_id="5416113713428057601"
        )
    )

    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer()


@router.callback_query(F.data == "adm:add_mandatory_channel", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_add_mandatory_channel_prompt(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.waiting_mandatory_channel)
    text = (
        f'<tg-emoji emoji-id="5206607081334906820">➕</tg-emoji> <b>Yangi Majburiy Kanal Qo\'shish</b>\n\n'
        f'Kanal qo\'shish uchun quyidagi usullardan birini tanlang:\n\n'
        f'1️⃣ Kanal username\'ini yuboring (masalan: <code>@mening_kanalim</code>)\n'
        f'2️⃣ Kanal ID\'sini yuboring (masalan: <code>-1001234567890</code>)\n'
        f'3️⃣ Kanaldan biror xabarni botga <b>Forward (uzatish)</b> qiling\n\n'
        f'⚠️ <b>MUHIM SHART:</b>\n'
        f'Avval botni o\'sha kanalga <b>Administrator</b> qilib qo\'shing va '
        f'<i>"A\'zolarni ko\'rish / Taklif havolalari yaratish"</i> huquqlarini bering!\n\n'
    )
    await callback.message.edit_text(text, reply_markup=admin_back_kb("mandatory_channels"), parse_mode="HTML")
    await callback.answer()


@router.message(AdminState.waiting_mandatory_channel, F.from_user.func(lambda u: u.id in ADMINS))
async def process_add_mandatory_channel(message: types.Message, state: FSMContext):
    target_chat = None

    # 1. Forward qilingan postdan olish
    if message.forward_from_chat:
        target_chat = message.forward_from_chat.id
    elif message.text:
        raw = message.text.strip()
        # https://t.me/username yoki https://t.me/+invite
        if "t.me/" in raw:
            part = raw.split("t.me/")[1].split("/")[0].split("?")[0].strip()
            if not part.startswith("+") and not part.startswith("joinchat"):
                target_chat = f"@{part}"
            else:
                target_chat = raw
        elif (raw.startswith("-100") and raw[1:].isdigit()) or (raw.startswith("-") and raw[1:].isdigit()) or raw.isdigit():
            target_chat = int(raw)
        elif raw.startswith("@"):
            target_chat = raw
        else:
            target_chat = f"@{raw}"
    else:
        await message.answer(
            "❌ Iltimos, kanal username'i (@kanal), ID'si yoki kanaldan forward qilingan xabar yuboring.",
            reply_markup=admin_back_kb("mandatory_channels")
        )
        return

    # Botning kanalga ulanishi va adminligini tekshirish
    try:
        bot_user = await message.bot.get_me()
        chat_info = await message.bot.get_chat(target_chat)

        # Adminlik huquqini tekshiramiz
        try:
            bot_member = await message.bot.get_chat_member(chat_info.id, bot_user.id)
            if bot_member.status not in ("administrator", "creator"):
                await message.answer(
                    f'<tg-emoji emoji-id="6028346797368283073">❌</tg-emoji> <b>Bot ushbu kanalda Administrator emas!</b>\n\n'
                    f'📢 <b>Kanal:</b> <b>{chat_info.title}</b> (<code>{chat_info.id}</code>)\n\n'
                    f'Foydalanuvchilar obunasini tekshirish uchun bot kanalga <b>Admin</b> qilib tayinlanishi shart.\n'
                    f'Iltimos, botni kanalga admin qilib, qaytadan yuboring:',
                    reply_markup=admin_back_kb("mandatory_channels"),
                    parse_mode="HTML"
                )
                return
        except Exception as perm_err:
            logger.warning(f"get_chat_member xatosi: {perm_err}")

        # Havola yaratish yoki olish
        if chat_info.username:
            url = f"https://t.me/{chat_info.username}"
            channel_identifier = f"@{chat_info.username}"
        else:
            channel_identifier = str(chat_info.id)
            url = getattr(chat_info, "invite_link", None)
            if not url:
                try:
                    invite = await message.bot.create_chat_invite_link(
                        chat_id=chat_info.id,
                        name="SMM Bot Majburiy Obuna"
                    )
                    url = invite.invite_link
                except Exception as inv_err:
                    logger.warning(f"Invite link yaratishda xato: {inv_err}")
                    url = f"https://t.me/c/{str(chat_info.id).replace('-100', '')}/1"

        # Bazaga saqlaymiz
        success = add_mandatory_channel(
            channel_id=channel_identifier,
            title=chat_info.title,
            url=url
        )
        await state.clear()

        if success:
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="Yana kanal qo'shish",
                    callback_data="adm:add_mandatory_channel",
                    icon_custom_emoji_id="5370951118698339120"
                ),
                InlineKeyboardButton(
                    text="Kanallar ro'yxati",
                    callback_data="adm:mandatory_channels",
                    icon_custom_emoji_id="5206607081334906820"
                ),
            )
            builder.row(
                InlineKeyboardButton(
                    text="Asosiy Panel",
                    callback_data="adm:main",
                    icon_custom_emoji_id="5416113713428057601"
                )
            )

            await message.answer(
                f'<tg-emoji emoji-id="6026257381678124710">✅</tg-emoji> <b>Majburiy kanal muvaffaqiyatli qo\'shildi!</b>\n\n'
                f'📢 <b>Kanal nomi:</b> <b>{chat_info.title}</b>\n'
                f'🆔 <b>ID / Username:</b> <code>{channel_identifier}</code>\n'
                f'🔗 <b>Havola:</b> <a href="{url}">{url}</a>\n'
                f'🤖 <b>Bot holati:</b> Administrator ✅\n\n'
                f'<i>Endi barcha oddiy foydalanuvchilar ushbu kanalga a\'zo bo\'lmaguncha botdan foydalana olmaydi.</i>',
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        else:
            await message.answer(
                "❌ Kanalni bazaga saqlashda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
                reply_markup=admin_back_kb("mandatory_channels")
            )

    except Exception as e:
        logger.error(f"process_add_mandatory_channel xatosi: {e}")
        await message.answer(
            f'<tg-emoji emoji-id="6028346797368283073">❌</tg-emoji> <b>Kanalga ulanib bo\'lmadi!</b>\n\n'
            f'<b>Xatolik:</b> <i>{e}</i>\n\n'
            f'<b>Mumkin bo\'lgan sabablar:</b>\n'
            f'1. Bot kanalga qo\'shilmagan yoki <b>Admin</b> qilinmagan.\n'
            f'2. Kanal username yoki ID xato kiritilgan.\n\n'
            f'Iltimos, tekshirib qaytadan yuboring:',
            reply_markup=admin_back_kb("mandatory_channels"),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "adm:del_mchannel_menu", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_del_mchannel_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    channels = get_mandatory_channels()

    if not channels:
        await callback.answer("❌ O'chirish uchun kanallar mavjud emas!", show_alert=True)
        await cb_mandatory_channels_menu(callback, state)
        return

    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.row(
            InlineKeyboardButton(
                text=f"🗑 {ch['title']}",
                callback_data=f"adm:del_mch:{ch['id']}",
                icon_custom_emoji_id="6028346797368283073"
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="adm:mandatory_channels",
            icon_custom_emoji_id="5307502033103915040"
        )
    )

    text = (
        f'<tg-emoji emoji-id="6028346797368283073">🗑</tg-emoji> <b>Majburiy Kanalni O\'chirish</b>\n\n'
        f'O\'chirmoqchi bo\'lgan kanalingiz ustiga bosing:'
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("adm:del_mch:"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_del_mchannel_action(callback: types.CallbackQuery, state: FSMContext):
    try:
        ch_id = int(callback.data.split("adm:del_mch:")[1])
        ch = get_mandatory_channel_by_id(ch_id)
        deleted = delete_mandatory_channel(ch_id)

        if deleted:
            ch_name = ch['title'] if ch else "Kanal"
            await callback.answer(f"✅ '{ch_name}' majburiy obunadan o'chirildi!", show_alert=True)
        else:
            await callback.answer("❌ Kanal topilmadi yoki allaqachon o'chirilgan!", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Xatolik: {e}", show_alert=True)

    await cb_mandatory_channels_menu(callback, state)


@router.callback_query(F.data == "adm:test_mandatory_channels", F.from_user.func(lambda u: u.id in ADMINS))
async def cb_test_mandatory_channels(callback: types.CallbackQuery):
    channels = get_mandatory_channels()
    if not channels:
        await callback.answer("❌ Kanallar mavjud emas!", show_alert=True)
        return

    await callback.answer("🔄 Kanallar tekshirilmoqda...", show_alert=False)

    report_lines = []
    bot_user = await callback.bot.get_me()

    for i, ch in enumerate(channels, 1):
        target = str(ch.get("channel_id", "")).strip()
        try:
            if (target.startswith("-") and target[1:].isdigit()) or target.isdigit():
                chat_target = int(target)
            else:
                chat_target = target if target.startswith("@") else f"@{target}"

            chat_info = await callback.bot.get_chat(chat_target)
            bot_member = await callback.bot.get_chat_member(chat_info.id, bot_user.id)

            if bot_member.status in ("administrator", "creator"):
                status_icon = "🟢"
                status_text = "<b>Faol (Admin ✅)</b>"
            else:
                status_icon = "🟡"
                status_text = "<b>Admin huquqi yo'q ⚠️</b>"

            report_lines.append(
                f"{status_icon} <b>{i}. {chat_info.title}</b>\n"
                f" ├ <b>ID / Username:</b> <code>{target}</code>\n"
                f" └ <b>Holat:</b> {status_text}"
            )
        except Exception as e:
            report_lines.append(
                f"🔴 <b>{i}. {ch['title']}</b>\n"
                f" ├ <b>ID / Username:</b> <code>{target}</code>\n"
                f" └ <b>Holat:</b> <i>Xatolik: {e}</i> ❌"
            )

    report_text = (
        f'<tg-emoji emoji-id="5895288113537748673">🔄</tg-emoji> <b>Majburiy Kanallar Holati:</b>\n\n'
        + "\n\n".join(report_lines)
    )

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🔄 Qayta tekshirish",
            callback_data="adm:test_mandatory_channels",
            icon_custom_emoji_id="5895288113537748673"
        ),
        InlineKeyboardButton(
            text="📢 Kanallar menyusi",
            callback_data="adm:mandatory_channels",
            icon_custom_emoji_id="5206607081334906820"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Asosiy Panel",
            callback_data="adm:main",
            icon_custom_emoji_id="5416113713428057601"
        )
    )

    try:
        await callback.message.edit_text(report_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception:
        pass


# ──────────────────────────────────────────
#  📢 BROADCAST (OMMAVIY XABAR)
# ──────────────────────────────────────────
@router.callback_query(F.data == "adm:broadcast", F.from_user.func(lambda u: u.id in ADMINS))
@router.message(Command("broadcast"), F.from_user.func(lambda u: u.id in ADMINS))
async def cb_start_broadcast(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.waiting_broadcast_content)
    text = (
        '<tg-emoji emoji-id="4992560350982309130">📢</tg-emoji> <b>Ommaviy Xabar (Broadcast)</b>\n\n'
        'Barcha faol foydalanuvchilarga yuboriladigan xabarni jo\'nating.\n'
        '<i>(Matn, Rasm, Video yoki Fayl ko\'rinishida yuborishingiz mumkin)</i>\n\n'
    )
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=admin_back_kb("main"), parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=admin_back_kb("main"), parse_mode="HTML")


@router.message(AdminState.waiting_broadcast_content, F.from_user.func(lambda u: u.id in ADMINS))
async def process_broadcast_content(message: types.Message, state: FSMContext):
    # Xabarni keyingi bosqich uchun saqlaymiz
    await state.update_data(
        broadcast_msg_id=message.message_id,
        broadcast_chat_id=message.chat.id,
    )
    await state.set_state(AdminState.confirm_broadcast)

    users = get_all_users(only_active=True)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚀 Yuborishni Boshlash", callback_data="adm:bcast_send"),
    )
    builder.row(
        InlineKeyboardButton(text="🔘 URL Tugma Qo'shish", callback_data="adm:bcast_add_btn"),
    )
    builder.row(
        InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="adm:main"),
    )

    await message.answer(
        f"📢 <b>Broadcast Tayyor!</b>\n\n"
        f"👥 Qabul qiluvchilar soni: <b>{len(users):,} ta</b>\n\n"
        f"Xabarni tekshiring va quyidagi tugmalardan birini bosing:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "adm:bcast_add_btn", AdminState.confirm_broadcast, F.from_user.func(lambda u: u.id in ADMINS))
async def cb_bcast_add_btn_prompt(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.waiting_broadcast_button)
    await callback.message.edit_text(
        "🔘 <b>Tugma qo'shish</b>\n\n"
        "Tugma matni va havolani quyidagi formatda yuboring:\n"
        "<code>Tugma Matni | https://t.me/kanal_linki</code>\n\n",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminState.waiting_broadcast_button, F.from_user.func(lambda u: u.id in ADMINS))
async def process_bcast_button(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if "|" not in text:
        await message.answer("❌ Noto'g'ri format! Masalan: <code>Kanalimiz | https://t.me/...</code>")
        return
    btn_text, btn_url = [p.strip() for p in text.split("|", 1)]
    if not (btn_url.startswith("http://") or btn_url.startswith("https://") or btn_url.startswith("tg://")):
        await message.answer("❌ Havola http:// yoki https:// bilan boshlanishi kerak!")
        return

    await state.update_data(btn_text=btn_text, btn_url=btn_url)
    await state.set_state(AdminState.confirm_broadcast)

    users = get_all_users(only_active=True)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚀 Yuborishni Boshlash", callback_data="adm:bcast_send"),
    )
    builder.row(
        InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="adm:main"),
    )

    await message.answer(
        f"✅ <b>Tugma biriktirildi:</b> [{btn_text}]({btn_url})\n\n"
        f"👥 Qabul qiluvchilar: <b>{len(users):,} ta</b>\n"
        f"Yuborishni tasdiqlaysizmi?",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "adm:bcast_send", AdminState.confirm_broadcast, F.from_user.func(lambda u: u.id in ADMINS))
async def execute_broadcast(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_id = data.get("broadcast_msg_id")
    from_chat_id = data.get("broadcast_chat_id")
    btn_text = data.get("btn_text")
    btn_url = data.get("btn_url")
    await state.clear()

    users = get_all_users(only_active=True)
    total = len(users)
    if total == 0:
        await callback.message.edit_text("❌ Foydalanuvchilar mavjud emas.", reply_markup=admin_back_kb("main"))
        await callback.answer()
        return

    reply_markup = None
    if btn_text and btn_url:
        b_builder = InlineKeyboardBuilder()
        b_builder.row(InlineKeyboardButton(text=btn_text, url=btn_url))
        reply_markup = b_builder.as_markup()

    status_msg = await callback.message.edit_text(f"🚀 <b>Ommaviy xabar yuborilmoqda...</b>\n0/{total}", parse_mode="HTML")
    await callback.answer()

    success, failed = 0, 0
    for i, uid in enumerate(users, 1):
        try:
            await bot.copy_message(
                chat_id=uid,
                from_chat_id=from_chat_id,
                message_id=msg_id,
                reply_markup=reply_markup
            )
            success += 1
        except Exception:
            failed += 1

        if i % 25 == 0 or i == total:
            try:
                pct = round((i / total) * 100)
                await status_msg.edit_text(
                    f"🚀 <b>Ommaviy xabar yuborilmoqda:</b> {pct}%\n\n"
                    f"📨 Yuborildi: <b>{success}</b>\n"
                    f"❌ Xatolik: <b>{failed}</b>\n"
                    f"👥 Jami: <b>{total}</b>",
                    parse_mode="HTML"
                )
            except Exception:
                pass

        await asyncio.sleep(0.04)

    await status_msg.edit_text(
        f"✅ <b>Ommaviy xabar muvaffaqiyatli yakunlandi!</b>\n\n"
        f"📨 Yetkazildi: <b>{success:,} ta</b>\n"
        f"❌ Yetkazilmadi (bloklaganlar): <b>{failed:,} ta</b>\n"
        f"👥 Jami a'zolar: <b>{total:,} ta</b>",
        reply_markup=admin_back_kb("main"),
        parse_mode="HTML"
    )

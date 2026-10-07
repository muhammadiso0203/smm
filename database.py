import sqlite3
import logging
from config import DATABASE

logger = logging.getLogger(__name__)


def get_connection():
    """Ma'lumotlar bazasiga ulanish"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Jadvallarni yaratish"""
    conn = get_connection()
    cursor = conn.cursor()

    # Foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY,
            user_id     INTEGER UNIQUE NOT NULL,
            username    TEXT,
            full_name   TEXT,
            phone       TEXT,
            balance     REAL DEFAULT 0,
            is_admin    INTEGER DEFAULT 0,
            is_banned   INTEGER DEFAULT 0,
            joined_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Mavjud bazalar uchun balance ustuni qo'shish
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # Xabarlar tarixi jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            message     TEXT,
            sent_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # To'lovlar (Hisob to'ldirish) jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            amount          INTEGER NOT NULL,
            exact_amount    INTEGER NOT NULL,
            status          TEXT DEFAULT 'pending',
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at      TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # Buyurtmalar jadvali (Statusni avtomatik kuzatish uchun)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id        INTEGER UNIQUE NOT NULL,
            user_id         INTEGER NOT NULL,
            service_id      INTEGER NOT NULL,
            service_title   TEXT,
            quantity        INTEGER NOT NULL,
            price           REAL NOT NULL,
            status          TEXT DEFAULT 'Pending',
            link            TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN link TEXT")
    except sqlite3.OperationalError:
        pass

    # Virtual Raqamlar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS virtual_numbers (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            server          INTEGER NOT NULL,
            country         TEXT NOT NULL,
            number          TEXT NOT NULL,
            hash_code       TEXT,
            price           REAL NOT NULL,
            sms_code        TEXT,
            status          TEXT DEFAULT 'waiting',
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # Statistika jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        DATE UNIQUE DEFAULT (date('now')),
            new_users   INTEGER DEFAULT 0,
            messages    INTEGER DEFAULT 0
        )
    """)

    # Bot sozlamalari (Stars narxi va boshqalar)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Majburiy obuna kanallari jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mandatory_channels (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id      TEXT UNIQUE NOT NULL,
            title           TEXT NOT NULL,
            url             TEXT NOT NULL,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    logger.info("✅ Ma'lumotlar bazasi tayyor")


# ──────────────────────────────────────────
#  Sozlamalar (Settings) funksiyalari
# ──────────────────────────────────────────

def get_setting(key: str, default: str = "") -> str:
    """Sozlama qiymatini olish"""
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return str(row["value"]) if row else default


def set_setting(key: str, value: str):
    """Sozlama qiymatini saqlash yoki yangilash"""
    conn = get_connection()
    conn.execute("""
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, str(value)))
    conn.commit()
    conn.close()


def get_star_price() -> float:
    """1 dona Telegram Star narxini olish (so'mda)"""
    from config import STAR_PRICE_UZS
    val = get_setting("star_price", str(STAR_PRICE_UZS))
    try:
        return float(val)
    except (ValueError, TypeError):
        return float(STAR_PRICE_UZS)


def set_star_price(price: float) -> float:
    """1 dona Telegram Star narxini belgilash"""
    set_setting("star_price", str(price))
    return float(price)


def get_orders_channel() -> str:
    """Buyurtmalar hisoboti yuboriladigan kanal (username yoki ID) ni olish"""
    return get_setting("orders_channel", "").strip()


def set_orders_channel(channel: str) -> str:
    """Buyurtmalar hisoboti yuboriladigan kanalni belgilash"""
    val = str(channel).strip()
    set_setting("orders_channel", val)
    return val



# ──────────────────────────────────────────
#  Foydalanuvchi funksiyalari
# ──────────────────────────────────────────

def add_user(user_id: int, username: str = None, full_name: str = None) -> bool:
    """Yangi foydalanuvchi qo'shish yoki mavjud foydalanuvchi ma'lumotlarini yangilash"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        existing = cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if existing:
            cursor.execute("""
                UPDATE users 
                SET username = COALESCE(?, username), 
                    full_name = COALESCE(?, full_name), 
                    last_seen = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            """, (username, full_name, user_id))
            conn.commit()
            return False
        else:
            cursor.execute("""
                INSERT INTO users (user_id, username, full_name, joined_at, last_seen)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (user_id, username, full_name))
            cursor.execute("""
                INSERT INTO stats (date, new_users) VALUES (date('now'), 1)
                ON CONFLICT(date) DO UPDATE SET new_users = new_users + 1
            """)
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"add_user xatosi: {e}")
        return False
    finally:
        conn.close()


def update_last_seen(user_id: int):
    """Oxirgi faollik vaqtini yangilash"""
    conn = get_connection()
    conn.execute("UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_user(user_id: int):
    """Foydalanuvchi ma'lumotlarini olish (vaqtlari mahalliy vaqtga moslangan holda)"""
    conn = get_connection()
    user = conn.execute("""
        SELECT id, user_id, username, full_name, phone, balance, is_admin, is_banned,
               datetime(joined_at, 'localtime') as joined_at,
               datetime(last_seen, 'localtime') as last_seen
        FROM users WHERE user_id = ?
    """, (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None


def get_all_users(only_active: bool = False):
    """Barcha foydalanuvchilarni olish"""
    conn = get_connection()
    if only_active:
        users = conn.execute("SELECT user_id FROM users WHERE is_banned = 0").fetchall()
    else:
        users = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    return [u["user_id"] for u in users]


def ban_user(user_id: int):
    conn = get_connection()
    conn.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def unban_user(user_id: int):
    conn = get_connection()
    conn.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def is_banned(user_id: int) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return bool(row and row["is_banned"])


def get_stats():
    """Umumiy statistikani olish"""
    conn = get_connection()
    total   = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    banned  = conn.execute("SELECT COUNT(*) as c FROM users WHERE is_banned = 1").fetchone()["c"]
    today_row = conn.execute(
        "SELECT COUNT(*) as c FROM users WHERE date(joined_at, 'localtime') = date('now', 'localtime')"
    ).fetchone()
    conn.close()
    return {
        "total":    total,
        "banned":   banned,
        "today":    today_row["c"] if today_row else 0,
    }


def get_admin_full_stats() -> dict:
    """Admin uchun kengaytirilgan to'liq moliyaviy va operatsion statistika"""
    conn = get_connection()
    
    # 👥 Foydalanuvchilar
    total_users = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    banned_users = conn.execute("SELECT COUNT(*) as c FROM users WHERE is_banned = 1").fetchone()["c"]
    today_users_row = conn.execute("SELECT COUNT(*) as c FROM users WHERE date(joined_at, 'localtime') = date('now', 'localtime')").fetchone()
    today_users = today_users_row["c"] if today_users_row else 0
    
    # 💰 Balanslar
    bal_row = conn.execute("SELECT COALESCE(SUM(balance), 0) as s FROM users").fetchone()
    total_user_balance = float(bal_row["s"]) if bal_row else 0.0
    
    # 📦 SMM Buyurtmalar (service_id != 9999)
    smm_total = conn.execute("SELECT COUNT(*) as c FROM orders WHERE service_id != 9999").fetchone()["c"]
    smm_today = conn.execute("SELECT COUNT(*) as c FROM orders WHERE service_id != 9999 AND date(created_at, 'localtime') = date('now', 'localtime')").fetchone()["c"]
    smm_sum_row = conn.execute("SELECT COALESCE(SUM(price), 0) as s FROM orders WHERE service_id != 9999 AND status NOT IN ('Canceled', 'Cancelled', 'Bekor qilindi', 'Canceled/Refunded')").fetchone()
    smm_total_sum = float(smm_sum_row["s"]) if smm_sum_row else 0.0
    smm_today_sum_row = conn.execute("SELECT COALESCE(SUM(price), 0) as s FROM orders WHERE service_id != 9999 AND status NOT IN ('Canceled', 'Cancelled', 'Bekor qilindi', 'Canceled/Refunded') AND date(created_at, 'localtime') = date('now', 'localtime')").fetchone()
    smm_today_sum = float(smm_today_sum_row["s"]) if smm_today_sum_row else 0.0

    # ⭐ Telegram Stars Buyurtmalar (service_id = 9999)
    stars_total = conn.execute("SELECT COUNT(*) as c FROM orders WHERE service_id = 9999").fetchone()["c"]
    stars_today = conn.execute("SELECT COUNT(*) as c FROM orders WHERE service_id = 9999 AND date(created_at, 'localtime') = date('now', 'localtime')").fetchone()["c"]
    stars_sum_row = conn.execute("SELECT COALESCE(SUM(price), 0) as s FROM orders WHERE service_id = 9999 AND status NOT IN ('Canceled', 'Cancelled', 'Bekor qilindi', 'Canceled/Refunded')").fetchone()
    stars_total_sum = float(stars_sum_row["s"]) if stars_sum_row else 0.0
    stars_today_sum_row = conn.execute("SELECT COALESCE(SUM(price), 0) as s FROM orders WHERE service_id = 9999 AND status NOT IN ('Canceled', 'Cancelled', 'Bekor qilindi', 'Canceled/Refunded') AND date(created_at, 'localtime') = date('now', 'localtime')").fetchone()
    stars_today_sum = float(stars_today_sum_row["s"]) if stars_today_sum_row else 0.0
    stars_qty_row = conn.execute("SELECT COALESCE(SUM(quantity), 0) as q FROM orders WHERE service_id = 9999 AND status NOT IN ('Canceled', 'Cancelled', 'Bekor qilindi', 'Canceled/Refunded')").fetchone()
    stars_total_qty = int(stars_qty_row["q"]) if stars_qty_row else 0
    
    # 📱 Virtual SMS Raqamlar
    virtual_total = conn.execute("SELECT COUNT(*) as c FROM virtual_numbers").fetchone()["c"]
    virtual_today = conn.execute("SELECT COUNT(*) as c FROM virtual_numbers WHERE date(created_at, 'localtime') = date('now', 'localtime')").fetchone()["c"]
    virtual_sum_row = conn.execute("SELECT COALESCE(SUM(price), 0) as s FROM virtual_numbers WHERE status != 'cancelled'").fetchone()
    virtual_total_sum = float(virtual_sum_row["s"]) if virtual_sum_row else 0.0
    virtual_today_sum_row = conn.execute("SELECT COALESCE(SUM(price), 0) as s FROM virtual_numbers WHERE status != 'cancelled' AND date(created_at, 'localtime') = date('now', 'localtime')").fetchone()
    virtual_today_sum = float(virtual_today_sum_row["s"]) if virtual_today_sum_row else 0.0
    virtual_active = conn.execute("SELECT COUNT(*) as c FROM virtual_numbers WHERE status = 'waiting'").fetchone()["c"]
    
    # ⏳ Faol Buyurtmalar (Barcha toifalar bo'yicha)
    active_smm_stars = conn.execute("""
        SELECT COUNT(*) as c FROM orders 
        WHERE status NOT IN ('Completed', 'Bajarildi', 'Yakunlandi', 'Canceled', 'Cancelled', 'Bekor qilindi', 'Canceled/Refunded', 'Partial/Refunded', 'Partial')
    """).fetchone()["c"]
    active_orders_count = active_smm_stars + virtual_active
    
    # 💳 To'lovlar (Depozitlar)
    dep_total_row = conn.execute("SELECT COALESCE(SUM(amount), 0) as s FROM deposits WHERE status = 'completed'").fetchone()
    total_deposits_sum = float(dep_total_row["s"]) if dep_total_row else 0.0
    dep_today_row = conn.execute("SELECT COALESCE(SUM(amount), 0) as s FROM deposits WHERE status = 'completed' AND date(created_at, 'localtime') = date('now', 'localtime')").fetchone()
    today_deposits_sum = float(dep_today_row["s"]) if dep_today_row else 0.0
    pending_deposits_count = conn.execute("SELECT COUNT(*) as c FROM deposits WHERE status = 'pending' AND expires_at >= datetime('now', 'localtime')").fetchone()["c"]
    
    # Jami aylanma (Barcha xizmatlar sof summasi)
    total_turnover = smm_total_sum + stars_total_sum + virtual_total_sum
    today_turnover = smm_today_sum + stars_today_sum + virtual_today_sum
    
    conn.close()
    return {
        "total_users": total_users,
        "banned_users": banned_users,
        "today_users": today_users,
        "total_user_balance": total_user_balance,
        
        "smm_total": smm_total,
        "smm_today": smm_today,
        "smm_total_sum": smm_total_sum,
        "smm_today_sum": smm_today_sum,
        
        "stars_total": stars_total,
        "stars_today": stars_today,
        "stars_total_sum": stars_total_sum,
        "stars_today_sum": stars_today_sum,
        "stars_total_qty": stars_total_qty,
        
        "virtual_total": virtual_total,
        "virtual_today": virtual_today,
        "virtual_total_sum": virtual_total_sum,
        "virtual_today_sum": virtual_today_sum,
        "virtual_active": virtual_active,
        
        "active_orders_count": active_orders_count,
        "total_turnover": total_turnover,
        "today_turnover": today_turnover,
        
        "total_deposits_sum": total_deposits_sum,
        "today_deposits_sum": today_deposits_sum,
        "pending_deposits_count": pending_deposits_count,
        
        # Legacy moslik uchun
        "orders_total": smm_total + stars_total,
        "orders_today": smm_today + stars_today,
        "total_order_sum": smm_total_sum + stars_total_sum,
        "today_order_sum": smm_today_sum + stars_today_sum,
        "virtual_numbers_count": virtual_total,
    }


# ──────────────────────────────────────────
#  Balans va To'lov (Deposit) funksiyalari
# ──────────────────────────────────────────

def get_user_balance(user_id: int) -> float:
    """Foydalanuvchi balansini olish"""
    conn = get_connection()
    row = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return float(row["balance"]) if row and row["balance"] is not None else 0.0


def add_user_balance(user_id: int, amount: float) -> float:
    """Foydalanuvchi balansiga mablag' qo'shish"""
    conn = get_connection()
    conn.execute("UPDATE users SET balance = COALESCE(balance, 0) + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    row = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return float(row["balance"]) if row else 0.0


def deduct_user_balance(user_id: int, amount: float) -> float:
    """Foydalanuvchi balansidan mablag' ayirish (manfiy bo'lmasligi uchun)"""
    conn = get_connection()
    conn.execute("UPDATE users SET balance = MAX(0, COALESCE(balance, 0) - ?) WHERE user_id = ?", (amount, user_id))
    conn.commit()
    row = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return float(row["balance"]) if row else 0.0


def set_user_balance(user_id: int, amount: float) -> float:
    """Foydalanuvchi balansini aniq belgilash"""
    conn = get_connection()
    conn.execute("UPDATE users SET balance = ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    row = conn.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return float(row["balance"]) if row else 0.0


def search_users(query: str, limit: int = 5):
    """Foydalanuvchini ID, username yoki ismi bo'yicha qidirish"""
    conn = get_connection()
    query_clean = str(query).strip().lstrip("@")
    if query_clean.isdigit():
        rows = conn.execute("""
            SELECT id, user_id, username, full_name, phone, balance, is_admin, is_banned,
                   datetime(joined_at, 'localtime') as joined_at,
                   datetime(last_seen, 'localtime') as last_seen
            FROM users WHERE user_id = ? OR CAST(user_id AS TEXT) LIKE ? LIMIT ?
        """, (int(query_clean), f"%{query_clean}%", limit)).fetchall()
    else:
        rows = conn.execute("""
            SELECT id, user_id, username, full_name, phone, balance, is_admin, is_banned,
                   datetime(joined_at, 'localtime') as joined_at,
                   datetime(last_seen, 'localtime') as last_seen
            FROM users 
            WHERE username LIKE ? OR full_name LIKE ? 
            ORDER BY id DESC LIMIT ?
        """, (f"%{query_clean}%", f"%{query_clean}%", limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_users(limit: int = 8, offset: int = 0):
    """Oxirgi ro'yxatdan o'tgan foydalanuvchilar (sahifalash bilan)"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, user_id, username, full_name, phone, balance, is_admin, is_banned,
               datetime(joined_at, 'localtime') as joined_at,
               datetime(last_seen, 'localtime') as last_seen
        FROM users ORDER BY id DESC LIMIT ? OFFSET ?
    """, (limit, offset)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_total_users_count() -> int:
    """Jami foydalanuvchilar soni"""
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()
    conn.close()
    return int(row["c"]) if row else 0


def create_pending_deposit(user_id: int, amount: int, minutes: int = 5) -> dict:
    """
    Yangi kutilayotgan to'lov yaratish (noyob exact_amount bilan).
    Masalan, 10000 kiritilsa -> 10005 yoki 10012 qilib beradi.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Avvalgi kutilayotgan to'lovlarni bekor qilamiz
    cursor.execute("UPDATE deposits SET status = 'cancelled' WHERE user_id = ? AND status = 'pending'", (user_id,))

    # Hozirda faol bo'lgan barcha exact_amount larni olamiz
    active_rows = cursor.execute(
        "SELECT exact_amount FROM deposits WHERE status = 'pending' AND expires_at > datetime('now', 'localtime')"
    ).fetchall()
    active_amounts = set(r["exact_amount"] for r in active_rows)

    # 1 dan 99 gacha bo'sh qo'shimcha topamiz
    offset = 1
    while (amount + offset) in active_amounts and offset < 200:
        offset += 1
    exact_amount = amount + offset

    cursor.execute("""
        INSERT INTO deposits (user_id, amount, exact_amount, status, expires_at)
        VALUES (?, ?, ?, 'pending', datetime('now', 'localtime', ?))
    """, (user_id, amount, exact_amount, f'+{minutes} minutes'))
    deposit_id = cursor.lastrowid
    conn.commit()

    row = cursor.execute("SELECT * FROM deposits WHERE id = ?", (deposit_id,)).fetchone()
    conn.close()
    return dict(row)


def find_pending_deposit_by_amount(received_amount: int):
    """
    Kelgan summa bo'yicha kutilayotgan to'lovni topish.
    Faqat muddati o'tmagan (5 daqiqa ichida) va status='pending' bo'lganini qidiradi.
    """
    conn = get_connection()
    row = conn.execute("""
        SELECT * FROM deposits 
        WHERE exact_amount = ? AND status = 'pending' AND expires_at >= datetime('now', 'localtime')
        ORDER BY id DESC LIMIT 1
    """, (received_amount,)).fetchone()
    conn.close()
    return dict(row) if row else None


def complete_deposit(deposit_id: int):
    """To'lovni muvaffaqiyatli yakunlash va foydalanuvchiga balans qo'shish"""
    conn = get_connection()
    cursor = conn.cursor()

    dep = cursor.execute("SELECT * FROM deposits WHERE id = ? AND status = 'pending'", (deposit_id,)).fetchone()
    if not dep:
        conn.close()
        return None

    deposit_data = dict(dep)
    cursor.execute("UPDATE deposits SET status = 'completed' WHERE id = ?", (deposit_id,))
    cursor.execute("UPDATE users SET balance = COALESCE(balance, 0) + ? WHERE user_id = ?", (deposit_data["amount"], deposit_data["user_id"]))
    conn.commit()

    new_bal = cursor.execute("SELECT balance FROM users WHERE user_id = ?", (deposit_data["user_id"],)).fetchone()
    conn.close()

    deposit_data["new_balance"] = new_bal["balance"] if new_bal else 0.0
    return deposit_data


# ──────────────────────────────────────────
#  Buyurtmalar (Orders) funksiyalari
# ──────────────────────────────────────────

def add_order_record(order_id: int, user_id: int, service_id: int, service_title: str, quantity: int, price: float, link: str = ""):
    """Yangi buyurtmani bazaga yozish"""
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO orders (order_id, user_id, service_id, service_title, quantity, price, status, link)
        VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?)
    """, (order_id, user_id, service_id, service_title, quantity, price, link))
    conn.commit()
    conn.close()


def get_active_orders():
    """Hali yakunlanmagan (tekshirilishi kerak bo'lgan) barcha buyurtmalarni olish"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM orders 
        WHERE status NOT IN ('Completed', 'Bajarildi', 'Yakunlandi', 'Canceled', 'Cancelled', 'Bekor qilindi', 'Canceled/Refunded', 'Partial/Refunded', 'Partial')
        ORDER BY id ASC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_order_status(order_id: int, status: str):
    """Buyurtma holatini yangilash"""
    conn = get_connection()
    conn.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
    conn.commit()
    conn.close()


def get_user_orders(user_id: int, limit: int = 10):
    """Foydalanuvchining so'nggi buyurtmalarini olish"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM orders 
        WHERE user_id = ? 
        ORDER BY id DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_order_by_id(order_id: int):
    """Buyurtma ID bo'yicha ma'lumotni olish"""
    conn = get_connection()
    row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_recent_orders(limit: int = 8):
    """Oxirgi barcha buyurtmalar ro'yxati"""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_deposits(limit: int = 8, offset: int = 0):
    """Oxirgi depozitlar/to'lovlar ro'yxati (foydalanuvchi ma'lumotlari bilan)"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT d.id, d.user_id, d.amount, d.exact_amount, d.status,
               datetime(d.created_at, 'localtime') as created_at,
               datetime(d.expires_at, 'localtime') as expires_at,
               u.username, u.full_name
        FROM deposits d
        LEFT JOIN users u ON d.user_id = u.user_id
        ORDER BY d.id DESC LIMIT ? OFFSET ?
    """, (limit, offset)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_deposits_count() -> int:
    """Jami barcha depozitlar soni"""
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as c FROM deposits").fetchone()
    conn.close()
    return int(row["c"]) if row else 0


def get_pending_deposits(limit: int = 8, offset: int = 0):
    """Kutilayotgan depozitlar (foydalanuvchi ma'lumotlari bilan)"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT d.id, d.user_id, d.amount, d.exact_amount, d.status,
               datetime(d.created_at, 'localtime') as created_at,
               datetime(d.expires_at, 'localtime') as expires_at,
               u.username, u.full_name
        FROM deposits d
        LEFT JOIN users u ON d.user_id = u.user_id
        WHERE d.status = 'pending'
        ORDER BY d.id DESC LIMIT ? OFFSET ?
    """, (limit, offset)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pending_deposits_count() -> int:
    """Kutilayotgan depozitlar soni"""
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as c FROM deposits WHERE status = 'pending'").fetchone()
    conn.close()
    return int(row["c"]) if row else 0


def get_deposit_by_id(deposit_id: int):
    """Depozit ID bo'yicha to'liq ma'lumot olish"""
    conn = get_connection()
    row = conn.execute("""
        SELECT d.id, d.user_id, d.amount, d.exact_amount, d.status,
               datetime(d.created_at, 'localtime') as created_at,
               datetime(d.expires_at, 'localtime') as expires_at,
               u.username, u.full_name
        FROM deposits d
        LEFT JOIN users u ON d.user_id = u.user_id
        WHERE d.id = ?
    """, (deposit_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def cancel_deposit(deposit_id: int) -> bool:
    """Kutilayotgan depozitni bekor qilish"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE deposits SET status = 'cancelled' WHERE id = ? AND status = 'pending'", (deposit_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


# ──────────────────────────────────────────
#  Virtual Raqamlar (SMS) funksiyalari
# ──────────────────────────────────────────

def add_virtual_number(user_id: int, server: int, country: str, number: str, hash_code: str, price: float) -> int:
    """Yangi olingan virtual raqamni bazaga yozish"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO virtual_numbers (user_id, server, country, number, hash_code, price, status)
        VALUES (?, ?, ?, ?, ?, ?, 'waiting')
    """, (user_id, server, country, number, hash_code, price))
    num_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return num_id


def get_virtual_number_by_id(order_id: int):
    """Virtual raqam buyurtmasini olish"""
    conn = get_connection()
    row = conn.execute("SELECT * FROM virtual_numbers WHERE id = ?", (order_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_virtual_number_sms(order_id: int, sms_code: str, status: str = "received"):
    """SMS kod kelganda raqamni yangilash"""
    conn = get_connection()
    conn.execute("""
        UPDATE virtual_numbers 
        SET sms_code = ?, status = ?
        WHERE id = ?
    """, (sms_code, status, order_id))
    conn.commit()
    conn.close()


def get_user_virtual_numbers(user_id: int, limit: int = 5):
    """Foydalanuvchining virtual raqamlari tarixi"""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM virtual_numbers 
        WHERE user_id = ? 
        ORDER BY id DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_orders_count(user_id: int) -> dict:
    """Foydalanuvchining har bir turdagi buyurtmalari sonini olish"""
    conn = get_connection()
    smm_count = conn.execute(
        "SELECT COUNT(*) as c FROM orders WHERE user_id = ? AND service_id != 9999", 
        (user_id,)
    ).fetchone()["c"]
    
    stars_count = conn.execute(
        "SELECT COUNT(*) as c FROM orders WHERE user_id = ? AND service_id = 9999", 
        (user_id,)
    ).fetchone()["c"]
    
    number_count = conn.execute(
        "SELECT COUNT(*) as c FROM virtual_numbers WHERE user_id = ?", 
        (user_id,)
    ).fetchone()["c"]
    
    conn.close()
    return {
        "smm": smm_count,
        "stars": stars_count,
        "number": number_count,
        "total": smm_count + stars_count + number_count
    }


def get_user_unified_orders(user_id: int, category: str = "all", limit: int = 5, offset: int = 0) -> list:
    """
    Barcha turdagi buyurtmalarni (SMM, Stars, Virtual raqamlar) birlashtirib, sana bo'yicha saralab qaytarish
    category: 'all', 'smm', 'stars', 'number'
    """
    conn = get_connection()
    results = []
    
    if category in ["all", "smm", "stars"]:
        query = "SELECT * FROM orders WHERE user_id = ?"
        params = [user_id]
        if category == "smm":
            query += " AND service_id != 9999"
        elif category == "stars":
            query += " AND service_id = 9999"
        
        rows = conn.execute(query, params).fetchall()
        for r in rows:
            d = dict(r)
            is_stars = (d.get("service_id") == 9999)
            results.append({
                "type": "stars" if is_stars else "smm",
                "id": d["order_id"],
                "db_id": d["id"],
                "user_id": d["user_id"],
                "service_id": d.get("service_id"),
                "title": d.get("service_title", "Xizmat"),
                "quantity": d.get("quantity", 0),
                "price": float(d.get("price", 0.0) or 0.0),
                "status": d.get("status", "Pending"),
                "link": d.get("link", ""),
                "created_at": d.get("created_at", "")
            })

    if category in ["all", "number"]:
        v_rows = conn.execute(
            "SELECT * FROM virtual_numbers WHERE user_id = ?", 
            (user_id,)
        ).fetchall()
        for r in v_rows:
            d = dict(r)
            results.append({
                "type": "number",
                "id": d["id"],
                "db_id": d["id"],
                "user_id": d["user_id"],
                "server": d.get("server", 1),
                "country": d.get("country", ""),
                "number": d.get("number", ""),
                "hash_code": d.get("hash_code", ""),
                "sms_code": d.get("sms_code", ""),
                "price": float(d.get("price", 0.0) or 0.0),
                "status": d.get("status", "waiting"),
                "created_at": d.get("created_at", "")
            })
    
    conn.close()
    
    # Sana bo'yicha teskari saralash (eng yangi birinchi)
    results.sort(key=lambda x: str(x.get("created_at") or ""), reverse=True)
    return results[offset:offset + limit]


def get_all_orders_count() -> dict:
    """Admin uchun barcha buyurtmalar soni (toifalar bo'yicha)"""
    conn = get_connection()
    smm_count = conn.execute(
        "SELECT COUNT(*) as c FROM orders WHERE service_id != 9999"
    ).fetchone()["c"]
    
    stars_count = conn.execute(
        "SELECT COUNT(*) as c FROM orders WHERE service_id = 9999"
    ).fetchone()["c"]
    
    number_count = conn.execute(
        "SELECT COUNT(*) as c FROM virtual_numbers"
    ).fetchone()["c"]
    
    active_smm_stars = conn.execute("""
        SELECT COUNT(*) as c FROM orders 
        WHERE status NOT IN ('Completed', 'Bajarildi', 'Yakunlandi', 'Canceled', 'Cancelled', 'Bekor qilindi', 'Canceled/Refunded', 'Partial/Refunded', 'Partial')
    """).fetchone()["c"]

    active_numbers = conn.execute("""
        SELECT COUNT(*) as c FROM virtual_numbers 
        WHERE status = 'waiting'
    """).fetchone()["c"]

    conn.close()
    return {
        "smm": smm_count,
        "stars": stars_count,
        "number": number_count,
        "active": active_smm_stars + active_numbers,
        "total": smm_count + stars_count + number_count
    }


def get_all_unified_orders(category: str = "all", limit: int = 8, offset: int = 0) -> list:
    """
    Admin uchun barcha foydalanuvchilarning buyurtmalarini toifalar bo'yicha olish
    category: 'all', 'smm', 'stars', 'number', 'active'
    """
    conn = get_connection()
    results = []
    
    if category in ["all", "smm", "stars", "active"]:
        query = "SELECT * FROM orders WHERE 1=1"
        if category == "smm":
            query += " AND service_id != 9999"
        elif category == "stars":
            query += " AND service_id = 9999"
        elif category == "active":
            query += " AND status NOT IN ('Completed', 'Bajarildi', 'Yakunlandi', 'Canceled', 'Cancelled', 'Bekor qilindi', 'Canceled/Refunded', 'Partial/Refunded', 'Partial')"
        
        rows = conn.execute(query).fetchall()
        for r in rows:
            d = dict(r)
            is_stars = (d.get("service_id") == 9999)
            results.append({
                "type": "stars" if is_stars else "smm",
                "id": d["order_id"],
                "db_id": d["id"],
                "user_id": d["user_id"],
                "service_id": d.get("service_id"),
                "title": d.get("service_title", "Xizmat"),
                "quantity": d.get("quantity", 0),
                "price": float(d.get("price", 0.0) or 0.0),
                "status": d.get("status", "Pending"),
                "link": d.get("link", ""),
                "created_at": d.get("created_at", "")
            })

    if category in ["all", "number", "active"]:
        v_query = "SELECT * FROM virtual_numbers WHERE 1=1"
        if category == "active":
            v_query += " AND status = 'waiting'"
            
        v_rows = conn.execute(v_query).fetchall()
        for r in v_rows:
            d = dict(r)
            results.append({
                "type": "number",
                "id": d["id"],
                "db_id": d["id"],
                "user_id": d["user_id"],
                "server": d.get("server", 1),
                "country": d.get("country", ""),
                "number": d.get("number", ""),
                "hash_code": d.get("hash_code", ""),
                "sms_code": d.get("sms_code", ""),
                "price": float(d.get("price", 0.0) or 0.0),
                "status": d.get("status", "waiting"),
                "created_at": d.get("created_at", "")
            })
    
    conn.close()
    
    # Sana bo'yicha teskari saralash (eng yangi birinchi)
    results.sort(key=lambda x: str(x.get("created_at") or ""), reverse=True)
    return results[offset:offset + limit]


def update_virtual_number_status(order_id: int, status: str):
    """Virtual raqam holatini yangilash"""
    conn = get_connection()
    conn.execute("UPDATE virtual_numbers SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()


def search_order_anywhere(query: str):
    """Buyurtmani ID, Raqam yoki boshqa parametr bo'yicha qidirish (SMM, Stars, Virtual Raqam)"""
    conn = get_connection()
    clean_q = query.strip().replace("#", "")
    
    # 1. Orders jadvalidan ID bo'yicha
    if clean_q.isdigit():
        oid = int(clean_q)
        row = conn.execute("SELECT * FROM orders WHERE order_id = ? OR id = ?", (oid, oid)).fetchone()
        if row:
            conn.close()
            d = dict(row)
            return {
                "type": "stars" if d.get("service_id") == 9999 else "smm",
                **d
            }
        
        # 2. Virtual raqamlar jadvalidan ID bo'yicha
        vrow = conn.execute("SELECT * FROM virtual_numbers WHERE id = ?", (oid,)).fetchone()
        if vrow:
            conn.close()
            return {"type": "number", **dict(vrow)}
            
    # 3. Virtual raqamlar jadvalidan telefon raqami bo'yicha
    vrow_num = conn.execute("SELECT * FROM virtual_numbers WHERE number LIKE ? OR hash_code LIKE ?", (f"%{clean_q}%", f"%{clean_q}%")).fetchone()
    if vrow_num:
        conn.close()
        return {"type": "number", **dict(vrow_num)}
        
    conn.close()
    return None



# ──────────────────────────────────────────
#  Majburiy Obuna Kanallari funksiyalari
# ──────────────────────────────────────────

def add_mandatory_channel(channel_id: str, title: str, url: str) -> bool:
    """Majburiy obuna kanalini qo'shish yoki yangilash"""
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO mandatory_channels (channel_id, title, url)
            VALUES (?, ?, ?)
            ON CONFLICT(channel_id) DO UPDATE SET title = excluded.title, url = excluded.url
        """, (str(channel_id).strip(), str(title).strip(), str(url).strip()))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"add_mandatory_channel xatosi: {e}")
        return False
    finally:
        conn.close()


def get_mandatory_channels() -> list:
    """Barcha majburiy obuna kanallarini olish"""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM mandatory_channels ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_mandatory_channel_by_id(channel_db_id: int) -> dict:
    """ID bo'yicha majburiy kanalni olish"""
    conn = get_connection()
    row = conn.execute("SELECT * FROM mandatory_channels WHERE id = ?", (channel_db_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_mandatory_channel(channel_db_id: int) -> bool:
    """ID bo'yicha majburiy kanalni o'chirish"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mandatory_channels WHERE id = ?", (channel_db_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def delete_mandatory_channel_by_channel_id(channel_id: str) -> bool:
    """Chat ID bo'yicha majburiy kanalni o'chirish"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mandatory_channels WHERE channel_id = ?", (str(channel_id).strip(),))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted




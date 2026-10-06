"""
📱 GrandSMM Virtual Nomer va SMS API Klienti
Hujjat: http://grandsmm.surkhandc2.uz/api/docs.html
Base URL: https://grandsmm.surkhandc2.uz/api/v2/nomer
"""
import logging
import aiohttp
import time
from typing import Dict, Any, Optional

from config import SMM_API_KEY, PRICE_MARGIN_PERCENT, NUMBER_API_URL

logger = logging.getLogger(__name__)

COUNTRY_NAMES = {
    "UZ": ("🇺🇿", "O'zbekiston"),
    "RU": ("🇷🇺", "Rossiya"),
    "KZ": ("🇰🇿", "Qozog'iston"),
    "KG": ("🇰🇬", "Qirg'iziston"),
    "TJ": ("🇹🇯", "Tojikiston"),
    "US": ("🇺🇸", "AQSH"),
    "GB": ("🇬🇧", "Buyuk Britaniya"),
    "TR": ("🇹🇷", "Turkiya"),
    "DE": ("🇩🇪", "Germaniya"),
    "FR": ("🇫🇷", "Fransiya"),
    "ID": ("🇮🇩", "Indoneziya"),
    "IN": ("🇮🇳", "Hindiston"),
    "BR": ("🇧🇷", "Braziliya"),
    "AZ": ("🇦🇿", "Ozarbayjon"),
    "GE": ("🇬🇪", "Gruziya"),
    "AE": ("🇦🇪", "BAA"),
    "SA": ("🇸🇦", "Saudiya Arabistoni"),
    "EG": ("🇪🇬", "Misr"),
    "UA": ("🇺🇦", "Ukraina"),
    "PL": ("🇵🇱", "Polsha"),
    "AF": ("🇦🇫", "Afg'oniston"),
    "AG": ("🇦🇬", "Antigua va Barbuda"),
    "AI": ("🇦🇮", "Angilya"),
    "AL": ("🇦🇱", "Albaniya"),
    "AM": ("🇦🇲", "Armaniston"),
    "AO": ("🇦🇴", "Angola"),
    "AR": ("🇦🇷", "Argentina"),
    "AS": ("🇦🇸", "Amerika Samoasi"),
    "AT": ("🇦🇹", "Avstriya"),
    "AU": ("🇦🇺", "Avstraliya"),
    "AW": ("🇦🇼", "Aruba"),
    "BA": ("🇧🇦", "Bosniya va Gertsegovina"),
    "BD": ("🇧🇩", "Bangladesh"),
    "BE": ("🇧🇪", "Belgiya"),
    "BF": ("🇧🇫", "Burkina-Faso"),
    "BH": ("🇧🇭", "Bahrayn"),
    "BM": ("🇧🇲", "Bermuda"),
    "BN": ("🇧🇳", "Bruney"),
    "BO": ("🇧🇴", "Boliviya"),
    "BS": ("🇧🇸", "Bagama"),
    "BW": ("🇧🇼", "Botsvana"),
    "BZ": ("🇧🇿", "Beliz"),
    "CA": ("🇨🇦", "Kanada"),
    "CD": ("🇨🇩", "Kongo DR"),
    "CG": ("🇨🇬", "Kongo"),
    "CH": ("🇨🇭", "Shveytsariya"),
    "CI": ("🇨🇮", "Kot-d'Ivuar"),
    "CL": ("🇨🇱", "Chili"),
    "CN": ("🇨🇳", "Xitoy"),
    "CO": ("🇨🇴", "Kolumbiya"),
    "CR": ("🇨🇷", "Kosta-Rika"),
    "CU": ("🇨🇺", "Kuba"),
    "CV": ("🇨🇻", "Kabo-Verde"),
    "CW": ("🇨🇼", "Kyurasao"),
    "CY": ("🇨🇾", "Kipr"),
    "CZ": ("🇨🇿", "Chexiya"),
    "DJ": ("🇩🇯", "Jibuti"),
    "DK": ("🇩🇰", "Daniya"),
    "DM": ("🇩🇲", "Dominika"),
    "DO": ("🇩🇴", "Dominikana"),
    "DZ": ("🇩🇿", "Jazoir"),
    "EC": ("🇪🇨", "Ekvador"),
    "EE": ("🇪🇪", "Estoniya"),
    "ER": ("🇪🇷", "Eritreya"),
    "ES": ("🇪🇸", "Ispaniya"),
    "ET": ("🇪🇹", "Efiopiya"),
    "FI": ("🇫🇮", "Finlyandiya"),
    "FJ": ("🇫🇯", "Fiji"),
    "GA": ("🇬🇦", "Gabon"),
    "GD": ("🇬🇩", "Grenada"),
    "GF": ("🇬🇫", "Fransuz Gvianasi"),
    "GG": ("🇬🇬", "Gernsi"),
    "GH": ("🇬🇭", "Gana"),
    "GL": ("🇬🇱", "Grenlandiya"),
    "GM": ("🇬🇲", "Gambiya"),
    "GN": ("🇬🇳", "Gvineya"),
    "GP": ("🇬🇵", "Gvadelupa"),
    "GQ": ("🇬🇶", "Ekvatorial Gvineya"),
    "GR": ("🇬🇷", "Gretsiya"),
    "GT": ("🇬🇹", "Gvatemala"),
    "GU": ("🇬🇺", "Guam"),
    "GY": ("🇬🇾", "Gayana"),
    "HK": ("🇭🇰", "Gonkong"),
    "HN": ("🇭🇳", "Gonduras"),
    "HR": ("🇭🇷", "Xorvatiya"),
    "HT": ("🇭🇹", "Gaiti"),
    "HU": ("🇭🇺", "Vengriya"),
    "IE": ("🇮🇪", "Irlandiya"),
    "IL": ("🇮🇱", "Isroil"),
    "IM": ("🇮🇲", "Men oroli"),
    "IQ": ("🇮🇶", "Iroq"),
    "IR": ("🇮🇷", "Eron"),
    "IS": ("🇮🇸", "Islandiya"),
    "IT": ("🇮🇹", "Italiya"),
    "JE": ("🇯🇪", "Jersi"),
    "JM": ("🇯🇲", "Yamayka"),
    "JO": ("🇯🇴", "Iordaniya"),
    "JP": ("🇯🇵", "Yaponiya"),
    "KE": ("🇰🇪", "Keniya"),
    "KH": ("🇰🇭", "Kambodja"),
    "KI": ("🇰🇮", "Kiribati"),
    "KM": ("🇰🇲", "Komor orollari"),
    "KN": ("🇰🇳", "Sent-Kits va Nevis"),
    "KP": ("🇰🇵", "Shimoliy Koreya"),
    "KR": ("🇰🇷", "Janubiy Koreya"),
    "KW": ("🇰🇼", "Quvayt"),
    "KY": ("🇰🇾", "Kayman orollari"),
    "LA": ("🇱🇦", "Laos"),
    "LB": ("🇱🇧", "Livan"),
    "LC": ("🇱🇨", "Sent-Lyusiya"),
    "LK": ("🇱🇰", "Shri-Lanka"),
    "LR": ("🇱🇷", "Liberiya"),
    "LS": ("🇱🇸", "Lesoto"),
    "LT": ("🇱🇹", "Litva"),
    "LU": ("🇱🇺", "Lyuksemburg"),
    "LV": ("🇱🇻", "Latviya"),
    "LY": ("🇱🇾", "Liviya"),
    "MA": ("🇲🇦", "Marokash"),
    "MD": ("🇲🇩", "Moldova"),
    "ME": ("🇲🇪", "Chernogoriya"),
    "MG": ("🇲🇬", "Madagaskar"),
    "MK": ("🇲🇰", "Makedoniya"),
    "ML": ("🇲🇱", "Mali"),
    "MM": ("🇲🇲", "Myanma"),
    "MN": ("🇲🇳", "Mo'g'uliston"),
    "MO": ("🇲🇴", "Makao"),
    "MQ": ("🇲🇶", "Martinika"),
    "MT": ("🇲🇹", "Malta"),
    "MU": ("🇲🇺", "Mavrikiy"),
    "MV": ("🇲🇻", "Maldiv"),
    "MW": ("🇲🇼", "Malavi"),
    "MX": ("🇲🇽", "Meksika"),
    "MY": ("🇲🇾", "Malayziya"),
    "MZ": ("🇲🇿", "Mozambik"),
    "NA": ("🇳🇦", "Namibiya"),
    "NC": ("🇳🇨", "Yangi Kaledoniya"),
    "NE": ("🇳🇪", "Niger"),
    "NG": ("🇳🇬", "Nigeriya"),
    "NI": ("🇳🇮", "Nikaragua"),
    "NL": ("🇳🇱", "Niderlandiya"),
    "NO": ("🇳🇴", "Norvegiya"),
    "NP": ("🇳🇵", "Nepal"),
    "NU": ("🇳🇺", "Niue"),
    "NZ": ("🇳🇿", "Yangi Zelandiya"),
    "OM": ("🇴🇲", "Ummon"),
    "PA": ("🇵🇦", "Panama"),
    "PE": ("🇵🇪", "Peru"),
    "PF": ("🇵🇫", "Fransuz Polineziyasi"),
    "PG": ("🇵🇬", "Papua-Yangi Gvineya"),
    "PH": ("🇵🇭", "Filippin"),
    "PK": ("🇵🇰", "Pokiston"),
    "PM": ("🇵🇲", "Sen-Pyer"),
    "PR": ("🇵🇷", "Puerto-Riko"),
    "PT": ("🇵🇹", "Portugaliya"),
    "PW": ("🇵🇼", "Palau"),
    "PY": ("🇵🇾", "Paragvay"),
    "QA": ("🇶🇦", "Qatar"),
    "RE": ("🇷🇪", "Reyunion"),
    "RO": ("🇷🇴", "Ruminiya"),
    "RS": ("🇷🇸", "Serbiya"),
    "SB": ("🇸🇧", "Solomon orollari"),
    "SC": ("🇸🇨", "Seyshel"),
    "SD": ("🇸🇩", "Sudan"),
    "SE": ("🇸🇪", "Shvetsiya"),
    "SG": ("🇸🇬", "Singapur"),
    "SI": ("🇸🇮", "Sloveniya"),
    "SK": ("🇸🇰", "Slovakiya"),
    "SL": ("🇸🇱", "Syerra-Leone"),
    "SN": ("🇸🇳", "Senegal"),
    "SO": ("🇸🇴", "Somali"),
    "SR": ("🇸🇷", "Surinam"),
    "SS": ("🇸🇸", "Janubiy Sudan"),
    "ST": ("🇸🇹", "San-Tome"),
    "SV": ("🇸🇻", "Salvador"),
    "SX": ("🇸🇽", "Sint-Marten"),
    "SY": ("🇸🇾", "Suriya"),
    "SZ": ("🇸🇿", "Esvatini"),
    "TC": ("🇹🇨", "Turks va Kaykos"),
    "TD": ("🇹🇩", "Chad"),
    "TH": ("🇹🇭", "Tailand"),
    "TL": ("🇹🇱", "Sharqiy Timor"),
    "TN": ("🇹🇳", "Tunis"),
    "TO": ("🇹🇴", "Tonga"),
    "TT": ("🇹🇹", "Trinidad va Tobago"),
    "TW": ("🇹🇼", "Tayvan"),
    "TZ": ("🇹🇿", "Tanzaniya"),
    "UG": ("🇺🇬", "Uganda"),
    "UY": ("🇺🇾", "Urugvay"),
    "VC": ("🇻🇨", "Sent-Vinsent"),
    "VE": ("🇻🇪", "Venesuela"),
    "VG": ("🇻🇬", "Britaniya Virgin"),
    "VI": ("🇻🇮", "AQSH Virgin"),
    "VN": ("🇻🇳", "Vyetnam"),
    "VU": ("🇻🇺", "Vanuatu"),
    "WS": ("🇼🇸", "Samoa"),
    "XK": ("🇽🇰", "Kosovo"),
    "YE": ("🇾🇪", "Yaman"),
    "YT": ("🇾🇹", "Mayotta"),
    "ZA": ("🇿🇦", "JAR"),
    "ZM": ("🇿🇲", "Zambiya"),
    "ZW": ("🇿🇼", "Zimbabve"),
}


def get_country_display(code: str) -> tuple[str, str]:
    """Davlat kodi bo'yicha bayroq va to'liq nomini qaytarish"""
    c = code.upper().strip()
    if c in COUNTRY_NAMES:
        return COUNTRY_NAMES[c]
    # Agar lug'atda bo'lmasa, harflardan bayroq yasaymiz
    flag = "".join(chr(127397 + ord(ch)) for ch in c if 'A' <= ch <= 'Z')
    return (flag or "🌐", c)


def format_country_button_text(flag: str, name: str, price: float, max_len: int = 29) -> str:
    """
    Tugma matnini shakllantirish:
    Narx har doim to'liq ko'rinadi.
    Agar butun matn sig'may qolsa, davlat nomi harflari sig'ganicha chiqib,
    sig'magani '...' qilinadi.
    """
    price_str = f" — {price:,.0f} so'm"
    prefix = f"{flag} "
    full_text = f"{prefix}{name}{price_str}"
    if len(full_text) <= max_len:
        return full_text

    available_chars = max_len - len(prefix) - len(price_str) - 3
    if available_chars > 2:
        short_name = name[:available_chars].strip() + "..."
    else:
        short_name = name[:max(1, available_chars)].strip() + "..."
    return f"{prefix}{short_name}{price_str}"


class NumberAPIClient:
    def __init__(self, api_url: str = NUMBER_API_URL, api_key: str = SMM_API_KEY):
        self.api_url = api_url
        self.api_key = api_key
        self._countries_cache = {}
        self._cache_time = {}
        self._cache_ttl = 180  # 3 daqiqa kesh

    async def _get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """GET so'rov yuborish"""
        p = params.copy()
        p["api_key"] = self.api_key
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url, params=p, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status == 200:
                        return await resp.json(content_type=None)
                    else:
                        text = await resp.text()
                        logger.error(f"Number API HTTP {resp.status}: {text}")
                        return {"success": False, "error": f"HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"Number API xatosi: {e}")
            return {"success": False, "error": f"Tarmoq xatosi: {e}"}

    async def get_balance(self) -> Dict[str, Any]:
        """API hisob balansini ko'rish"""
        return await self._get({"action": "getBalance"})

    async def get_countries(self, server: int = 1, force_refresh: bool = False) -> Dict[str, Any]:
        """Server bo'yicha mavjud davlatlar va narxlar ro'yxati (+20% ustama bilan)"""
        now = time.time()
        if not force_refresh and server in self._countries_cache and (now - self._cache_time.get(server, 0) < self._cache_ttl):
            return self._countries_cache[server]

        res = await self._get({"action": "available_countries", "server": server})
        if res.get("success") and "countries" in res:
            multiplier = 1.0 + (PRICE_MARGIN_PERCENT / 100.0)
            for c_code, info in res["countries"].items():
                if isinstance(info, dict) and "price" in info:
                    try:
                        base_price = float(info["price"])
                        info["price"] = round(base_price * multiplier)
                    except (ValueError, TypeError):
                        pass
            self._countries_cache[server] = res
            self._cache_time[server] = now
        return res

    async def get_number(self, server: int, country: str) -> Dict[str, Any]:
        """
        Virtual raqam sotib olish
        :param server: 1 yoki 2
        :param country: Davlat kodi (masalan: UZ, RU, US)
        :return: {"success": True, "number": "+998...", "hash_code": "...", "price": 4050, "server": 1}
        """
        return await self._get({
            "action": "getNumber",
            "server": int(server),
            "country": str(country).upper().strip()
        })

    async def get_code(self, server: int, hash_code: str = "", number: str = "") -> Dict[str, Any]:
        """
        SMS kodni tekshirish
        :param server: 1 yoki 2
        :param hash_code: server=1 uchun hash_code
        :param number: server=2 uchun number
        :return: {"success": True, "status": "ok", "code": "12345", "password": ""}
                 yoki {"success": False, "status": "waiting"}
        """
        params = {"action": "getCode", "server": int(server)}
        if int(server) == 1:
            params["hash_code"] = str(hash_code)
        else:
            params["number"] = str(number).replace("+", "").strip()
        return await self._get(params)

    async def get_stars_price(self) -> Dict[str, Any]:
        """GrandSMM dan Stars narxlarini olish (action=getPrices)"""
        return await self._get({"action": "getPrices"})

    async def buy_stars(self, username: str, amount: int) -> Dict[str, Any]:
        """
        Telegram Stars sotib olish (action=buyStars)
        :param username: Telegram username
        :param amount: Stars soni (kamida 50)
        """
        clean_user = str(username).strip()
        clean_user = clean_user.replace("https://t.me/", "").replace("http://t.me/", "").replace("t.me/", "")
        clean_user = clean_user.lstrip("@").strip().rstrip("/")
        return await self._get({
            "action": "buyStars",
            "username": clean_user,
            "amount": int(amount)
        })


number_api = NumberAPIClient()


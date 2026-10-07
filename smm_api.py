"""
🚀 GrandSMM REST API v2.0 Client (Asinxron)
Hujjat: https://grandsmm.surkhandc2.uz/api/smmdocs.html
"""
import logging
import aiohttp
import time
from typing import Optional, Dict, Any

from config import SMM_API_URL, SMM_API_KEY, PRICE_MARGIN_PERCENT

logger = logging.getLogger(__name__)


class GrandSMMClient:
    """GrandSMM API bilan ishlovchi asinxron klass"""

    def __init__(self, api_url: str = SMM_API_URL, api_key: str = SMM_API_KEY):
        self.api_url = api_url
        self.api_key = api_key
        self._services_cache = None
        self._services_cache_time = 0
        self._cache_ttl = 300  # 5 daqiqa kesh

    async def _request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST so'rov yuborish (x-www-form-urlencoded)"""
        payload = data.copy()
        payload["key"] = self.api_key

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status == 200:
                        return await resp.json(content_type=None)
                    else:
                        text = await resp.text()
                        logger.error(f"GrandSMM API HTTP {resp.status}: {text}")
                        return {"error": f"Server javobi: HTTP {resp.status}"}
        except Exception as e:
            logger.error(f"GrandSMM API so'rov xatosi: {e}")
            return {"error": f"Tarmoq xatosi: {e}"}

    async def get_services(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Barcha mavjud xizmatlar ro'yxatini olish (platformalar bo'yicha guruhlangan va +20% ustama bilan)"""
        now = time.time()
        if not force_refresh and self._services_cache and (now - self._services_cache_time < self._cache_ttl):
            return self._services_cache

        res = await self._request({"action": "services"})
        if isinstance(res, dict) and "error" not in res:
            multiplier = 1.0 + (PRICE_MARGIN_PERCENT / 100.0)
            for platform, items in res.items():
                if isinstance(items, list):
                    for item in items:
                        if "rate" in item:
                            try:
                                base_rate = float(item["rate"])
                                item["rate"] = str(round(base_rate * multiplier))
                            except (ValueError, TypeError):
                                pass
            self._services_cache = res
            self._services_cache_time = now
        return res

    async def get_service_by_id(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Xizmat ID si bo'yicha to'liq ma'lumotni APIdan topish"""
        services = await self.get_services()
        if not isinstance(services, dict):
            return None
        sid = int(service_id)
        for platform, items in services.items():
            if isinstance(items, list):
                for item in items:
                    if int(item.get("service", 0)) == sid:
                        return item
        return None

    def get_cached_rate(self, service_id: int, default: int = 0) -> int:
        """Keshdagi xizmat narxini sinxron qaytarish (agar keshda bo'lsa)"""
        if self._services_cache and isinstance(self._services_cache, dict):
            sid = int(service_id)
            for platform, items in self._services_cache.items():
                if isinstance(items, list):
                    for item in items:
                        if int(item.get("service", 0)) == sid:
                            try:
                                return int(float(item.get("rate", default)))
                            except (ValueError, TypeError):
                                return default
        return default

    async def add_order(self, service_id: int, link: str, quantity: int) -> Dict[str, Any]:
        """
        Yangi SMM buyurtma qo'shish
        :param service_id: Xizmat ID raqami
        :param link: Havola (kanal/guruh/post)
        :param quantity: Miqdor (min va max oralig'ida)
        :return: {'order': 23501} yoki {'error': '...'}
        """
        return await self._request({
            "action": "add",
            "service": int(service_id),
            "link": str(link).strip(),
            "quantity": int(quantity)
        })

    async def get_order_status(self, order_id: int) -> Dict[str, Any]:
        """
        Buyurtma holatini ko'rish
        :param order_id: Buyurtma ID raqami
        :return: {'order': 23501, 'status': 'Bajarilmoqda', 'charge': '15000', ...}
        """
        return await self._request({
            "action": "status",
            "order": int(order_id)
        })

    async def get_balance(self) -> Dict[str, Any]:
        """
        Hisob balansini tekshirish
        :return: {'balance': '150000', 'currency': 'UZS'}
        """
        return await self._request({"action": "balance"})


# Global instansiya
smm_api = GrandSMMClient()

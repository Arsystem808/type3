
import os
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
import httpx

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY") or os.getenv("POLYGON_KEY") or os.getenv("API_KEY")

BASE = "https://api.polygon.io"

class PolygonError(RuntimeError):
    pass

def _headers():
    if not POLYGON_API_KEY:
        raise PolygonError("POLYGON_API_KEY не задан. Укажи ключ в окружении или .env")
    return {"Authorization": f"Bearer {POLYGON_API_KEY}"}

def _today_range_utc(hours_back: int = 36) -> Tuple[str, str]:
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours_back)
    return start.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")

def _norm_crypto_pair(ticker: str) -> Tuple[str, str]:
    """Нормализуем 'BTCUSD'|'BTC/USDT'|'BTCUSDT' → ('BTC','USD'|'USDT')."""
    t = ticker.replace("X:", "").replace(":", "").replace("-", "").replace("_","").upper()
    if "/" in ticker:
        left, right = ticker.upper().split("/")
        return left, right
    # Популярные суффиксы
    for quote in ("USDT","USD","EUR","GBP","RUB"):
        if t.endswith(quote) and len(t) > len(quote):
            return t[:-len(quote)], quote
    # fallback
    if len(t) >= 6:
        return t[:3], t[3:]
    raise PolygonError(f"Не удалось распарсить крипто-пару из '{ticker}'")

def last_trade_equity(ticker: str) -> float:
    """Последняя цена трейда по акции."""
    url = f"{BASE}/v2/last/trade/{ticker.upper()}"
    with httpx.Client(timeout=10) as client:
        r = client.get(url, headers=_headers())
        if r.status_code == 200:
            data = r.json()
            if 'results' in data and 'price' in data['results']:
                return float(data['results']['price'])
        # Fallback: возьмём последний бар агрегатов за минуту
        fr, to = _today_range_utc(48)
        url2 = f"{BASE}/v2/aggs/ticker/{ticker.upper()}/range/1/minute/{fr}/{to}?adjusted=true&sort=desc&limit=1"
        r2 = client.get(url2, headers=_headers())
        if r2.status_code == 200:
            data2 = r2.json()
            res = (data2 or {}).get("results") or []
            if res:
                return float(res[0].get("c"))
    raise PolygonError(f"Не удалось получить цену {ticker}: {r.text if 'r' in locals() else ''}")

def last_trade_crypto(pair: str) -> float:
    """Последняя цена трейда по крипто-паре."""
    base, quote = _norm_crypto_pair(pair)
    # Документация: /v1/last/crypto/{from}/{to}
    url = f"{BASE}/v1/last/crypto/{base}/{quote}"
    with httpx.Client(timeout=10) as client:
        r = client.get(url, headers=_headers())
        if r.status_code == 200:
            data = r.json()
            # форматы отличаются: try data['last']['price'] or data['lastTrade']['price']
            price = None
            if isinstance(data, dict):
                if 'last' in data and isinstance(data['last'], dict):
                    price = data['last'].get('price')
                if not price and 'lastTrade' in data and isinstance(data['lastTrade'], dict):
                    price = data['lastTrade'].get('price')
            if price:
                return float(price)
        # Fallback: агрегаты
        fr, to = _today_range_utc(72)
        xticker = f"X:{base}{quote}"
        url2 = f"{BASE}/v2/aggs/ticker/{xticker}/range/1/minute/{fr}/{to}?sort=desc&limit=1"
        r2 = client.get(url2, headers=_headers())
        if r2.status_code == 200:
            data2 = r2.json()
            res = (data2 or {}).get("results") or []
            if res:
                return float(res[0].get("c"))
    raise PolygonError(f"Не удалось получить цену {pair}: {r.text if 'r' in locals() else ''}")

def get_last_price(asset_class: str, ticker: str) -> float:
    if asset_class == "equity":
        return last_trade_equity(ticker)
    if asset_class == "crypto":
        return last_trade_crypto(ticker)
    raise PolygonError(f"Неизвестный класс актива: {asset_class}")

import requests
import os
import time
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation

# Para birimleri (güncel Steam market currency ID'leri)
CURRENCY_MAP = {
    'usd': {'id': 1,  'symbol': '$',   'name': 'USD'},
    'eur': {'id': 3,  'symbol': '€',   'name': 'EUR'},
    'try': {'id': 32, 'symbol': '₺',   'name': 'TRY'},
    'rub': {'id': 5,  'symbol': '₽',   'name': 'RUB'},
    # İstersen ekle: gbp:2, cad:4 vs.
}

def parse_price(price_str: str) -> Decimal:
    """ '$12.34' veya '1 234,56 €' gibi string → Decimal """
    if not price_str or price_str in ('—', 'Fiyat yok', 'N/A'):
        return Decimal('0')
    # Rakam + . , boşluk hariç her şeyi temizle
    cleaned = ''.join(c for c in price_str if c.isdigit() or c in '.,')
    cleaned = cleaned.replace(',', '.').replace(' ', '')
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return Decimal('0')


def get_price(item_name: str, currency_id: int, price_cache: dict) -> tuple[str, Decimal]:
    if item_name in price_cache:
        return price_cache[item_name]

    url = "https://steamcommunity.com/market/priceoverview/"
    params = {
        'appid': 730,
        'currency': currency_id,
        'market_hash_name': item_name,
    }
    try:
        time.sleep(1.3)  # Rate limit için güvenli bekleme
        r = requests.get(url, params=params, timeout=12)
        if r.status_code != 200:
            price_cache[item_name] = ("Hata", Decimal('0'))
            return price_cache[item_name]

        data = r.json()
        if not data.get('success', False):
            price_cache[item_name] = ("Fiyat yok", Decimal('0'))
            return price_cache[item_name]

        lowest = data.get('lowest_price', '—')
        parsed = parse_price(lowest)
        price_cache[item_name] = (lowest, parsed)
        return lowest, parsed

    except Exception as e:
        print(f"  ! Hata ({item_name}): {e}")
        price_cache[item_name] = ("N/A", Decimal('0'))
        return price_cache[item_name]


def main():
    parser = argparse.ArgumentParser(description="Steam CS2 Envanter Değer Hesaplayıcı")
    parser.add_argument('--currency', choices=['usd', 'try', 'eur', 'rub'], default='usd',
                        help="Para birimi: usd (default), try, eur, rub")
    args = parser.parse_args()

    curr = CURRENCY_MAP[args.currency]
    currency_id = curr['id']
    symbol = curr['symbol']
    curr_name = curr['name']

    steam_id = os.getenv('STEAM_ID') or input("Steam ID'nizi girin (7656119...): ").strip()
    if not steam_id or len(steam_id) < 10:
        print("Geçerli Steam ID girin!")
        return

    inv_url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=english&count=5000"

    try:
        print("Envanter çekiliyor...")
        inv_res = requests.get(inv_url, timeout=15)
        inv_res.raise_for_status()
        data = inv_res.json()
    except Exception as e:
        print(f"Envanter alınamadı: {e}")
        return

    desc_map = {d['classid']: d['market_hash_name'] for d in data.get('descriptions', [])}
    items = [desc_map.get(a['classid']) for a in data['assets'] if a['classid'] in desc_map]
    inventory_counts = Counter(item for item in items if item)  # Boşları at

    if not inventory_counts:
        print("Envanter boş veya çekilemedi.")
        return

    price_cache = {}  # Cache: isim → (str fiyat, Decimal fiyat)
    total_value = Decimal('0')

    print("\n" + "═" * 85)
    print(f"{'EŞYA ADI (ADET)':<50} | {'BİRİM FİYAT':<18} | {'TOPLAM':<15}")
    print("─" * 85)

    for name, count in sorted(inventory_counts.items()):
        price_str, price_dec = get_price(name, currency_id, price_cache)
        subtotal = price_dec * count
        total_value += subtotal

        count_display = f"({count})" if count > 1 else ""
        line = f"{name} {count_display:<8} | {price_str:<18} | {symbol}{subtotal:,.2f}"
        # Türkçe format: nokta → boşluk, virgül → nokta
        formatted = line.replace(',', ' ').replace('.', ',')
        print(formatted[:84])  # Çok uzun isimleri kırp

    print("═" * 85)
    total_formatted = f"{symbol}{total_value:,.2f}".replace(',', ' ').replace('.', ',')
    print(f"                    TOPLAM ENVANTER DEĞERİ ({curr_name}):  {total_formatted}")
    print(f"\nNot: {len(inventory_counts)} farklı eşya • {len(price_cache)} fiyat sorgusu yapıldı • Cache kullanıldı")

    if len(items) >= 4900:
        print("UYARI: 5000 eşya limitine yaklaşıldı, bazı eşyalar eksik olabilir (Steam API sınırlaması)")


if __name__ == "__main__":
    main()

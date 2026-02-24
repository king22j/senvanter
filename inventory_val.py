import requests
import os
import time
from collections import Counter

def clean_price(price_str):
    # "15,50 TL" veya "CLP$ 500" gibi metinleri sayıya çevirir
    if not price_str or "Fiyat" in price_str:
        return 0.0
    try:
        # Sadece rakamları ve virgül/noktayı tut
        cleaned = "".join(c for c in price_str if c.isdigit() or c in ",.")
        cleaned = cleaned.replace(",", ".")
        # Birden fazla nokta varsa (binlik ayırıcı gibi) sonuncusunu tut
        if cleaned.count('.') > 1:
            parts = cleaned.split('.')
            cleaned = "".join(parts[:-1]) + "." + parts[-1]
        return float(cleaned)
    except:
        return 0.0

def get_price_info(item_name):
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {'appid': 730, 'currency': 25, 'market_hash_name': item_name}
    try:
        time.sleep(1.2) # Ban yememek için şart
        r = requests.get(url, params=params)
        if r.status_code == 200:
            return r.json().get('lowest_price', '0')
    except:
        return "0"
    return "0"

def start():
    steam_id = os.getenv('STEAM_ID', 'ID_YAZ').strip()
    inv_url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=turkish&count=500"
    
    try:
        res = requests.get(inv_url)
        data = res.json()
        desc_map = {d['classid']: d['market_hash_name'] for d in data.get('descriptions', [])}
        items = [desc_map.get(a['classid']) for a in data['assets'] if a['classid'] in desc_map]
        
        inventory_counts = Counter(items)
        total_inventory_value = 0.0
        
        print("\n" + "="*70)
        print(f"{'EŞYA ADI (ADET)':<40} | {'BİRİM':<12} | {'TOPLAM':<12}")
        print("-" * 70)

        for name, count in sorted(inventory_counts.items()):
            price_str = get_price_info(name)
            unit_price = clean_price(price_str)
            item_total = unit_price * count
            total_inventory_value += item_total
            
            # Satır yazdırma
            display_name = f"{name} ({count})"[:39]
            print(f"{display_name:<40} | {price_str:<12} | {item_total:>8.2f}")

        print("-" * 70)
        print(f"{'GENEL TOPLAM DEĞER':<40} | {' ':12} | {total_inventory_value:>8.2f} TL")
        print("="*70)

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    start()

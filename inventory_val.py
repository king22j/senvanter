import requests
import os
import time
from collections import Counter

def get_price(item_name):
    # Her eşya için piyasa fiyatını çeken fonksiyon
    url = f"https://steamcommunity.com/market/priceoverview/"
    params = {
        'appid': 730,
        'currency': 25, # 25 = TL (Dolar istersen 1 yap)
        'market_hash_name': item_name
    }
    try:
        # Steam'i yormamak için kısa bir bekleme
        time.sleep(1.1) 
        r = requests.get(url, params=params)
        if r.status_code == 200:
            data = r.json()
            return data.get('lowest_price', 'Fiyat Bulunamadı')
    except:
        return "N/A"
    return "N/A"

def start():
    steam_id = os.getenv('STEAM_ID', 'BURAYA_ID_YAZ').strip()
    inv_url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=turkish&count=500"
    
    try:
        inv_res = requests.get(inv_url)
        if inv_res.status_code != 200:
            print(f"Envanter çekilemedi. Hata: {inv_res.status_code}")
            return

        data = inv_res.json()
        desc_map = {d['classid']: d['market_hash_name'] for d in data.get('descriptions', [])}
        items = [desc_map.get(a['classid']) for a in data['assets'] if a['classid'] in desc_map]
        
        inventory_counts = Counter(items)
        
        print("\n" + "="*65)
        print(f"{'EŞYA ADI (ADET)':<40} | {'BİRİM FİYAT':<15}")
        print("-" * 65)

        for name, count in sorted(inventory_counts.items()):
            price = get_price(name) # Her benzersiz eşya için 1 kez fiyat sorar
            print(f"{name} ({count})".strip()[:39].ljust(40) + f" | {price}")

        print("="*65)
        print("Not: Steam limitlerine takılmamak için fiyatlar 1 sn arayla çekiliyor.")

    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    start()

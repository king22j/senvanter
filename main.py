import requests
from collections import Counter

def get_inventory_value(steam_id):
    # Steam envanter API URL'si (CS2/CS:GO için appid: 730)
    url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=turkish&count=5000"
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data or 'descriptions' not in data:
            print("Envanter alınamadı. Profilin gizli olmadığından emin ol.")
            return

        # Eşya isimlerini ve fiyatlarını eşleştirmek için bir sözlük
        item_names = [item['market_hash_name'] for item in data['assets']]
        # Aynı isimdeki eşyaları say (Örn: {'Clutch Case': 10})
        inventory_counts = Counter(item_names)
        
        print(f"\n--- Güncel Envanter Durumu ---")
        print(f"{'Eşya Adı':<40} | {'Miktar':<10}")
        print("-" * 55)

        total_items = 0
        for name, count in inventory_counts.items():
            print(f"{name:<40} ({count})")
            total_items += count

        print("-" * 55)
        print(f"Toplam Eşya Sayısı: {total_items}")
        print("Not: Anlık fiyat çekimi Steam API limitlerine takılmamak için bu versiyonda isim bazlı gruplanmıştır.")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

# Kendi SteamID64 numaranı buraya yaz
my_steam_id = "BURAYA_STEAM_ID_YAZ" 
get_inventory_value(my_steam_id)

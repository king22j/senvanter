import requests
from collections import Counter
import os

def get_inventory_value(steam_id):
    if not steam_id or steam_id == "BURAYA_STEAM_ID_YAZ":
        print("Hata: Geçerli bir SteamID bulunamadı! Lütfen kodu düzenleyin veya GitHub Secrets kullanın.")
        return

    # Steam envanter API URL'si (CS2 için appid: 730, contextid: 2)
    url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=turkish&count=5000"
    
    try:
        response = requests.get(url)
        # Steam bazen çok sık sorgu atınca 429 (Too Many Requests) döner
        if response.status_code != 200:
            print(f"Steam API hatası: {response.status_code}. Envanter gizli olabilir veya çok sık sorgu attınız.")
            return

        data = response.json()
        
        # 'assets' gerçek eşyaları, 'descriptions' ise o eşyaların isim/tür bilgilerini tutar
        if not data or 'assets' not in data or 'descriptions' not in data:
            print("Envanter verisi boş döndü. Profilinizi 'Public' yapın.")
            return

        # Asset ID'leri ile açıklamaları eşleştirmek için bir harita oluşturuyoruz
        # Çünkü 'assets' kısmında sadece ID'ler vardır, isimler 'descriptions' kısmındadır.
        descriptions = {d['classid']: d['market_hash_name'] for d in data['descriptions']}
        
        # Her bir varlığın ismini çekip listeye ekleyelim
        item_names = []
        for asset in data['assets']:
            classid = asset['classid']
            if classid in descriptions:
                item_names.append(descriptions[classid])

        # Aynı isimdeki eşyaları grupla (Senin istediğin kısım burası)
        inventory_counts = Counter(item_names)
        
        print(f"\n" + "="*60)
        print(f"{'EŞYA ADI':<45} | {'ADET':<10}")
        print("-" * 60)

        total_items = 0
        # Alfabetik sıralı listeleyelim
        for name in sorted(inventory_counts.keys()):
            count = inventory_counts[name]
            print(f"{name:<45} ({count})")
            total_items += count

        print("-" * 60)
        print(f"TOPLAM EŞYA SAYISI: {total_items}")
        print("="*60)

    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")

if __name__ == "__main__":
    # Önce GitHub Secrets'tan (ortam değişkeni) okumaya çalış
    # Eğer orada yoksa manuel yazılanı kullanır
    env_steam_id = os.getenv('STEAM_ID')
    
    if env_steam_id:
        my_steam_id = env_steam_id
    else:
        # GitHub'da çalıştırmayacaksan buraya kendi ID'ni tırnak içine yazabilirsin
        my_steam_id = "BURAYA_STEAM_ID_YAZ" 

    get_inventory_value(my_steam_id)

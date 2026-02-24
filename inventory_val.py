import requests
from collections import Counter
import os

def get_inventory():
    # ID'yi al ve temizle
    steam_id = os.getenv('STEAM_ID', 'BURAYA_ID_YAZ').strip()
    
    # 400 hatasını engellemek için en sade URL (Parametreleri azalttık)
    url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=turkish&count=100"
    
    try:
        # Sadece 1 kez istek atıyor
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"Steam hatası: {response.status_code}. ID yanlis olabilir veya profil gizli.")
            return

        data = response.json()
        
        if not data or 'assets' not in data:
            print("Envanter bos veya veri gelmedi.")
            return

        # Esya isimlerini çek
        descriptions = {d['classid']: d['market_hash_name'] for d in data.get('descriptions', [])}
        
        # Gruplandirma yap
        items = []
        for asset in data['assets']:
            name = descriptions.get(asset['classid'], "Bilinmeyen Esya")
            items.append(name)
        
        envanter = Counter(items)

        # Temiz cikti
        print("\n--- ENVANTER OZETI ---")
        for ad, adet in sorted(envanter.items()):
            print(f"{ad} ({adet})")
        
        print(f"\nToplam: {len(items)} parca esya.")

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    get_inventory()

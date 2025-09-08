# Bu betik, otomasyon (CI/CD) ortamlarında çalışacak şekilde tasarlanmıştır.
# Tüm yayın linklerini çeker ve 'yayin_linkleri.json' adında bir dosyaya kaydeder.

import requests
from bs4 import BeautifulSoup
import time
import hashlib
import json
import os # Ortam değişkenlerini okumak için

# --- YAPILANDIRMA ---
API_BASE_URL = "https://mainapi.kakirikocdn.store" 
# Gizli anahtar, GitHub Actions secrets'tan ortam değişkeni olarak alınacak.
SECRET_KEY = os.environ.get("SECRET_KEY")
# --- YAPILANDIRMA SONU ---

def kanallari_getir(url):
    """Sitedeki mevcut tüm kanalları ve ID'lerini çeker."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        kanallar = {}
        # Hem maçları hem de sabit kanalları buluyoruz
        mac_etiketleri = soup.find_all('a', class_='single-match')
        kanal_etiketleri = soup.find_all('div', class_='single-channel')

        for etiket in mac_etiketleri + kanal_etiketleri:
            stream_id = etiket.get('data-stream')
            mac_adi = etiket.get('data-name')
            if stream_id and mac_adi:
                kanallar[mac_adi.strip()] = stream_id.strip()
        
        return kanallar
    except requests.exceptions.RequestException as e:
        print(f"Hata: Kanal listesi alınamadı. {e}")
        return None

def m3u8_linki_uret(kanal_id):
    """Belirtilen kanal ID'si için güvenli .m3u8 linkini üretir."""
    if not SECRET_KEY:
        print("Hata: 'SECRET_KEY' ortam değişkeni bulunamadı veya ayarlanmamış.")
        return None

    # Linkin 1 saat (3600 saniye) sonra geçersiz olmasını sağlıyoruz
    expire_timestamp = int(time.time()) + 3600
    yol = f"/test/{kanal_id}/"
    
    # Token'ı oluşturacak metni birleştiriyoruz
    hash_metni = f"{SECRET_KEY}{yol}{expire_timestamp}"
    token = hashlib.md5(hash_metni.encode('utf-8')).hexdigest()
    
    # Tam .m3u8 linkini oluşturuyoruz
    tam_link = f"{API_BASE_URL}{yol}chunklist.m3u8?token={token}&expire={expire_timestamp}"
    return tam_link

if __name__ == "__main__":
    site_url = "https://84padisahbettv.com"
    print(f"'{site_url}' adresinden kanal listesi alınıyor...")
    
    kanallar = kanallari_getir(site_url)
    
    if kanallar:
        tum_yayinlar = []
        print(f"{len(kanallar)} adet kanal/maç bulundu. Linkler üretiliyor...")
        
        for ad, kimlik in kanallar.items():
            link = m3u8_linki_uret(kimlik)
            if link:
                tum_yayinlar.append({
                    "ad": ad,
                    "kimlik": kimlik,
                    "yayin_linki": link
                })
        
        # Sonuçları JSON dosyasına yaz
        cikis_dosyasi = "yayin_linkleri.json"
        with open(cikis_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(tum_yayinlar, f, ensure_ascii=False, indent=4)
            
        print(f"Tüm yayın linkleri başarıyla '{cikis_dosyasi}' dosyasına yazıldı.")
    else:
        print("İşlem başarısız oldu. Hiç kanal bulunamadı.")
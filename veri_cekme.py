# Bu betik, bir web sitesinin arka plan API mantığını taklit ederek
# doğrudan canlı yayın (.m3u8) linkleri üretir.

import requests
from bs4 import BeautifulSoup
import time
import hashlib
import json

# --- YAPILANDIRMA ---
# BU DEĞERLERİN, SİTENİN JAVASCRIPT DOSYALARI İNCELENEREK DOĞRULANMASI GEREKİR.
# Bu bir varsayımdır ve sitenin JS kodlarından bulunmalıdır.
API_BASE_URL = "https://mainapi.kakirikocdn.store" 
# Bu anahtar, token üretimindeki en kritik parçadır. 
# Genellikle main.js gibi dosyalarda bulunur ve dikkatlice aranmalıdır.
SECRET_KEY = "BURAYA_JS_DOSYASINDAN_BULUNAN_GİZLİ_ANAHTAR_GELECEK" 
# --- YAPILANDIRMA SONU ---

def kanallari_getir(url):
    """Sitedeki mevcut tüm kanalları ve ID'lerini çeker."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        kanallar = {}
        # Hem maçları hem de sabit kanalları bulmaya çalışalım
        mac_etiketleri = soup.find_all('a', class_='single-match')
        kanal_etiketleri = soup.find_all('div', class_='single-channel')

        for etiket in mac_etiketleri + kanal_etiketleri:
            # data-stream veya data-id gibi benzersiz bir kimlik arıyoruz
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
    
    if SECRET_KEY == "BURAYA_JS_DOSYASINDAN_BULUNAN_GİZLİ_ANAHTAR_GELECEK":
        print("\nUYARI: Betiğin çalışması için 'SECRET_KEY' değişkenini güncellemelisiniz.")
        print("Bu anahtar, sitenin JavaScript dosyaları incelenerek bulunabilir.\n")
        return None

    # Linkin 1 saat (3600 saniye) sonra geçersiz olmasını sağlıyoruz.
    expire_timestamp = int(time.time()) + 3600
    
    # Kanal yolunu oluşturuyoruz (örneğin: /test/Bein-Sports-1/)
    # Sitenin JS'sindeki yapıya göre bu yol formatı değişebilir.
    yol = f"/test/{kanal_id}/"

    # Token'ı oluşturacak metni birleştiriyoruz.
    # Sıralama çok önemlidir ve JS dosyasındaki ile aynı olmalıdır.
    hash_metni = f"{SECRET_KEY}{yol}{expire_timestamp}"

    # MD5 hash'ini hesaplıyoruz.
    token = hashlib.md5(hash_metni.encode('utf-8')).hexdigest()

    # Tam .m3u8 linkini oluşturuyoruz.
    tam_link = f"{API_BASE_URL}{yol}chunklist.m3u8?token={token}&expire={expire_timestamp}"
    
    return tam_link

if __name__ == "__main__":
    site_url = "https://84padisahbettv.com"
    print(f"'{site_url}' adresinden kanal listesi alınıyor...")
    
    kanallar = kanallari_getir(site_url)
    
    if kanallar:
        print("Kullanılabilir Kanallar/Maçlar Bulundu:\n")
        
        # Kanalları listelemek için numaralandırma
        kanal_listesi = list(kanallar.items())
        for i, (ad, kimlik) in enumerate(kanal_listesi):
            print(f"{i + 1}: {ad} (ID: {kimlik})")
            
        try:
            secim = int(input("\nLinkini üretmek istediğiniz yayının numarasını girin: ")) - 1
            if 0 <= secim < len(kanal_listesi):
                secilen_ad, secilen_id = kanal_listesi[secim]
                print(f"\n'{secilen_ad}' için link üretiliyor...")
                
                m3u8_linki = m3u8_linki_uret(secilen_id)
                
                if m3u8_linki:
                    print("\n--- ÜRETİLEN DOĞRUDAN YAYIN LİNKİ ---")
                    print(m3u8_linki)
                    print("\nBu linki VLC Player gibi oynatıcılarda açabilirsiniz.")
            else:
                print("Geçersiz numara girdiniz.")
        except ValueError:
            print("Lütfen sadece sayı giriniz.")
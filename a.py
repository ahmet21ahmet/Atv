import asyncio
from playwright.async_api import async_playwright

URL = "https://www.diziyou16.com/"
OUTPUT_FILE = "diziyou_playwright.html"

async def main():
    """
    Belirtilen URL'ye gider, Cloudflare korumasını geçer ve sayfanın
    HTML içeriğini bir dosyaya kaydeder.
    """
    print(f"🚀 Playwright başlatılıyor ve {URL} adresine gidiliyor...")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()

            # İsteğe bağlı referer ayarı
            await page.set_extra_http_headers({
                "Referer": "https://www.google.com/"
            })

            print("⏳ Sayfa yükleniyor, lütfen bekleyin...")
            await page.goto(URL, timeout=90000, wait_until="domcontentloaded")  # Timeout 90 saniyeye çıkarıldı

            print("🔄 Sayfa içeriği alınıyor...")
            html = await page.content()

            print(f"✅ HTML içeriği başarıyla alındı. '{OUTPUT_FILE}' dosyasına yazılıyor.")
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(html)
            print("💾 Dosya başarıyla kaydedildi.")

        except Exception as e:
            print(f"❌ Bir hata oluştu: {e}")
        finally:
            if 'browser' in locals() and browser:
                await browser.close()
            print("🚪 Tarayıcı kapatıldı.")

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
from playwright.async_api import async_playwright

URL = "https://streambtw.com"

async def main():
    async with async_playwright() as p:
        # Chromium, Firefox veya WebKit seçebilirsin
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

        print("⏳ Sayfa yükleniyor...")
        await page.goto(URL, timeout=60000)  # 60 saniye timeout

        # Cloudflare challenge'ı geçtikten sonra body alınır
        html = await page.content()

        print("✅ Sayfa yüklendi, HTML kaynağı aşağıda:\n")
        print(html)

        # İstersen dosyaya kaydet
        with open("dizibox_playwright.html", "w", encoding="utf-8") as f:
            f.write(html)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
from playwright.sync_api import sync_playwright
import sys

def test_playwright_link(url):
    print(f"Testing terminal-level connectivity to {url} with Playwright (Relaxed wait)...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
            page = context.new_page()
            # Use domcontentloaded instead of networkidle
            response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print(f"Status: {response.status}")
            
            # Take a screenshot to debug
            page.screenshot(path=".tmp/debug_airundown.png")
            print("Screenshot saved to .tmp/debug_airundown.png")
            
            if response.status == 200:
                print(f"✅ Success with Playwright!")
                browser.close()
                return True
            else:
                print(f"❌ Failed with Playwright. Status: {response.status}")
                browser.close()
                return False
    except Exception as e:
        print(f"❌ Error with Playwright: {e}")
        return False

if __name__ == "__main__":
    url = "https://www.therundown.ai/archive"
    if not test_playwright_link(url):
        sys.exit(1)

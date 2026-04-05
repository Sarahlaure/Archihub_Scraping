from playwright.sync_api import sync_playwright
import sys

def inspect_html(url):
    print(f"Inspecting HTML of {url}...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Print first 2000 chars of body
            content = page.content()
            print("--- HTML CONTENT SNIPPET ---")
            print(content[:2000])
            print("--- END SNIPPET ---")
            
            # Find all links that look like articles
            links = page.query_selector_all("a")
            print(f"Found {len(links)} links. Top 10 suspicious ones:")
            count = 0
            for link in links:
                href = link.get_attribute("href")
                if href and ("/p/" in href or "/post/" in href):
                    print(f"Text: {link.inner_text().strip()[:50]} | Href: {href}")
                    count += 1
                if count >= 10: break

            browser.close()
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    inspect_html("https://www.therundown.ai/archive")

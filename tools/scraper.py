import json
import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests
from dateutil import parser as date_parser
import datetime
COMPETITIONS_FILE = "public/competitions.json"
JOBS_FILE = "public/jobs.json"
NEWS_FILE = "public/news.json"

def fetch_html(url, use_requests=False):
    """Fetches the HTML content of a given URL, falling back to requests if Playwright fails."""
    print(f"Fetching {url}...")
    html_content = ""
    
    # Try requests first if explicitly asked
    if use_requests:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                print(f"Success with requests for {url}")
                return r.text
        except Exception as e:
            print(f"Requests failed for {url}: {e}")

    # Otherwise use Playwright
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            # Navigate with a shorter timeout and a networkidle check
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            # Give JS a moment to render
            page.wait_for_timeout(3000)
            html_content = page.content()
            browser.close()
    except Exception as e:
        print(f"Error fetching {url} with Playwright: {e}")
        # Final fallback to requests
        if not use_requests:
            try:
                print(f"Falling back to requests for {url}...")
                headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
                r = requests.get(url, headers=headers, timeout=15)
                html_content = r.text
            except Exception as inner_e:
                print(f"Fallback also failed: {inner_e}")
                
    return html_content

def parse_competitions_archi(html):
    print("Parsing competitions.archi...")
    competitions = []
    if not html: return competitions
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all(lambda tag: tag.has_attr('class') and any('competition' in c for c in tag['class']) and tag.name in ['div', 'li'])
    seen_links = set()
    for item in items:
        link_el = item.find('a', href=True)
        if not link_el: continue
        link = link_el['href']
        if link in seen_links: continue
        seen_links.add(link)
        title_el = item.find(['h2', 'h3', 'h4'])
        title = title_el.get_text(strip=True) if title_el else link_el.get_text(strip=True)
        if not title: continue
        text = item.get_text(separator=' ', strip=True)
        deadline = "Unknown"
        deadline_iso = None
        if "Submission:" in text:
            # Clean up the text first to make date parsing more reliable
            text_clean = text.replace('\n', ' ').replace('\r', '')
            deadline_part = text_clean.split("Submission:", 1)[1]
            deadline = deadline_part.split("Registration:")[0].strip() if "Registration:" in deadline_part else deadline_part[:30]
            
            try:
                # Try to parse the date. We use fuzzy=True to ignore surrounding text.
                # However, architecturecompetitions.com and competitions.archi sometimes use weird formats
                # Best effort parsing:
                parsed_date = date_parser.parse(deadline, fuzzy=True)
                deadline_iso = parsed_date.isoformat()
            except Exception:
                pass
                
        competitions.append({
            "title": title,
            "link": link,
            "deadline": deadline,
            "deadline_iso": deadline_iso,
            "description": text[:200] + "..." if len(text) > 200 else text,
            "type": "competition"
        })
    return competitions

def parse_architecturecompetitions_com(html):
    print("Parsing architecturecompetitions.com...")
    competitions = []
    if not html: return competitions
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select('div.item a[href], div.row a[href]')
    seen_links = set()
    for link_el in links:
        link = link_el['href']
        if not link.startswith('http'):
            link = "https://architecturecompetitions.com" + link if link.startswith('/') else "https://architecturecompetitions.com/" + link
        if any(exclude in link for exclude in ['/login', '/launch', 'an.pro']): continue
        if link in seen_links: continue
        seen_links.add(link)
        title_el = link_el.find(['h2', 'h3', 'h4', 'strong'])
        title = title_el.get_text(strip=True) if title_el else link_el.get_text(strip=True)
        if len(title) > 10:
            text = link_el.get_text(separator=' ', strip=True)
            competitions.append({
                "title": title,
                "link": link,
                "deadline": "Unknown",
                "description": text[:200] + "..." if len(text) > 200 else text,
                "type": "competition"
            })
    return competitions

def parse_riba_jobs(html):
    print("Parsing jobs.architecture.com...")
    jobs = []
    if not html: return jobs
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all('a', href=lambda h: h and '/job/' in h)
    seen_links = set()
    for link_el in links:
        link = "https://jobs.architecture.com" + link_el['href'] if link_el['href'].startswith('/') else link_el['href']
        if link in seen_links: continue
        seen_links.add(link)
        
        text_content = link_el.get_text(separator=' | ', strip=True)
        parts = text_content.split(' | ')
        if len(parts) >= 2:
            title = parts[0]
            location = parts[1]
        else:
            title = text_content
            location = "Unknown"
            
        if len(title) > 5:
            jobs.append({
                "title": title,
                "link": link,
                "location": location,
                "description": text_content,
                "type": "job"
            })
    return jobs

def parse_dezeen_news(html):
    print("Parsing dezeen.com news...")
    news = []
    if not html: return news
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all("article")
    seen_links = set()
    for item in items:
        link_el = item.find('a', href=True)
        if not link_el: continue
        link = link_el['href']
        if link in seen_links: continue
        seen_links.add(link)
        
        title_el = item.find(['h1', 'h2', 'h3'])
        title = title_el.get_text(strip=True) if title_el else link_el.get_text(strip=True)
        
        if len(title) > 10:
            text = item.get_text(separator=' ', strip=True)
            news.append({
                "title": title,
                "link": link,
                "date": "Recent",
                "description": text[:200] + "..." if len(text) > 200 else text,
                "type": "news"
            })
    return news

def save_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(data)} items to {filepath}")

def run_scraper():
    # 1. Competitions
    comps1 = parse_competitions_archi(fetch_html("https://competitions.archi/"))
    comps2 = parse_architecturecompetitions_com(fetch_html("https://architecturecompetitions.com/", use_requests=True))
    
    unique_comps = {c['link']: c for c in comps1 + comps2}.values()
    save_json(list(unique_comps), COMPETITIONS_FILE)

    # 2. Jobs
    jobs = parse_riba_jobs(fetch_html("https://jobs.architecture.com/", use_requests=True))
    save_json(jobs, JOBS_FILE)

    # 3. News
    news = parse_dezeen_news(fetch_html("https://www.dezeen.com/architecture/"))
    save_json(news, NEWS_FILE)

if __name__ == "__main__":
    run_scraper()

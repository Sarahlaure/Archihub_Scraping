import sys
import io
# Force UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import os
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests
from dateutil import parser as date_parser
import datetime

COMPETITIONS_FILE = "public/competitions.json"
JOBS_FILE = "public/jobs.json"
NEWS_FILE = "public/news.json"

# ─── Patterns to identify non-competition links on architecturecompetitions.com ───
# These are navigation, participant profiles, blog posts, etc.
ARCH_COM_JUNK_PATTERNS = [
    r'from .+!$',           # participant profiles: "Minseong Kim from South Korea!"
    r'\bfrom\b.+\b(United States|France|Germany|China|UK|United Kingdom|Poland|Romania|Spain|Italy|Australia|Canada|Japan|Brazil|India|Turkey|Portugal|Netherlands|Belgium|Austria|Switzerland|Sweden|Denmark|Norway|Finland|Korea|Egypt|Jordan|Indonesia|Vietnam|Ukraine|Armenia|Slovakia|Macedonia|Cyprus|Hungary|Peru|Ethiopia|New Zealand|Ireland|Thailand|Georgia|Mexico|Argentina|Chile|Czech|Serbia|Croatia|Greece|Iran|Pakistan|Israel|Philippines|Malaysia|Singapore|Taiwan|Lebanon|UAE|Russia|Kazakhstan|Cuba|Morocco|Tunisia|Algeria|Ghana|Nigeria|Kenya|Colombia|Ecuador|Bolivia|Paraguay|Uruguay|Venezuela|Dominican|Costa Rica|Guatemala|Honduras|El Salvador|Nicaragua|Panama|Jamaica|Trinidad|Haiti|Barbados|Bahamas|Sri Lanka|Bangladesh|Nepal|Myanmar|Cambodia|Laos|Fiji|Papua|Zimbabwe|Zambia|Tanzania|Uganda|Rwanda|Cameroon|Senegal|Ivory|Mali|Burkina|Mozambique|Madagascar|Angola|Namibia|Botswana|Lesotho|Eswatini|Djibouti|Eritrea|Somalia|Sudan|South Sudan|Libya|Tunisia|Syria|Iraq|Kuwait|Qatar|Bahrain|Oman|Yemen|Afghanistan|Tajikistan|Kyrgyzstan|Uzbekistan|Turkmenistan|Azerbaijan|Moldova|Belarus|Lithuania|Latvia|Estonia|Slovenia|Montenegro|Bosnia|Albania|Kosovo|North Macedonia|Cyprus|Malta|Luxembourg|Iceland|Liechtenstein|Monaco|San Marino|Vatican|Andorra|Montenegro)\b',
    r'^(All open|Housing crisis|Small-scale|Competitions results|News|Blog|University rankings|Presentation review|Upload panel|Video lectures|Publish a book|Privacy policy|Website terms|Government agencies|Non-profit|Real estate developers|Educational institutions|Hospitality industries|Cultural institutions|Construction product brands|Download brief|KYC|competition integrity)',
    r'^\d{1,2}[,.]?\d{0,3} design projects',
    r'^(Login|Register|Sign|About|Contact|FAQ|Help|Support)',
]

def _is_junk_competition_title(title: str) -> bool:
    """Returns True if the title is clearly NOT a real competition."""
    for pattern in ARCH_COM_JUNK_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            return True
    # Also exclude very short "titles" that are likely nav items
    if len(title) < 8:
        return True
    return False


def fetch_html(url, use_requests=False, wait_selector=None):
    """Fetches the HTML content of a given URL, with optional Playwright wait_for_selector."""
    print(f"Fetching {url}...")
    html_content = ""

    if use_requests:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }
            r = requests.get(url, headers=headers, timeout=25)
            if r.status_code == 200:
                print(f"  [OK] requests OK [{r.status_code}] for {url}")
                return r.text
            else:
                print(f"  [FAIL] requests got status {r.status_code} for {url}")
        except Exception as e:
            print(f"  [FAIL] requests failed for {url}: {e}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            if wait_selector:
                try:
                    page.wait_for_selector(wait_selector, timeout=15000)
                    print(f"  [OK] Selector '{wait_selector}' found")
                except Exception:
                    print(f"  [WARN] Selector '{wait_selector}' timed out -- continuing anyway")

            # Allow JS to finish rendering
            page.wait_for_timeout(3500)
            html_content = page.content()
            browser.close()
            print(f"  [OK] Playwright OK for {url}")
    except Exception as e:
        print(f"  [FAIL] Playwright error for {url}: {e}")
        if not use_requests:
            try:
                print(f"  [RETRY] Fallback to requests for {url}...")
                headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
                r = requests.get(url, headers=headers, timeout=20)
                html_content = r.text
            except Exception as inner_e:
                print(f"  [FAIL] Fallback also failed: {inner_e}")

    return html_content


def parse_competitions_archi(html):
    """Parse competitions.archi — reliable source with good date data."""
    print("Parsing competitions.archi...")
    competitions = []
    if not html:
        return competitions

    soup = BeautifulSoup(html, "html.parser")

    # competitions.archi wraps each competition in a tag with 'competition' in its CSS class
    items = soup.find_all(
        lambda tag: tag.has_attr("class")
        and any("competition" in c for c in tag["class"])
        and tag.name in ["div", "li", "article"]
    )

    seen_links = set()
    for item in items:
        link_el = item.find("a", href=True)
        if not link_el:
            continue
        link = link_el["href"]
        # Ensure absolute URL
        if link.startswith("/"):
            link = "https://competitions.archi" + link
        if link in seen_links:
            continue
        seen_links.add(link)

        title_el = item.find(["h2", "h3", "h4"])
        title = title_el.get_text(strip=True) if title_el else link_el.get_text(strip=True)
        if not title or len(title) < 5:
            continue

        text = item.get_text(separator=" ", strip=True)

        # Extract deadline
        deadline = "Unknown"
        deadline_iso = None
        if "Submission:" in text:
            text_clean = text.replace("\n", " ").replace("\r", "")
            deadline_part = text_clean.split("Submission:", 1)[1]
            deadline_raw = (
                deadline_part.split("Registration:")[0].strip()
                if "Registration:" in deadline_part
                else deadline_part[:40]
            )
            deadline = deadline_raw.strip()
            try:
                parsed_date = date_parser.parse(deadline, fuzzy=True)
                deadline_iso = parsed_date.isoformat()
            except Exception:
                pass

        # Build a clean description: skip the repeated header/metadata lines
        # Try to find content after "Type:" or "Prizes:" labels
        desc_text = text
        for marker in ["Type: Open", "Type: Student", "Type: Invited", "Prizes:"]:
            if marker in desc_text:
                parts = desc_text.split(marker, 1)
                if len(parts) > 1 and len(parts[1]) > 30:
                    desc_text = parts[1].strip()
                    break

        description = desc_text[:250] + "..." if len(desc_text) > 250 else desc_text

        competitions.append({
            "title": title,
            "link": link,
            "deadline": deadline,
            "deadline_iso": deadline_iso,
            "description": description,
            "type": "competition",
        })

    print(f"  >> Found {len(competitions)} competitions from competitions.archi")
    return competitions


def parse_architecturecompetitions_com(html):
    """Parse architecturecompetitions.com — only real competitions, skip nav/profiles."""
    print("Parsing architecturecompetitions.com...")
    competitions = []
    if not html:
        return competitions

    soup = BeautifulSoup(html, "html.parser")

    # Try the most specific selectors first — competition cards usually have an h2/h3
    # Strategy: find all links that are inside a card-like container and have a proper title
    seen_links = set()

    # Primary: look for competition cards with prize info or deadline
    # These are usually in .item, .card, .competition-item, or article tags
    card_selectors = [
        "article",
        ".competition-card",
        ".item",
        ".card",
        "[class*='competition']",
    ]

    candidate_links = []
    for sel in card_selectors:
        found = soup.select(f"{sel} a[href]")
        if found:
            candidate_links.extend(found)

    # Fallback: all links with href containing year-like pattern or euro sign
    if not candidate_links:
        candidate_links = soup.find_all("a", href=True)

    for link_el in candidate_links:
        href = link_el.get("href", "")
        # Normalise URL
        if not href.startswith("http"):
            if href.startswith("/"):
                href = "https://architecturecompetitions.com" + href
            else:
                href = "https://architecturecompetitions.com/" + href

        # Hard exclusions
        if any(
            excl in href
            for excl in [
                "/login",
                "/launch",
                "an.pro",
                "/privacy",
                "/legal",
                "/contact",
                "/about",
                "/register",
                "/news",
                "/blog",
                "/results",
                "/profile",
                "/reviews",
                "/videos",
                "/publishing",
                "/government",
                "/non-profit",
                "/real-estate",
                "/educational",
                "/hospitality",
                "/culture",
                "/brands",
                "/university",
                "/#",
                "/architecture-projects",
                "/buildner-and-architectureinfo",
                "-competition-participants-",  # participant profile pages
                "-competition-participants",
                "-green-award-competition-participants",
                "-student-award-competition-participants",
                "-1st-competition-participants",
                "-2nd-competition-participants",
                "-3rd-competition-participants",
            ]
        ):
            continue

        if href in seen_links:
            continue

        # Get the best title from the link context
        parent = link_el.parent
        title_el = link_el.find(["h2", "h3", "h4", "strong", "b"])
        if not title_el and parent:
            title_el = parent.find(["h2", "h3", "h4", "strong", "b"])

        if title_el:
            title = title_el.get_text(strip=True)
        else:
            title = link_el.get_text(strip=True)

        # Remove prize / number suffixes that get merged (e.g. "MICROHOME 2026100,000 € Prize")
        title = re.sub(r"\s*\d[\d,\.]+\s*[€$£]\s*Prize.*", "", title).strip()
        title = re.sub(r"\s*[\d,\.]+\s*[€$£].*Prize.*", "", title).strip()

        if not title or len(title) < 8:
            continue

        # Filter out junk
        if _is_junk_competition_title(title):
            continue

        seen_links.add(href)
        text = link_el.get_text(separator=" ", strip=True)
        description = text[:200] + "..." if len(text) > 200 else text

        competitions.append({
            "title": title,
            "link": href,
            "deadline": "Unknown",
            "deadline_iso": None,
            "description": description,
            "type": "competition",
        })

    print(f"  >> Found {len(competitions)} competitions from architecturecompetitions.com")
    return competitions


def parse_riba_jobs(html):
    """Parse jobs.architecture.com — handles SPA rendering via Playwright."""
    print("Parsing jobs.architecture.com...")
    jobs = []
    if not html:
        return jobs

    soup = BeautifulSoup(html, "html.parser")

    # jobs.architecture.com renders job cards dynamically
    # Job links typically contain /job/ in the path
    links = soup.find_all("a", href=lambda h: h and "/job/" in h)

    if not links:
        # Fallback: try broader link detection for SPA
        links = soup.find_all("a", href=lambda h: h and h.startswith("/job"))

    seen_links = set()
    for link_el in links:
        raw_href = link_el.get("href", "")
        if raw_href.startswith("/"):
            link = "https://jobs.architecture.com" + raw_href
        elif raw_href.startswith("http"):
            link = raw_href
        else:
            continue

        if link in seen_links:
            continue
        seen_links.add(link)

        # Extract structured content from the job card
        text_content = link_el.get_text(separator=" | ", strip=True)
        parts = [p.strip() for p in text_content.split(" | ") if p.strip()]

        title = parts[0] if parts else text_content
        location = parts[1] if len(parts) >= 2 else "Location not specified"
        salary_info = parts[2] if len(parts) >= 3 else ""

        # Skip if title is too short or looks like a label
        if len(title) < 6:
            continue

        description = text_content[:300] if text_content else title

        jobs.append({
            "title": title,
            "link": link,
            "location": location,
            "salary": salary_info,
            "description": description,
            "type": "job",
        })

    print(f"  >> Found {len(jobs)} jobs from jobs.architecture.com")
    return jobs


def parse_dezeen_news(html):
    """Parse dezeen.com/architecture — extracts real article titles (not category tags)."""
    print("Parsing dezeen.com news...")
    news = []
    if not html:
        return news

    soup = BeautifulSoup(html, "html.parser")
    articles = soup.find_all("article")
    seen_links = set()

    for item in articles:
        link_el = item.find("a", href=True)
        if not link_el:
            continue

        href = link_el.get("href", "")
        # Ensure absolute URL
        if href.startswith("/"):
            href = "https://www.dezeen.com" + href
        if not href.startswith("http"):
            continue

        if href in seen_links:
            continue
        seen_links.add(href)

        # ── Dezeen-specific title extraction ──
        # The article tag usually has:
        # 1. A category <span> or <p> (short, e.g., "Renovations")
        # 2. The real title in an <h2> or <h3> (longer, descriptive)
        # Strategy: find the heading element that has the longest meaningful text
        title = None

        # Try headings first (most reliable)
        for heading_tag in ["h2", "h3", "h4", "h1"]:
            candidate = item.find(heading_tag)
            if candidate:
                candidate_text = candidate.get_text(strip=True)
                # Real titles are longer than category labels
                if len(candidate_text) > 20:
                    title = candidate_text
                    break

        # If no heading found, look for the most descriptive link text
        if not title:
            # Find all <a> elements with long text (not category pills)
            for a_el in item.find_all("a", href=True):
                a_text = a_el.get_text(strip=True)
                if len(a_text) > 30:
                    title = a_text
                    break

        # Final fallback
        if not title:
            title = link_el.get_text(strip=True)

        if len(title) < 10:
            continue

        # ── Build clean description ──
        # Skip navigation-like text and extract meaningful content
        all_text = item.get_text(separator=" ", strip=True)

        # Remove the category prefix if it's duplicated at the start
        # e.g. "Renovations Renovations Replus Bureau..." → "Replus Bureau..."
        # Find where the real title starts and keep content after it
        desc_text = all_text
        if title in desc_text:
            idx = desc_text.find(title)
            desc_text = desc_text[idx:].strip()

        # Remove the title from the start of description to avoid repetition
        if desc_text.startswith(title):
            desc_text = desc_text[len(title):].strip()

        description = desc_text[:280] + "..." if len(desc_text) > 280 else desc_text

        # Extract date from URL if possible (dezeen URLs have /YYYY/MM/DD/)
        date_match = re.search(r"/(\d{4}/\d{2}/\d{2})/", href)
        date_str = date_match.group(1).replace("/", "-") if date_match else "Recent"

        news.append({
            "title": title,
            "link": href,
            "date": date_str,
            "description": description,
            "type": "news",
        })

    print(f"  >> Found {len(news)} news articles from dezeen.com")
    return news


def parse_bustler_competitions(html):
    """Parse bustler.net/competitions — reliable source with clear dates."""
    print("Parsing bustler.net competitions...")
    competitions = []
    if not html:
        return competitions
    
    soup = BeautifulSoup(html, "html.parser")
    seen_links = set()
    
    # 1. Featured competitions
    featured = soup.find_all("div", class_="featured-listing")
    for item in featured:
        link_el = item.find("a", class_="item")
        if not link_el: continue
        href = link_el.get("href", "")
        if not href.startswith("http"):
            href = "https://bustler.net" + href
            
        title_el = item.find("p", class_="listing-title")
        if not title_el: continue
        title = title_el.get_text(strip=True)
        
        dates = item.find_all("p", class_="listing-dates")
        deadline = "Unknown"
        deadline_iso = None
        for d in dates:
            text = d.get_text(strip=True)
            if "Submit:" in text or "Register:" in text:
                date_str = text.split(":", 1)[1].strip()
                deadline = date_str
                try:
                    parsed_date = date_parser.parse(date_str, fuzzy=True)
                    deadline_iso = parsed_date.isoformat()
                    if "Submit:" in text:
                        break
                except Exception:
                    pass
        
        if deadline_iso and href not in seen_links:
            seen_links.add(href)
            competitions.append({
                "title": title,
                "link": href,
                "deadline": deadline,
                "deadline_iso": deadline_iso,
                "description": "Promoted on Bustler",
                "type": "competition"
            })
            
    # 2. Main list competitions
    list_entries = soup.find_all("a", class_="landing-page-list-entry")
    for link_el in list_entries:
        href = link_el.get("href", "")
        if not href.startswith("http"):
            href = "https://bustler.net" + href
            
        if "/news/" in href or href in seen_links:
            continue
            
        title_el = link_el.find("h3", class_="title")
        if not title_el: continue
        title = title_el.get_text(strip=True)
        
        dates_el = link_el.find("p", class_="event-dates")
        deadline = "Unknown"
        deadline_iso = None
        if dates_el:
            text = dates_el.get_text(strip=True)
            parts = text.split("|")
            date_str = parts[-1].strip() if parts else text
            deadline = date_str
            try:
                parsed_date = date_parser.parse(date_str, fuzzy=True)
                deadline_iso = parsed_date.isoformat()
            except Exception:
                pass
                
        if deadline_iso:
            seen_links.add(href)
            competitions.append({
                "title": title,
                "link": href,
                "deadline": deadline,
                "deadline_iso": deadline_iso,
                "description": "Listed on Bustler",
                "type": "competition"
            })
            
    print(f"  >> Found {len(competitions)} competitions from bustler.net")
    return competitions


def save_json(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"  [SAVED] {len(data)} items -> {filepath}")


def run_scraper():
    print("\n" + "=" * 60)
    print("  ArchiHub Scraper — Starting")
    print("=" * 60 + "\n")

    # ── 1. Competitions ──────────────────────────────────────────
    print("[ COMPETITIONS ]")
    comps1 = parse_competitions_archi(fetch_html("https://competitions.archi/"))
    comps2 = parse_architecturecompetitions_com(
        fetch_html("https://architecturecompetitions.com/", use_requests=True)
    )
    comps3 = parse_bustler_competitions(
        fetch_html("https://bustler.net/competitions", use_requests=True)
    )

    # Deduplicate by link — keep competitions.archi entries first (they have better data)
    comps_map = {}
    for c in comps1 + comps2 + comps3:
        if c["link"] not in comps_map:
            comps_map[c["link"]] = c

    all_comps = list(comps_map.values())

    # Final quality filter: remove any remaining junk
    all_comps = [
        c for c in all_comps
        if not _is_junk_competition_title(c["title"])
        and len(c["title"]) >= 8
    ]

    save_json(all_comps, COMPETITIONS_FILE)
    print(f"  Total unique competitions: {len(all_comps)}")
    print()

    # ── 2. Jobs ─────────────────────────────────────────────────
    print("[ JOBS ]")
    jobs_html = fetch_html(
        "https://jobs.architecture.com/",
        wait_selector="a[href*='/job/']"
    )
    jobs = parse_riba_jobs(jobs_html)

    if len(jobs) < 3:
        # Fallback: try with requests (sometimes static HTML has listings)
        print("  [WARN] Few jobs found, retrying with requests...")
        jobs_html2 = fetch_html("https://jobs.architecture.com/", use_requests=True)
        jobs2 = parse_riba_jobs(jobs_html2)
        if len(jobs2) > len(jobs):
            jobs = jobs2

    save_json(jobs, JOBS_FILE)
    print(f"  Total jobs: {len(jobs)}")
    print()

    # ── 3. News ──────────────────────────────────────────────────
    print("[ NEWS ]")
    news = parse_dezeen_news(fetch_html("https://www.dezeen.com/architecture/"))
    save_json(news, NEWS_FILE)
    print(f"  Total news articles: {len(news)}")
    print()

    print("=" * 60)
    print("  Scraping complete!")
    print("="* 60)


if __name__ == "__main__":
    run_scraper()

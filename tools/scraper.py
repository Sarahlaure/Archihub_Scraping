import sys
import io
# Force UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import os
import re
import unicodedata
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
    r'^(Guest jury|Book store|Explore Buildner|Join next competition)',
    r'winners announced',
    r'results announced',
    r'prize awarded',
    r'winners in',
    r'select winners',
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


def _normalize_title(title: str) -> str:
    """Normalize a title for deduplication: lowercase, remove accents, special chars, extra spaces."""
    # Lowercase
    t = title.lower().strip()
    # Remove \r\n and extra whitespace
    t = re.sub(r'[\r\n]+', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    # Remove unicode accents
    t = unicodedata.normalize('NFD', t)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    # Remove common noise words and punctuation
    t = re.sub(r'[^a-z0-9 ]', '', t)
    # Remove common prefixes/suffixes that differ between sources
    t = re.sub(r'\baia invites\b', '', t)
    t = re.sub(r'\bopen to all\b', '', t)
    t = re.sub(r'\bedition\b', '', t)
    t = re.sub(r'\bnew\b', '', t)
    t = re.sub(r'\bchallange\b', 'challenge', t)  # Fix common typo
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def _deduplicate_competitions(competitions: list) -> list:
    """Deduplicate competitions by normalized title similarity.
    Prefers entries with valid deadline_iso over those without."""
    seen = {}  # normalized_title -> competition entry
    result = []

    for comp in competitions:
        norm = _normalize_title(comp['title'])
        # Skip very short normalized titles (likely junk)
        if len(norm) < 5:
            continue

        if norm in seen:
            # If existing has no deadline but new one does, replace
            existing = seen[norm]
            if not existing.get('deadline_iso') and comp.get('deadline_iso'):
                seen[norm] = comp
                # Replace in result list
                for i, r in enumerate(result):
                    if _normalize_title(r['title']) == norm:
                        result[i] = comp
                        break
            # Otherwise keep the existing one (first wins = competitions.archi)
        else:
            seen[norm] = comp
            result.append(comp)

    return result


# ── Job title translations (EN -> FR) ──
JOB_TITLE_TRANSLATIONS = {
    'architect': 'Architecte',
    'senior architect': 'Architecte Senior',
    'junior architect': 'Architecte Junior',
    'project architect': 'Architecte de Projet',
    'architectural technologist': 'Technologue en Architecture',
    'architectural assistant': 'Assistant Architecte',
    'architectural designer': 'Concepteur Architectural',
    'project manager': 'Chef de Projet',
    'project runner': 'Responsable de Projet',
    'interior designer': 'Designer d\'Intérieur',
    'urban designer': 'Urbaniste',
    'urban planner': 'Urbaniste',
    'landscape architect': 'Architecte Paysagiste',
    'design manager': 'Responsable Design',
    'bim manager': 'Responsable BIM',
    'bim coordinator': 'Coordinateur BIM',
    'associate': 'Associé',
    'director': 'Directeur',
    'associate director': 'Directeur Associé',
    'principal': 'Directeur Principal',
    'part i': 'Partie I',
    'part ii': 'Partie II',
    'part iii': 'Partie III',
    'part 1': 'Partie 1',
    'part 2': 'Partie 2',
    'part 3': 'Partie 3',
    'consultant': 'Consultant',
    'brpd consultant': 'Consultant BRPD',
    'sustainability consultant': 'Consultant en Développement Durable',
    'planner': 'Planificateur',
    'town planner': 'Urbaniste',
    'heritage consultant': 'Consultant en Patrimoine',
    'technician': 'Technicien',
    'cad technician': 'Technicien CAO',
    'revit technician': 'Technicien Revit',
    'graduate architect': 'Architecte Diplômé',
    'intern architect': 'Architecte Stagiaire',
    'site architect': 'Architecte de Chantier',
    'design architect': 'Architecte Concepteur',
    'lead architect': 'Architecte Principal',
}

def _translate_job_title(title: str) -> str:
    """Translate an English job title to French.
    Tries exact match first, then partial matches, then word-by-word."""
    title_clean = title.strip()
    lower = title_clean.lower()

    # Exact match
    if lower in JOB_TITLE_TRANSLATIONS:
        return JOB_TITLE_TRANSLATIONS[lower]

    # Try matching with " / " separator (e.g. "Architect / Architectural Technologist")
    if ' / ' in title_clean:
        parts = [p.strip() for p in title_clean.split(' / ')]
        translated_parts = []
        for part in parts:
            part_lower = part.lower()
            if part_lower in JOB_TITLE_TRANSLATIONS:
                translated_parts.append(JOB_TITLE_TRANSLATIONS[part_lower])
            else:
                translated_parts.append(part)
        return ' / '.join(translated_parts)

    # Try longest match first
    for en, fr in sorted(JOB_TITLE_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True):
        if en in lower:
            title_clean = re.sub(re.escape(en), fr, lower, count=1, flags=re.IGNORECASE)
            # Capitalize first letter
            return title_clean[0].upper() + title_clean[1:] if title_clean else title_clean

    return title_clean


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


def _fetch_rss(url):
    """Fetch and parse an RSS feed. Returns a list of (title, link, description, date_str) tuples."""
    import xml.etree.ElementTree as ET

    print(f"  Fetching RSS: {url}")
    items = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=25)
        if r.status_code != 200:
            print(f"  [FAIL] RSS returned status {r.status_code}")
            return items

        root = ET.fromstring(r.text)
        for item in root.findall(".//item"):
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pub_el = item.find("pubDate")

            title = title_el.text.strip() if title_el is not None and title_el.text else None
            link = link_el.text.strip() if link_el is not None and link_el.text else None

            if not title or not link or len(title) < 10:
                continue

            # Clean description (remove HTML tags from RSS content)
            desc_raw = desc_el.text if desc_el is not None and desc_el.text else ""
            desc_clean = re.sub(r"<[^>]+>", "", desc_raw).strip()
            desc_clean = re.sub(r"\s+", " ", desc_clean)
            description = desc_clean[:280] + "..." if len(desc_clean) > 280 else desc_clean

            # Parse date
            date_str = "Récent"
            if pub_el is not None and pub_el.text:
                try:
                    parsed = date_parser.parse(pub_el.text)
                    date_str = parsed.strftime("%d %b %Y")
                except Exception:
                    # Try extracting from URL
                    date_match = re.search(r"/(\d{4}/\d{2}/\d{2})/", link)
                    if date_match:
                        date_str = date_match.group(1).replace("/", "-")

            items.append((title, link, description, date_str))

        print(f"  [OK] {len(items)} articles from RSS")
    except Exception as e:
        print(f"  [FAIL] RSS error: {e}")

    return items


def parse_dezeen_rss():
    """Fetch architecture news from Dezeen RSS feed (reliable, no 403 blocks)."""
    print("Parsing Dezeen RSS (architecture)...")
    news = []
    items = _fetch_rss("https://www.dezeen.com/architecture/feed/")

    for title, link, description, date_str in items:
        news.append({
            "title": title,
            "link": link,
            "date": date_str,
            "description": description,
            "type": "news",
        })

    print(f"  >> Found {len(news)} news from Dezeen RSS")
    return news


def parse_archdaily_rss():
    """Fetch architecture news from ArchDaily RSS feed."""
    print("Parsing ArchDaily RSS...")
    news = []
    items = _fetch_rss("https://www.archdaily.com/feed")

    for title, link, description, date_str in items:
        # Clean ArchDaily titles (they sometimes have extra whitespace)
        title = re.sub(r"\s+", " ", title).strip()

        news.append({
            "title": title,
            "link": link,
            "date": date_str,
            "description": description,
            "type": "news",
        })

    print(f"  >> Found {len(news)} news from ArchDaily RSS")
    return news


def fetch_all_news():
    """Fetch and merge news from multiple RSS sources, deduplicated by title."""
    print("Fetching news from multiple sources...")
    dezeen_news = parse_dezeen_rss()
    archdaily_news = parse_archdaily_rss()

    # Merge all news, Dezeen first (generally more architecture-focused)
    all_news = dezeen_news + archdaily_news

    # Deduplicate by normalized title
    seen = {}
    deduped = []
    for item in all_news:
        norm = _normalize_title(item["title"])
        if len(norm) < 8:
            continue
        if norm not in seen:
            seen[norm] = True
            deduped.append(item)

    # Sort by date (most recent first) — try parsing dates
    def sort_key(item):
        try:
            return date_parser.parse(item["date"], fuzzy=True)
        except Exception:
            return datetime.datetime.min

    deduped.sort(key=sort_key, reverse=True)

    # Limit to 40 most recent articles to keep the feed manageable
    deduped = deduped[:40]

    print(f"  >> Total unique news after merge: {len(deduped)}")
    return deduped


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

    # Step 1: Deduplicate by link — keep competitions.archi entries first (better data)
    comps_map = {}
    for c in comps1 + comps2 + comps3:
        if c["link"] not in comps_map:
            comps_map[c["link"]] = c

    all_comps = list(comps_map.values())

    # Step 2: Quality filter — remove junk titles
    all_comps = [
        c for c in all_comps
        if not _is_junk_competition_title(c["title"])
        and len(c["title"]) >= 8
    ]

    # Step 3: Cross-source deduplication by normalized title
    # Prioritizes entries with known deadlines (from competitions.archi or bustler)
    before_dedup = len(all_comps)
    all_comps = _deduplicate_competitions(all_comps)
    print(f"  Dedup: {before_dedup} -> {len(all_comps)} (removed {before_dedup - len(all_comps)} duplicates)")

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

    # Translate job titles to French
    for job in jobs:
        job['title'] = _translate_job_title(job['title'])

    save_json(jobs, JOBS_FILE)
    print(f"  Total jobs: {len(jobs)}")
    print()

    # ── 3. News ──────────────────────────────────────────────────
    print("[ NEWS ]")
    news = fetch_all_news()
    save_json(news, NEWS_FILE)
    print(f"  Total news articles: {len(news)}")
    print()

    print("=" * 60)
    print("  Scraping complete!")
    print("="* 60)


if __name__ == "__main__":
    run_scraper()

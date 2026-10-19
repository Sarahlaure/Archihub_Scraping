# 🏛️ Archi.Comp — Architecture Opportunities Platform

[![Daily Data Sync](https://github.com/Sarahlaure/Archihub_Scraping/actions/workflows/daily_sync.yml/badge.svg)](https://github.com/Sarahlaure/Archihub_Scraping/actions/workflows/daily_sync.yml)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![Playwright](https://img.shields.io/badge/Scraping-Playwright-2EAD33?logo=playwright)](https://playwright.dev/python/)
[![Vercel](https://img.shields.io/badge/Deployed-Vercel-000?logo=vercel)](https://vercel.com)

A modern, automated web platform that aggregates **international architecture competitions**, **job listings**, and **industry news** — updated daily via GitHub Actions.

---

## ✨ Features

- **Live Competition Feed** — Only shows competitions with verified, upcoming deadlines
- **Sticky Navigation** — Switch between Competitions, Jobs & News tabs at any scroll depth
- **Auto-Generated Summaries** — Fallback descriptions for entries with missing or short excerpts
- **Daily Automation** — GitHub Actions runs the scraper at 06:00 UTC every day
- **Source Attribution** — Every entry links directly to the original organizer or recruiter

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, Tailwind CSS v4, Framer Motion |
| Scraping | Python 3.11, Playwright (Chromium Headless), BeautifulSoup4 |
| Auth | Supabase (Google OAuth, RLS) |
| CI/CD | GitHub Actions |
| Hosting | Vercel |

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ & npm
- Python 3.11+ & pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Sarahlaure/Archihub_Scraping.git
cd Archihub_Scraping

# Install frontend dependencies
npm install

# Install scraping dependencies
pip install -r requirements.txt
playwright install chromium
```

### Run Locally

```bash
# Generate data (scrape sources)
python tools/scraper.py

# Start the dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

---

## 📁 Project Structure

```
├── .github/workflows/    # GitHub Actions (daily scraper)
├── public/               # Static assets + scraped JSON data
├── src/
│   ├── app/              # Next.js App Router pages
│   ├── components/       # React components (UI, theme)
│   └── lib/              # Utilities (Supabase client, helpers)
├── tools/
│   └── scraper.py        # Python scraping engine
├── package.json          # Node.js dependencies
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🌐 Deployment

1. Connect this repository to [Vercel](https://vercel.com)
2. Vercel auto-detects Next.js and deploys instantly
3. Every commit pushed by GitHub Actions triggers automatic redeployment

---

## 📝 License

Developed as an architecture opportunities aggregator. All displayed data belongs to their respective organizers and publishers.

# Project Constitution: AI/ML Innovation Pilot

## 1. Project Purpose

Build a deterministic, self-healing scraper and a premium dashboard to aggregate high-value news for AI/ML Engineers.

## 2. Data Schemas

### Article Payload (JSON)

```json
{
  "id": "string (hash of URL)",
  "title": "string",
  "summary": "string (brief summary/excerpt)",
  "link": "string (url)",
  "source": "string (Ben's Bytes, AI Rundown, Reddit, etc.)",
  "published_at": "ISO8601 string",
  "relevance_score": "float (0.0 - 1.0)",
  "tags": ["career", "innovation", "business", "technical"],
  "scraped_at": "ISO8601 string"
}
```

### Saved Article (Supabase `saved_articles` table)

```sql
id          UUID PRIMARY KEY DEFAULT gen_random_uuid()
user_id     UUID REFERENCES auth.users(id)
article_id  TEXT NOT NULL
title       TEXT
link        TEXT
source      TEXT
summary     TEXT
published_at TEXT
created_at  TIMESTAMPTZ DEFAULT now()
UNIQUE(user_id, article_id)
```

## 3. Behavioral Rules

- **Data First:** No scraping without schema validation.
- **24h Cycle:** Scrape latest 24h of data. If no new data, fallback to most recent.
- **Filtering:** Focus on "How AI/ML engineers can stand out" and "Business problem solving".
- **Reliability:** Use Layer 3 tools for scraping with heavy error handling.
- **Deduplication:** `articles.json` may contain duplicates (same ID, different title variant). Client must dedupe before rendering.

## 4. Architectural Invariants

- Frontend: Premium Next.js dashboard deployed on Vercel.
- Auth: Supabase Auth with Google OAuth. Middleware refreshes tokens on every request.
- Database: Supabase PostgreSQL with RLS policies (SELECT/INSERT/DELETE restricted to `auth.uid() = user_id`).
- Storage: `.tmp/` for raw scraped data, `public/articles.json` for the feed.

## 5. Maintenance Log

- 2026-02-13: Initial Schema defined.
- 2026-02-18: Supabase Auth + saved_articles integration.
- 2026-02-25: Fixed duplicate save bug, empty saved tab bug, tab UI/UX issues, `&apos;` rendering.

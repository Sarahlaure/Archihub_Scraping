# Findings & Research

## Discoveries

- **Ben's Bytes Archive:** `https://bensbites.substack.com/archive` (Substack based).
- **The AI Rundown Archive:** `https://www.therundown.ai/archive` (Custom site, Beehiiv based).
- **Reddit Subreddits:** `r/MachineLearning`, `r/ArtificialIntelligence`, `r/learnmachinelearning`, `r/LocalLLaMA`.

## Constraints

- Newsletter content is often behind a "Read more" or requires clicking into individual articles from the archive.
- Reddit requires either PRAW (API) or scraping (risk of blocks). PRAW is preferred for reliability.
- 24h update cycle requires timestamps from the source.

## Bug Analysis (2026-02-25)

### Bug 1: Double Article Save

- **Symptom:** Clicking bookmark on one article visually saved two articles at once.
- **Root Cause:** The scraper generates duplicate entries in `articles.json` — same `id` but different `title` variants (e.g., subtitle vs. main title from the same Substack post).
- **Fix:** Client-side deduplication using a `Map<id, Article>` that keeps only the first occurrence of each article ID.

### Bug 2: Saved Tab Shows Nothing

- **Symptom:** Clicking "Enregistrés" tab showed no articles, even after bookmarking several.
- **Root Cause:** The saved tab was filtering from `articles.json` (which changes daily) instead of loading from Supabase directly. If an article was saved yesterday but `articles.json` was refreshed today, the ID match would fail silently.
- **Fix:**
  1. Added metadata columns (`title`, `link`, `source`, `summary`, `published_at`) to Supabase `saved_articles` table.
  2. `toggleSave()` now upserts the full article payload.
  3. Saved tab now renders from `savedArticles` state (loaded from Supabase), not from `articles.json`.

### Bug 3: Tab Not Clickable / Confusing UI

- **Symptom:** "Enregistrés (2)" looked like a label, not a button.
- **Fix:** Redesigned tabs with clear active state (shadow, bg-background), separated counter into a styled badge, added cursor-pointer, dynamic page title.

### Bug 4: `&apos;` Showing Literally

- **Symptom:** Title "Flux d'actualités" rendered as `Flux d&apos;actualités`.
- **Root Cause:** Using `&apos;` inside a JSX expression `{}` renders it literally since it's treated as a string, not HTML.
- **Fix:** Replaced with Unicode curly apostrophe `\u2019`.

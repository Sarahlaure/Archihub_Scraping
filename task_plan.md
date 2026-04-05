# Task Plan: AI/ML Engineer News Scraper

## Phase 1: Blueprint

- [x] Discovery Questions Refined (User provided initial constraints)
- [x] Data Schema Defined in `gemini.md`
- [x] Research Archive URLs for Ben's Bytes & AI Rundown
- [x] Define Scraping Strategy in `architecture/scrapingSOP.md`

## Phase 2: Link

- [x] Test HTTP/Scraping connection to sources
- [x] Verify HTML selectors for each source

## Phase 3: Architect

- [x] Layer 1: SOP for scraping and data normalization
- [x] Layer 3: Python scraper tool (`tools/scraper.py`)
- [x] Layer 2: Scraper coordinator

## Phase 4: Stylize

- [x] Design Premium UI with Vanilla CSS (Glassmorphism, Dark Mode)
- [x] Implement "Save" functionality (LocalStorage initially)
- [x] Interactive filtering for innovation/career tags
- [x] Payload Refinement & Formatting

## Phase 5: Trigger

- [x] 24h Cron job setup (simulation script `run_sync.sh`)
- [x] Supabase integration (Auth + saved_articles table + RLS)

## Phase 6: Bug Fixes & Polish (2026-02-25)

- [x] Fix duplicate articles in feed (client-side dedup from `articles.json`)
- [x] Fix saved tab showing empty (load full articles from Supabase instead of filtering JSON)
- [x] Add metadata columns to `saved_articles` table (title, link, source, summary, published_at)
- [x] Redesign tab navigation (clearer active state, badge counter, cursor-pointer)
- [x] Fix `&apos;` literal rendering in dynamic title
- [x] Update all documentation files (progress.md, findings.md, gemini.md, task_plan.md, requirements.txt)

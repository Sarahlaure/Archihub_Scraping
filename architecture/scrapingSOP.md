# SOP: Multi-Source AI News Scraper

## Goal
Collect the latest (24h) news articles related to AI/ML innovation and career growth from specified sources.

## Sources
1. **Ben's Bytes (Substack)**
   - Link: `https://bensbites.substack.com/archive`
   - Method: Scrape archive for latest post link -> Scrape post content.
2. **The AI Rundown (Beehiiv)**
   - Link: `https://www.therundown.ai/archive`
   - Method: Scrape archive for latest post link -> Scrape post content.
3. **Reddit (API/Scraping)**
   - Subreddits: `r/MachineLearning`, `r/ArtificialIntelligence`
   - Filter: Top posts in last 24h with specific keywords (innovation, career, business).

## Logic Flow
1. **Trigger:** Script executes (manually or via cron).
2. **Fetch:**
   - For each source, fetch the list of recent articles.
   - Filter by `published_at > (now - 24h)`.
   - If no news in 24h, take the single most recent entry.
3. **Normalize:**
   - Map raw data to the `Article Payload` schema in `gemini.md`.
   - Assign `relevance_score` based on keyword matching (innovation, engineer, market, problem).
4. **Save:**
   - Append normalized data to `.tmp/latest_articles.json`.
5. **Deduplication:**
   - Check against existing `id` (hash of URL) to avoid duplicates.

## Edge Cases & Error Handling
- **Source Down:** Log error to `progress.md` and continue to next source.
- **Selector Change:** If scraping fails, attempt fallback selectors or log for manual update.
- **Rate Limiting:** Implement random sleep between requests.

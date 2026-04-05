# SOP: Data Normalization

## Input
Raw HTML or JSON from scraping tools.

## Output
JSON object following the schema in `gemini.md`.

## Transformation Rules
1. **ID Generation:** `hashlib.md5(url.encode()).hexdigest()`
2. **Date Parsing:** 
   - Convert strings like "Yesterday" or "2 hours ago" to ISO8601.
   - Default to current UTC time if no date found.
3. **Summary Extraction:**
   - Take the first 2-3 sentences of the article content.
   - Strip HTML tags.
4. **Relevance Scoring:**
   - Boost score if title or summary contains: "innovation", "career", "engineer", "problem", "solve", "market", "hiring".
   - Base score: 0.5. Max score: 1.0.
5. **Deduplication:**
   - If `id` exists in `data.json`, update the record only if the new one has more content.

## Schema Validation
Each entry must contain:
- `id`: Non-empty string
- `title`: Non-empty string
- `link`: Valid URL
- `source`: Known source name
- `published_at`: Valid ISO8601 string

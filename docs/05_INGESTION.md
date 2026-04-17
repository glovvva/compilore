# 05 — INGESTION
## Compilore: Source Adapters, Methods, Status

**Last updated:** 2026-04-17

---

## Overview

The ingestion layer extracts clean text from any source and delivers it to the
Compile loop. The adapter pattern means: every source type = isolated module.
The core engine never knows what the source was. PII must be scrubbed in memory
before anything is persisted to Supabase.

**Phase 1 scope:** Text/Markdown documents only.
**Phase 2 scope:** PDFs, social media, audio, proprietary Polish legal documents.

---

## Source Map by User Profile

Different users of Compilore have different dominant source types. This matters
for prioritizing adapter development.

### Profile A — Tech Strategist (Bartek)
| Source | Method | Status |
|---|---|---|
| Articles (Substack, Mirror, Medium, blogs) | URL → trafilatura | ✅ live |
| Research PDFs | PyMuPDF | ✅ live |
| Markdown notes | markdown_adapter.py | ✅ live |
| Plain text | text_adapter.py | ✅ live |
| Pasted text/snippets | text_paste_adapter.py | ⚠️ MISSING — add Sprint 2 |
| YouTube long-form | youtube-transcript-api + yt-dlp fallback | 🔲 planned |
| Twitter/X threads | SociaVault API | 🔲 planned |
| GitHub READMEs | raw.githubusercontent.com + GitHub API | 🔲 planned |
| Hacker News threads | Algolia HN API | 🔲 planned |
| Substack (paywalled) | Cookie injection | 🔲 planned |

### Profile B — HR/Biohacking/Wellness (Żona)
| Source | Method | Status |
|---|---|---|
| Instagram Reels | SociaVault API → n8n | 🔲 planned |
| TikTok | SociaVault API or tiktools | 🔲 planned |
| Substack newsletters (free) | URL → trafilatura | ✅ live (same as articles) |
| Substack newsletters (paywalled) | Cookie injection | 🔲 planned |
| YouTube short-form | youtube-transcript-api | 🔲 planned |
| Wellness podcasts (non-Spotify) | RSS → Faster-Whisper | 🔲 planned |
| Spotify podcasts | RSS (non-exclusives) → Faster-Whisper | 🔲 planned (Spotify exclusives = impossible) |

### Profile C — Technical Advisor (Friend)
| Source | Method | Status |
|---|---|---|
| Technical blog posts / docs | URL → trafilatura (or Firecrawl Phase 2) | ✅ live |
| GitHub READMEs | raw.githubusercontent.com | 🔲 planned |
| Hacker News threads | Algolia HN API | 🔲 planned |
| Technical podcasts | RSS → Faster-Whisper | 🔲 planned |
| Twitter/X threads | SociaVault API | 🔲 planned |

### Profile D — Technical Advisor (Industrial Distribution)
| Source | Method | Status |
|---|---|---|
| Manufacturer catalogs (PDF, native-digital) | PyMuPDF (pdf_text_adapter.py) + compile_technical_catalog.md prompt | ✅ ready (Phase 1, table extraction limited) |
| Manufacturer catalogs (PDF, scanned) | Docling TableFormer ACCURATE | 🔲 Phase 2 |
| Internal price lists / offers | pdf_text_adapter.py | ✅ ready (RODO note: Hetzner EU only) |
| Word documents (.docx) | python-docx adapter | 🔲 planned |
| Multi-language catalogs (PL/DE/EN) | Language detection + parameter normalization | 🔲 Phase 2 |

**Note for pilot:** Before ingesting any internal pricing or client offers, confirm data residency with user (Hetzner EU). Public manufacturer catalogs have no restriction.

---

## Adapter Specifications

### ✅ URL Adapter (trafilatura)
**File:** `src/modules/ingest/url_adapter.py`
**Method:** trafilatura extracts main content from URL, strips navigation/ads
**Output quality:** Good for articles. Degrades on SPA-heavy sites. Upgrade to
  Firecrawl self-hosted at Phase 2 if quality issues arise.
**Cost:** $0
**Polish language:** Works, no special handling needed

### ✅ Markdown Adapter
**File:** `src/modules/ingest/markdown_adapter.py`
**Method:** Read .md file, extract YAML frontmatter + content body
**Output quality:** Perfect — already structured
**Cost:** $0

### ✅ PDF Adapter (PyMuPDF)
**File:** `src/modules/ingest/pdf_text_adapter.py`
**Scope:** Native-digital PDFs only (not scanned)
**Known limitation:** Synchronous — blocks FastAPI event loop on large PDFs.
  Replace with Kreuzberg (async) at Phase 2.
**Cost:** $0

### ⚠️ Text Paste Adapter — MISSING
**File:** `src/modules/ingest/text_paste_adapter.py`
**Method:** Direct POST to `/ingest/paste` with raw text body
**Why critical:** Simplest possible input. Snippets, meeting notes, emails, any
  text the user has open. ~20 lines of code.
**Cost to compile:** ~$0.03 for a 500-word snippet
**Add:** Sprint 2, first task

---

## Planned Adapter Specifications

### YouTube Adapter
**File:** `src/modules/ingest/youtube_adapter.py`
**Method:**
1. `youtube-transcript-api` — downloads auto-generated or manual captions directly
   by video ID (no browser, no download)
2. Fallback: `yt-dlp` downloads audio → Faster-Whisper transcription
**When fallback needed:** Video has no captions (live streams, unlisted, some shorts)
**Output:** Pure conversational text with timestamps
**Token estimate per hour:** ~15,000–25,000 tokens
**Compile cost per 1h video:** ~$0.15–$0.25
**n8n integration:** Pass YouTube URL → trigger ingest endpoint

### Instagram Reels Adapter
**File:** `src/modules/ingest/instagram_adapter.py`
**Method:** SociaVault API
**Endpoint:** `GET https://api.sociavault.com/v1/scrape/instagram/transcript?url={url}`
**Auth:** `x-api-key` header
**Output:** JSON with transcript text
**Cost:** 1 credit per transcript regardless of length
**Pricing:** Growth pack $79/20,000 credits = **$0.004/transcript**
**n8n integration:** Standard HTTP Request node, no native node needed
**Reliability advantage:** Dedicated maintained endpoint vs Apify headless actors
  that break when Meta updates DOM structure
**Note:** Does not require Instagram login or OAuth

### Twitter/X Thread Adapter
**File:** `src/modules/ingest/twitter_adapter.py`
**Method:** SociaVault API
**Endpoint:** `GET https://api.sociavault.com/v1/scrape/twitter/tweet?url={url}`
**Why not official API:** Official X Basic = $100/mo for 10,000 tweets. Enterprise = $5,000/mo.
**Why not Apify:** Headless browser can't capture virtualized DOM lists (>50 tweets
  are unloaded as user scrolls). Single static snapshot misses most of thread.
**Output:** Full nested thread as structured JSON
**Cost:** $29/6,000 credits
**Legal note:** Scraping publicly available data aligns with hiQ vs. LinkedIn precedent.
  Violates X ToS → use SociaVault to abstract IP risk from Hetzner server.

### GitHub Adapter
**File:** `src/modules/ingest/github_adapter.py`
**Method:**
1. Single README: `raw.githubusercontent.com/{owner}/{repo}/main/README.md` — pure Markdown, zero noise
2. Full repo docs: GitHub REST API to map tree → async download of all `.md` files
**Auth:** GitHub personal token (5,000 requests/hour authenticated)
**Cost:** $0
**Output quality:** Perfect — raw Markdown, no HTML wrapper

### Hacker News Adapter
**File:** `src/modules/ingest/hackernews_adapter.py`
**Method:** Algolia HN API (`hn.algolia.com/api`)
**Why Algolia, not Firebase:** Firebase API has N+1 problem.
  500-comment thread = 500 HTTP requests.
  Algolia: single GET, returns up to 1,000 items with nested hierarchy in one payload.
**Critical:** Preserve nested comment hierarchy in output (indentation + quote blocks).
  LLM needs to know which comment replies to which parent to understand debate context.
**Cost:** $0 (free API, no key required)

### Podcast/Audio Adapter
**File:** `src/modules/ingest/podcast_adapter.py`
**Method:**
1. Detect if podcast has RSS feed (most non-Spotify podcasts do)
2. Parse RSS → download MP3 to Hetzner
3. Route through Faster-Whisper Large-v3 (self-hosted)
**Spotify path:** Use `spotify-scraper` Python package to detect new episodes in
  target playlists → locate public RSS feed if exists → download MP3
**Spotify exclusives:** No path. Workaround: if podcast also on YouTube → use YouTube adapter.
**Why Faster-Whisper Large-v3:**
  - 4x faster than original Whisper
  - Handles Polish diacritics (ą, ę, ł, ń, ó, ś, ź, ż) accurately
  - Handles PL/EN code-switching (Polish conversation + English technical terms) without breaking
  - Runs self-hosted on Hetzner = GDPR compliant (audio never leaves EU)
  - $0 per minute (vs $0.0043/min Deepgram, $0.21/hr AssemblyAI)
**Post-processing:** Faster-Whisper generates VTT/SRT with timestamps. Run local LLM
  step via n8n to add paragraph breaks + speaker labels before storing.

### Substack Paywalled Adapter
**File:** `src/modules/ingest/substack_adapter.py`
**Method:**
1. `scrape-substack` library queries hidden JSON API to discover new posts
2. For paywalled posts: inject `substack.sid` + `substack.lli` session cookies from
   logged-in browser session into Python requests headers
**Cookies:** Export from browser → store in Hetzner `.env`. Rotate manually when session expires.
**Hard constraint:** ONLY for own paid subscriptions. Never for redistribution, republishing,
  or training. Private PKB use only. Violation = copyright infringement + Substack ban.
**Cost:** $0 (you already pay for the subscription)

### TikTok Adapter
**File:** `src/modules/ingest/tiktok_adapter.py`
**Method option 1:** JSON hydration — TikTok SPAs ship `<script id="__NEXT_DATA__">` with
  structured JSON in HTML. Parse HTML → extract JSON → no browser needed.
**Method option 2:** SociaVault API (unified approach with Instagram)
**Why not official API:** TikTok Research API restricted to academic institutions only.
  Commercial/private developer use explicitly forbidden.
**Cost:** SociaVault ~$0.004/video or $0 (JSON hydration)

---

## PII Scrubbing (Required Before Any Persistence)

Social media data inevitably contains PII: usernames, email addresses, location data,
phone numbers scraped from profiles and comments.

**Rule:** PII scrubbing runs in memory, BEFORE any data is written to Supabase.

**Implementation:** n8n Code node with regex + optional local LLM pass:
- Credit card numbers → masked
- Physical addresses → masked
- Email addresses not belonging to the content owner → masked
- Phone numbers → masked

**Why this matters for GDPR:** Storing unscrubbed social media data exposes the system
to GDPR data subject access requests and right-to-be-forgotten mandates. This is not
optional compliance — it is infrastructure requirement.

n8n execution logs: configure to discard successful execution logs or write only
sanitized payloads to isolated storage volume.

---

## Token Estimates by Source Type

| Source type | Approx tokens | Compile cost | Embed cost | Total |
|---|---|---|---|---|
| Short article (1,500 words) | ~4K in / ~2K out | ~$0.042 | ~$0.001 | **~$0.04** |
| Medium article (3,000 words) | ~6K in / ~3K out | ~$0.063 | ~$0.002 | **~$0.07** |
| YouTube transcript (30 min) | ~10K in / ~4K out | ~$0.09 | ~$0.003 | **~$0.09** |
| YouTube transcript (2 hours) | ~25K in / ~6K out | ~$0.165 | ~$0.008 | **~$0.17** |
| Research paper (10-20 pages) | ~15K in / ~5K out | ~$0.12 | ~$0.005 | **~$0.13** |
| Instagram Reel transcript | ~2K in / ~1.5K out | ~$0.028 | ~$0.001 | **~$0.03** |
| Pasted text snippet | ~2K in / ~1.5K out | ~$0.028 | ~$0.001 | **~$0.03** |
| Long report / MPZP (Phase 2) | ~50K in / ~15K out | ~$0.375 | ~$0.015 | **~$0.39** |

Note: Brief originally estimated $0.40/document — this was calibrated for MPZP-scale
documents. Personal use with articles/transcripts is $0.04–$0.17/document.

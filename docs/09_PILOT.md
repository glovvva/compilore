# 09 — PILOT USER FRAMEWORK
## Compilore: Wojtek / HermesTools Pilot Program

**Created:** 2026-04-17
**Last updated:** 2026-04-19
**Status:** Active — awaiting domain/SSL setup
**Pilot user:** Wojtek (Technical Advisor, HermesTools Sp. z o.o.)
**Company:** HermesTools Sp. z o.o., Bielsko-Biała — industrial assembly tools 
distribution (wkrętarki przetwornikowe, klucze dynamometryczne, narzędzia montażowe).
Operates across Poland + Czech Republic + Slovakia. Est. 1994.
**Pilot duration:** 8 weeks structured + open-ended continuation
**Goal:** Validate that Compilore solves the parametric catalog search problem for 
industrial tools distribution. If successful → proposal to HermesTools company account 
(Team tier) → replication to adjacent firms in same vertical.

---

## 1. WHY THIS PILOT MATTERS

Wojtek is not just a friendly test user. He is:
1. **Signal source:** His usage patterns tell us if the core loop works for B2B 
   technical distribution — the new beachhead market.
2. **Internal champion:** If the tool works, he is the person who walks into his 
   manager's office and says "we should buy this for the whole technical team."
3. **Onboarding blueprint:** Everything we learn from Wojtek's experience becomes 
   the onboarding template for every future B2B client.
4. **Conversion path:** Wojtek (free) → HermesTools company (Team tier, ~1,200–
   1,800 PLN/msc) → referral to similar firms in industrial tools distribution.

One failed experience = tool discarded permanently (confirmed by DR-1 shadow 
testing behavior). The pilot must be smooth, well-documented, and closely monitored.

---

## 2. PILOT STRUCTURE (8 WEEKS)

### Week 1–2: Foundation — "Does it ingest?"
**Goal:** System ingests Wojtek's real documents without errors. Wiki starts forming.

**Wojtek's task:**
- Upload 1 folder from one manufacturer (recommend: start with KOLVER or HAZET — 
  most frequently used, best structured PDFs)
- Include: product catalog, technical datasheet, calibration certificate template, 
  price list if available
- Ask 3 test questions he already knows the answers to (from memory/experience)

**We measure:**
- Ingest success rate (0 errors target)
- Wiki pages created: are they meaningful? Do concept pages make sense?
- Citation accuracy: does the answer point to the right page in the right document?
- Answer quality: would Wojtek send this answer to a client as-is? (Y/N)

**Success gate:** 3/3 test questions answered correctly with valid citations.
**Fail signal:** Any hallucinated specification (wrong torque value, wrong model number).

---

### Week 3–4: Expansion — "Does it scale?"
**Goal:** Multiple manufacturers in one Wiki. Cross-manufacturer queries work.

**Wojtek's task:**
- Upload 2–3 more manufacturer folders (e.g. APEX, CLECO, SCS)
- Ask 5 cross-manufacturer questions:
  - "Which wkrętarki przetwornikowe from our portfolio support Bluetooth data 
    archiving and have torque range 2–20 Nm?"
  - "Compare KOLVER and CLECO for ESD-safe assembly — what are the differences?"
  - "Which of our tools are certified to ISO 6789-2?"
  - [2 more from Wojtek's real daily queries]

**We measure:**
- Cross-document retrieval accuracy
- Does Wiki compound? (Are new concept pages created that link manufacturers?)
- Response time (target: under 10 seconds for query synthesis)
- Did Wojtek use an answer in a real client interaction? (key signal)

**Success gate:** 4/5 cross-manufacturer queries answered correctly.

---

### Week 5–6: Stress Test — "Does it handle the hard stuff?"
**Goal:** Test edge cases: raster tables, multilingual docs, calibration specs.

**Wojtek's task:**
- Upload the most complex document he has (a catalog with tables as images, 
  or a German-language manufacturer spec)
- Ask a question that requires reading a table (e.g. torque-angle curve lookup)
- Ask a question that requires combining info from 3+ documents

**We measure:**
- VLM fallback trigger rate (how often does Docling fail and VLM kicks in?)
- Table extraction accuracy
- Multi-document synthesis quality
- Language handling (PL/EN/DE mix in single query response)

**Success gate:** Table-based query answered correctly at least once.
**If fails:** Document as known limitation, not a blocker — note for Phase 2 VLM priority.

---

### Week 7–8: Real Usage — "Would you pay for this?"
**Goal:** Wojtek uses Compilore in real daily work, without structured prompts from us.

**Wojtek's task:**
- Use freely for 2 weeks
- No assigned questions — real client queries only
- Log: date, question type, answer quality (1–5), did he use it (Y/N)

**We measure:**
- Daily active usage (target: at least 3 days/week)
- Query volume vs. week 1 (should increase if value is real)
- Unprompted feedback (positive or negative)
- **The key question at end of week 8:** "Would you recommend this to your manager 
  as a tool for the whole technical team?" (Y/N + why)

**Success gate:** "Yes" on the recommendation question.

---

## 3. WOJTEK'S ONBOARDING INSTRUCTIONS
*(This section becomes the basis for all future client onboarding docs)*

### Before first login
**Prerequisites checklist (Bartek, before Wojtek's login):**
- [ ] Domain/SSL configured and working (blocked — separate issue)
- [x] Wojtek's Supabase Auth account created 
      (wojtek-igi@wp.pl, id: c79b66ea-b564-4332-8fa5-46693e2d675e)
- [ ] Wojtek's account added to hermes-pilot org_members 
      (pending domain/SSL confirmation)
- [x] Docling installed and validated on KOLVER catalog
- [x] organization_id isolation active — hermes-pilot org seeded
- [ ] Bartek password set via /admin/set-password
- [ ] Wojtek password set via /admin/set-password and 
      communicated securely
- [ ] Supabase Redirect URL updated to production domain 
      (currently set to 127.0.0.1:8001/auth/callback for local)

Bartek sends Wojtek:
1. Login link + credentials
2. This message (in Polish, see §6 below)
3. A 5-minute Loom walkthrough of the UI (record once, reuse forever)

### What to upload first
Do NOT upload everything at once. Start small, verify quality, then expand.

**Recommended upload order:**
1. **Session 1:** One manufacturer folder — the one Wojtek uses most. 
   Include catalog + datasheet only. No price lists yet.
2. **Session 2 (after confirming Session 1 works):** Second manufacturer folder.
3. **Session 3+:** Remaining folders, one at a time.

**Folder naming convention (important for Wiki quality):**

---

## 9. KNOWN TECHNICAL CONSTRAINTS

| Constraint | Impact | Status |
|---|---|---|
| Python 3.9 venv | All type hints must use Optional[X] not X\|None | Fixed in main.py + supabase.py. Watch for regressions. |
| Docling export_to_markdown deprecation | Warning noise in logs, no functional impact | Pending fix: pass doc argument |
| Magic link redirect | Requires correct Supabase Redirect URL per environment | Set to /auth/callback. Must update for each new domain. |
| ADMIN_TOKEN env var | POST /admin/set-password returns 404 if not set | Must be in .env before setting user passwords |
| Wojtek org_members row | Wojtek cannot log in until row added manually | Pending domain/SSL + user_id confirmation |

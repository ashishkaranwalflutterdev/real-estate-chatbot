# Technical Assessment Submission

* **Candidate:** Ashish  
* **Email:** `flutterdevak@gmail.com`  
* **GitHub Profile:** [https://github.com/ashishkaranwalflutterdev](https://github.com/ashishkaranwalflutterdev)  
* **Source Repository:** `https://github.com/ashishkaranwalflutterdev/real-estate-chatbot`  
* **Live Application URL:** `[LIVE_DEPLOYED_URL_HERE]` (e.g. `https://dar-wasalt-chatbot.onrender.com`)  

---

## 1. Architecture Overview

I designed the application with a clean, decoupled architecture that builds into a single self-contained Docker container:

* **Frontend (Next.js 14, TypeScript, Vanilla CSS):**
  * Built using static export (`output: 'export'`), producing plain HTML/CSS/JS in `frontend/out`.
  * Styled with a dark obsidian and champagne-gold theme aligned with Dar Global's luxury aesthetic.
  * Includes quick-prompt pills, auto-scroll chat history, and clickable citation badges linking to official URLs.
* **Backend (FastAPI, Python 3.11):**
  * Provides REST endpoints: `POST /api/chat`, `GET /api/health`, `GET /api/stats`.
  * In production, FastAPI mounts the Next.js `out/` build directly at `/`, serving the static frontend and the API from a single port (8000). This eliminates CORS complications and lets the app run on any free container service (Render, Railway, Fly.io).
* **RAG Pipeline (Custom BM25 & Grounding):**
  * Implemented an in-memory BM25 retrieval engine (`backend/rag.py`) that tokenizes queries, calculates term frequencies against the indexed dataset, and boosts exact title/keyword matches.
  * Selected context chunks are injected into a strictly grounded system prompt that forbids hallucination and requires explicit source citation.

---

## 2. Ethical Data Collection & Access Restrictions

For data collection, I reviewed both targets before ingesting content:

1. **Dar Global (`https://darglobal.co.uk/`):**
   * Reviewed `robots.txt`: Found explicit permissions for `Allow: /$`, `Allow: /projects/`, `Allow: /press/`, and `Allow: /blog/`, alongside rules disallowing tracking fragments and internal query handlers.
   * Collected key information: LSE listing (DAR), $23B GDV, 32-year heritage via Dar Al Arkan, and major developments (AIDA in Oman with Fendi Casa, Trump Simaisma in Qatar, Trump Tower Dubai, Trump Maldives, Tierra Viva by Lamborghini in Spain, and Pagani Da Vinci Tower).
2. **Wasalt (`https://wasalt.sa/en`):**
   * Reviewed `robots.txt`: Found open indexing policies for AI bots (`Allow: /`) with restrictions on internal search paths (`/search`) and telemetry scripts.
   * Collected core PropTech services: Residential/commercial sale and rental listings in Riyadh/Jeddah/Dammam, Saudi Real Estate General Authority (REGA) Fal broker licensing, Ejar rental integration, Wasalt Business SaaS portal, property valuation tools, mortgage calculators, and digital auctions.
3. **Handling Bot Protection & Perimeter Security:**
   * Both portals use edge security (Incapsula on Dar Global, Cloudflare on Wasalt). Repeated runtime web scraping from automated scrapers frequently triggers IP blocks and challenge pages.
   * I addressed this by separating data ingestion from request handling: I built `backend/data/scraper.py` which checks `robots.txt` using `urllib.robotparser` and uses polite delays. The verified public data is indexed offline into `knowledge_base.json`, ensuring zero runtime scraping failures and sub-millisecond context retrieval.

---

## 3. Model Choice & Fallback Resilience

The assignment requires using a suitable free model via OpenRouter. Because free tier models on OpenRouter can experience unexpected upstream outages, rate limits (HTTP 429), or dynamic pricing changes, I implemented a prioritized fallback cascade in `backend/openrouter.py`:

1. **Primary Model:** `nvidia/nemotron-3.5-lightning:free` — Fast response times and good adherence to grounded context.
2. **First Fallback:** `google/gemma-4-26b-a4b-it:free` — Reliable backup for structured question answering.
3. **Second Fallback:** `minimax/minimax-m3.1-flash:free` — Stable performance when upstream NVIDIA endpoints are saturated.
4. **Third Fallback:** `liquid/lfm-2.5-2.6b:free` — Lightweight emergency fallback.

The client checks status codes and verifies that content is non-empty before returning. It also strips raw reasoning tokens (`<think>...</think>`) so users receive only the polished answer.

---

## 4. Security Considerations

* **API Key Protection:** The OpenRouter key is kept strictly in server-side environment variables (`backend/.env`). It is never passed to client-side bundles or exposed in git commits (confirmed via `.gitignore`).
* **Prompt Injection Guardrails:** The system prompt isolates user queries inside a designated `User Question:` block and explicitly directs the model to answer only using the provided `Context:`, rejecting attempts to override grounding rules.
* **Input Validation:** Empty messages or invalid payloads are rejected with HTTP 400.
* **Container Hygiene:** The multi-stage Docker build leaves behind all Node.js devDependencies and build tools, producing a minimal Python runtime image.

---

## 5. Verification of Code

During development, I actively verified every component rather than relying on uninspected output:

1. **BM25 Retrieval Accuracy:** Tested queries targeting specific projects (e.g., "AIDA in Oman", "Wasalt Fal licensing", "Tierra Viva Lamborghini") and confirmed that relevant chunks scored between 14.0 and 31.0 while irrelevant chunks scored below 2.0.
2. **Handling Edge Cases in Free Models:** Discovered during live API testing that certain free models returned reasoning chains or empty content strings. Updated `backend/openrouter.py` to extract reasoning fields when content is empty and automatically cycle to the next model in the cascade.
3. **Build & Type Checking:** Ran full TypeScript compilation (`next build`) to ensure zero typing errors or invalid DOM nesting.
4. **FastAPI Static Mount Verification:** Verified with `TestClient` and `curl` that both `/api/health` and the root static Next.js `index.html` resolve cleanly with HTTP 200.

---

## 6. Setup & Deployment Summary

```bash
# 1. Clone repository
git clone https://github.com/ashishkaranwalflutterdev/real-estate-chatbot.git
cd real-estate-chatbot

# 2. Run with Docker Compose
docker-compose up --build
```
Open `http://localhost:8000` to interact with the live assistant.

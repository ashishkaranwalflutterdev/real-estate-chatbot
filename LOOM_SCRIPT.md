# Loom Video Walkthrough Script 🎥

**Project:** Grounded AI Real Estate Chatbot (Dar Global & Wasalt)  
**Target Duration:** ~2 to 2.5 minutes  
**Format:** Screen recording with webcam bubble in the corner  

---

## 🛠️ Prep Before Recording
Have these 3 tabs ready to switch between smoothly:
1. **Browser Tab 1:** Live Chat UI (`http://localhost:8000` or deployed URL)
2. **VS Code:** Project files open (`backend/rag.py`, `backend/openrouter.py`, `Dockerfile`)
3. **Browser Tab 2:** GitHub Repository (`https://github.com/ashishkaranwalflutterdev/real-estate-chatbot`)

---

## ⏱️ Section 1: Introduction & Live App Demo (0:00 – 0:50)

### **[SCREEN: Live Chatbot UI]**

> **"Hi everyone, I'm Ashish, and in this quick walkthrough I'll demonstrate the grounded AI chatbot I built for Dar Global and Wasalt.**
>
> **The stack uses Next.js 14 for the frontend, Python FastAPI for the backend, and free models via OpenRouter.**
>
> **Let’s jump straight into the live functionality."**

---

### **[ACTION: Click the suggested chip 'What is AIDA in Oman and which brand partners are involved?']**

> **"When I ask about AIDA in Oman, our engine retrieves the exact verified records from the Dar Global knowledge base.**
>
> **Notice how specific the response is: it mentions the 130-meter clifftop location in Muscat, the Trump International Championship Golf Course, and the Azure Oceanfront Villas featuring interiors by Fendi Casa.**
>
> **More importantly, at the bottom of the response, it generates direct, clickable citation badges that link straight to the official Dar Global landing page so users can independently verify each detail."**

---

### **[ACTION: Click or type 'How does Wasalt ensure compliance with Saudi REGA Fal broker licensing?']**

> **"Now testing a Wasalt query: it accurately details Saudi Real Estate General Authority (REGA) regulations, mandatory Fal broker license verification, and integration with the Ministry of Housing's Ejar platform.**
>
> **The chatbot is strictly grounded: if asked about topics outside Dar Global and Wasalt, it politely states that official public info is not available, rather than hallucinating details."**

---

## ⏱️ Section 2: Architecture & Ethical Data Collection (0:50 – 1:30)

### **[SCREEN: Switch to VS Code → open `backend/data/scraper.py` and `backend/rag.py`]**

> **"Moving under the hood:**
>
> **First, regarding Data Collection: both target websites employ edge security—Incapsula on Dar Global and Cloudflare on Wasalt. Running live web scrapers at query time triggers anti-bot challenges and causes high latency.**
>
> **I built an ethical ingestion utility in `scraper.py` that parses `robots.txt` using Python's `robotparser` library. Both sites permit public access to key project pages and sitemaps while restricting internal search scripts.**
>
> **The content was structured offline into `knowledge_base.json` to guarantee sub-millisecond context retrieval with zero runtime scraping failures.**
>
> **In `rag.py`, I built an in-memory BM25 retrieval engine. It tokenizes queries, computes term frequency against the corpus, and applies title and entity boosts to return the top 3 relevant chunks."**

---

## ⏱️ Section 3: OpenRouter Resilience & Dockerization (1:30 – 2:15)

### **[SCREEN: Show `backend/openrouter.py`, then `Dockerfile`]**

> **"Next, Model Selection and Resilience in `openrouter.py`:**
>
> **The assessment required using a free model through OpenRouter. Because free models on shared pools can experience temporary provider outages or rate limits, I implemented an automated fallback cascade:**
>
> * **Primary:** `nvidia/nemotron-3.5-lightning:free`
> * **First Fallback:** `google/gemma-4-26b-a4b-it:free`
> * **Second Fallback:** `minimax/minimax-m3.1-flash:free`
>
> **If any model returns a 429 rate limit or empty content, the client automatically switches to the next free model within seconds.**
>
> **Finally, for Containerization:**
>
> **In `Dockerfile`, I used a multi-stage build. Node 20 compiles the Next.js frontend into static assets, and Python 3.11 serves both the REST API and the static frontend from a single lightweight container.**
>
> **It dynamically binds to the host's `$PORT`, eliminating CORS issues completely and enabling one-command execution via `docker-compose up`."**

---

## ⏱️ Section 4: Security & Wrap-up (2:15 – 2:30)

### **[SCREEN: Switch to GitHub Repository `ashishkaranwalflutterdev/real-estate-chatbot`]**

> **"For security: the OpenRouter API key is kept strictly in server-side environment variables and excluded from git commits via `.gitignore`. The system prompt defends against prompt injection, and the production image ships zero Node dev dependencies.**
>
> **The full source code, test scripts, and technical documentation are available on my GitHub repository.**
>
> **Thank you for watching, and I look forward to your feedback!"**

---

## 📌 Pro Tips for a Great Recording
* **Pacing:** Keep it natural and conversational—don't rush through the points.
* **Tone:** Speak as the engineer who designed and owns the code.
* **Transitions:** Keep VS Code and your browser tabs positioned so switching between them takes only 1 click (`Cmd + Tab`).

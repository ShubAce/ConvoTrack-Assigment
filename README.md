# ConvoTrack – Multi‑Agent Business Intelligence QA System

Autonomous multi‑agent RAG (Retrieval Augmented Generation) system that ingests ConvoTrack case study pages, builds a Pinecone vector knowledge base, and serves a FastAPI backend powering a modern React (Vite) chat UI. Users ask open‑ended business / market / strategy questions; the system classifies intent, retrieves evidence, performs structured reasoning with Groq Llama3 70B, and returns a richly formatted, source‑grounded answer plus citations.

## Contents

1. Features
2. Architecture & Data Flow
3. Repository Structure
4. Technology Stack
5. Environment Variables (.env template)
6. Setup & Run (Backend + Frontend)
7. Knowledge Base Build Workflow
8. API Reference
9. Frontend UX Highlights
10. Multi‑Agent Design (Roles & Responsibilities)
11. Customization Tips
12. Troubleshooting & Diagnostics
13. Roadmap / Next Ideas
14. License

15. Features

---

-   End‑to‑end autonomous question answering over scraped case study corpus.
-   Multi‑agent orchestration (Manager + Research + Analysis + Synthesizer agents).
-   Automatic question intent routing into analysis modes: strategic, trends, comparative, executive, default.
-   Retrieval via Pinecone (semantic vector search) with HuggingFace MiniLM embeddings.
-   Structured, deeply reasoned analytical output with evidence synthesis & recommendations.
-   Source citation panel with expandable raw text snippets (React sidebar / mobile overlay).
-   FastAPI backend with clean JSON schema and CORS config for local dev ports (3000 / 5173).
-   Selenium scraping script to refresh corpus from live case study URLs.
-   Automatic knowledge base initialization on server startup (rebuild if index empty).

2. Architecture & Data Flow

---

High‑level pipeline:

```
         (1) Selenium Scraper
                │
                ▼
          Raw Case Study .txt files
                │
        DocumentLoader + Splitter
                │ (chunks)
                ▼
   HuggingFace Endpoint Embeddings
                │ (vectors)
                ▼
           Pinecone Index
                │ (top-k relevant docs)
                ▼
           ResearchAgent
                │ context docs
                ▼
           AnalysisAgent (LLM: Groq Llama3 70B)
                │ raw structured analysis
                ▼
          SynthesizerAgent (formatting)
                │ answer + metadata
                ▼
        FastAPI /ask endpoint (JSON)
                │
                ▼
           React Frontend (chat + citations)
```

3. Repository Structure

---

```
extractContent/
  selenium_scraper.py            # Scrape case study pages into article_*.txt
  scraped_articles_selenium/     # Persisted text corpus (inputs to RAG)
qa_agent/
  fastapi_server.py              # FastAPI app (startup loads agent)
  qa_agent_ai.py                 # Multi‑agent system (manager + workers)
  document_loader.py             # Corpus loading, splitting, Pinecone index mgmt
frontend/                        # React + Vite chat UI (source citations panel)
requirements.txt                 # Python backend dependencies
```

4. Technology Stack

---

Backend:

-   Python 3.12+
-   FastAPI + Uvicorn
-   LangChain (orchestration, chains, prompts)
-   Groq Llama3‑70B (ChatGroq) – reasoning & routing
-   Pinecone (vector DB) – semantic retrieval
-   HuggingFace Endpoint Embeddings (MiniLM-L6-v2, 384-dim)
-   Selenium (Chrome) – initial corpus acquisition

Frontend:

-   React 19 + Vite
-   Tailwind CSS 4 (via @tailwindcss/vite)
-   Framer Motion (animations)
-   react-markdown (LLM answer rendering)
-   lucide-react (icons)
-   Axios (API calls)

5. Environment Variables (.env template)

---

Create `qa_agent/.env` (already loaded via `dotenv`):

```
GROQ_API_KEY=your_groq_key_here
PINECONE_API_KEY=your_pinecone_key_here
HUGGINGFACE_API_TOKEN=your_hf_token_here
```

Notes:

-   Pinecone index name defaults to `convotrack-casestudies` (see `VectorStoreManager`). Region/serverless spec is hard‑coded (AWS us-east-1).
-   HuggingFace token must permit inference for `sentence-transformers/all-MiniLM-L6-v2` via endpoint.
-   No OpenAI key needed (Groq is used).

6. Setup & Run

---

### 6.1 Backend (Windows CMD examples)

```
cd qa_agent
python -m venv .venv
.venv\Scripts\activate
pip install -r ..\requirements.txt
copy NUL .env  (then edit .env with keys)  # or create manually
python fastapi_server.py
```

Server starts at http://localhost:8000 with hot reload.

Health check: http://localhost:8000/health

### 6.2 Frontend

```
cd frontend
npm install
npm run dev
```

Open the printed local URL (default http://localhost:5173). The app auto‑checks backend health.

7. Knowledge Base Build Workflow

---

First server startup:

1. `fastapi_server` runs `AdvancedCaseStudyQAAgent` startup event.
2. `setup_knowledge_base()` (Pinecone) checks if the index has vectors.
3. If empty: loads `extractContent/scraped_articles_selenium/*.txt`, splits into 1000‑char chunks (200 overlap), embeds, and upserts into Pinecone.
4. Subsequent restarts reuse existing vectors (fast).

Force rebuild options:

-   Run `python qa_agent/document_loader.py` (its `__main__` uses `force_rebuild=True`).
-   Or modify the startup call to pass `force_rebuild=True` (manual code change).

Scraping new corpus:

```
cd extractContent
python selenium_scraper.py
```

Ensure Chrome + matching chromedriver are installed/on PATH. New article files will appear; then rebuild the vector store.

8. API Reference

---

Base URL: `http://localhost:8000`

### 8.1 GET /health

Response 200:

```
{
  "status": "healthy",
  "message": "ConvoTrack QA Agent API is running and agent is initialized.",
  "agent_initialized": true
}
```

Errors: 503 if agent failed to initialize.

### 8.2 POST /ask

Request body:

```
{ "question": "What emerging trends connect influencer engagement to consumer purchase behavior?" }
```

(Note: client does NOT send analysis_type; router chooses it.)

Successful response:

```
{
  "question": "...",
  "answer": "🎯 **Detailed Strategic Business Analysis**\n ... formatted markdown ...",
  "sources": [
     {
       "content": "Chunk text ...",
       "url": "https://convotrack.ai/case-studies/...",
       "article_number": "12"
     },
     ...
  ],
  "agent_type": "strategic_analysis",
  "confidence": "high",
  "analysis_type": "strategic"
}
```

Error responses:

-   400: empty question
-   503: agent not initialized
-   500: internal processing error (trace logged server-side)

Rate / Performance Considerations:

-   Each `/ask` triggers: routing LLM call + retrieval + analysis LLM call + formatting.
-   Increase/decrease retrieved chunks via `search_kwargs={"k": 15}` in `qa_agent_ai.py`.

9. Frontend UX Highlights

---

-   Real‑time connection badge (Online / Offline / Connecting).
-   Animated message ingress with Framer Motion.
-   Analysis type chip (auto‑selected by router) visible atop each bot response.
-   Citation History sidebar: groups sources per user query, expandable to view raw chunk content & link back to original URL.
-   Mobile responsive drawer for citations.
-   Markdown rendering of structured answer (headings, lists, emphasis preserved).

10. Multi‑Agent Design

---

Roles (inside `qa_agent_ai.py`):

-   Manager (AdvancedCaseStudyQAAgent)
    -   Intent routing (LLM classifier) → analysis type
    -   Orchestrates research → analysis → synthesis
    -   Compiles final JSON payload
-   ResearchAgent
    -   Similarity retrieval over Pinecone vector store (k=15)
-   AnalysisAgent
    -   Selects prompt template (all specialized types reuse enhanced analytical prompt)
    -   Runs detailed chain with Groq Llama3 70B
-   SynthesizerAgent
    -   Adds human‑friendly headers, footers, contextual disclaimers per analysis type

11. Customization Tips

---

| Goal                      | Where to Change                                                                                    |
| ------------------------- | -------------------------------------------------------------------------------------------------- |
| Adjust retrieval depth    | `search_kwargs` in `AdvancedCaseStudyQAAgent.__init__`                                             |
| Add new analysis category | Add to router prompt + templates dict, update frontend analysisTypes list if you want chip styling |
| Change embedding model    | `repo_id` in `VectorStoreManager` (ensure dimension matches index)                                 |
| Force index rebuild       | Run `document_loader.py` main or add `force_rebuild=True` during startup                           |
| Temperature / creativity  | `temperature` param in `ChatGroq` init                                                             |
| Chunk size / overlap      | `RecursiveCharacterTextSplitter` in `DocumentLoader`                                               |
| Add auth to API           | Wrap FastAPI endpoints with dependency or API key logic                                            |

12. Troubleshooting & Diagnostics

---

Issue -> Remedy:

-   GROQ_API_KEY not found: Ensure `.env` is in `qa_agent/` directory (same working dir when launching) and variable spelled correctly.
-   Pinecone authentication error: Confirm key + region specification (serverless us-east-1). If index dimension mismatch, delete index in dashboard and rebuild.
-   HuggingFace 403: Token lacks access / rate-limited – verify scope or switch to local embedding model (would require code changes to use `HuggingFaceEmbeddings` offline).
-   Empty answers: Check that `.txt` corpus actually has meaningful content beyond headers; verify retrieval by running `python qa_agent/document_loader.py` and test similarity search printout section.
-   Selenium fails to start: Install Chrome & matching chromedriver; or switch to undetected-chromedriver / headless mode adjustments.
-   CORS errors in browser: Ensure frontend requests exactly `http://localhost:8000` and that origin (`http://localhost:5173` or `3000`) is included in `allow_origins` list.
-   High latency: Reduce k from 15 to e.g. 8; possibly downgrade model; enable streaming (not yet implemented) as an enhancement.

Logging: Server prints lifecycle steps (init, routing classification, analysis type chosen). Add more granular logs inside each agent as needed.

13. Roadmap / Next Ideas

---

-   Streaming token output to frontend (Server-Sent Events or WebSocket) with incremental markdown rendering.
-   Add evaluation tests: retrieval recall, hallucination checks.
-   Caching layer (question → answer) for repeated queries.
-   Query expansion / hybrid (sparse + dense) retrieval.
-   Add authentication & basic usage metering.
-   Observability: structured logging + trace IDs.
-   Prompt specialization per analysis type (currently reuses single enhanced template).
-   Add unit tests (pytest) for document loading and response schema integrity.

14. License

---

Add your preferred license here (e.g., MIT). Include attribution notices for third‑party models/services (Groq, Pinecone, HuggingFace, etc.).

---

## Quick Start (TL;DR)

```
# Backend
cd qa_agent
python -m venv .venv && .venv\Scripts\activate
pip install -r ..\requirements.txt
echo GROQ_API_KEY=...> .env & echo PINECONE_API_KEY=...>> .env & echo HUGGINGFACE_API_TOKEN=...>> .env
python fastapi_server.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173, ask a question, expand citations.

---

Contributions & feedback welcome. Enjoy exploring autonomous BI with ConvoTrack!

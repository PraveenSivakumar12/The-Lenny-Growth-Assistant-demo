# The Lenny Growth Assistant
> An AI-powered full-stack SaaS workspace grounded in Lenny’s Podcast transcripts. Built with React, TypeScript, FastAPI, SQLAlchemy, and a custom lexical-similarity retrieval engine.

---

## 🌟 Key Features

* **🎙️ Grounded in the Official Starter Corpus:** Fetches the permitted public starter transcripts at first startup, builds a local searchable chunk index, and returns source citations. The raw dataset and derived full-text chunk index are excluded from Git because the source license prohibits raw-file redistribution.
* **🔄 Seamless Multi-Turn Context & Session Isolation:** Follow-up questions maintain memory within the conversation thread without cross-thread contamination.
* **✍️ Ship 30 for 30 Essay Generation Skill:** Encodes Dickie Bush and Nicolas Cole's framework (1-3-1 hook cadence, skimmable subheadings, selective bolding, bullet points, Golden Takeaway, ~1,250 words).
* **🖥️ Interactive Artifact Viewer:** Live Preview and Code tabs for generated Markdown essays and interactive HTML/CSS webpage widgets.
* **🛡️ Sandboxed Security Boundary:** Untrusted model-generated HTML is rendered in an isolated `iframe` with `sandbox="allow-scripts"` (strictly omitting `allow-same-origin`), preventing cookie theft or DOM compromise.
* **🎛️ Local Ollama & Cloud Model Switching:** Run 100% locally and privately with Ollama (e.g. Llama 3.2), or switch instantly to OpenAI (GPT-4o) or Anthropic (Claude 3.5 Sonnet).
* **💾 Persistent Storage & Migrations:** Powered by SQLAlchemy and Alembic migrations, supporting PostgreSQL (via Docker Compose) with automatic zero-setup SQLite fallback for local development.

---

## ⚠️ Public demo security note

This submission is currently a **demo, not a multi-user production service**: it has no authentication or per-user ownership checks for conversations/artifacts. Do not enter confidential content. Public access can also incur model-provider charges; configure provider-side usage limits. Add authentication, ownership enforcement, and rate limiting before production use.

## Dataset source and license

The knowledge base is fetched from [LennysNewsletter/lennys-newsletterpodcastdata](https://github.com/LennysNewsletter/lennys-newsletterpodcastdata). Review its [LICENSE.md](https://github.com/LennysNewsletter/lennys-newsletterpodcastdata/blob/main/LICENSE.md) before use. This repository intentionally excludes downloaded raw transcripts and generated full-text chunk indices; `scripts/bootstrap_knowledge.py` fetches them locally or at deployment runtime.

## 🏗️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, React-Markdown, Remark-GFM |
| **Backend** | Python 3.11, FastAPI, Pydantic V2, SQLAlchemy 2.0, Alembic, Uvicorn, AsyncPG, AioSQLite |
| **AI / RAG** | Ollama (Local), OpenAI / Anthropic (Cloud), IDF-weighted lexical retrieval + generated NumPy index |
| **Testing** | Pytest (Backend, 13 test cases), Vitest (Frontend), TestClient |
| **Deployment** | Docker, Docker Compose, Railway, Environment Variables (.env) |

---

## 🚀 Quick Start Guide

### Prerequisites
* **Python 3.10+** (tested on 3.11)
* **Node.js 18+** & npm
* (Optional) **Ollama** for running models locally ([Install Ollama](https://ollama.ai))
* (Optional) **Docker Desktop** for multi-container deployment

---

### Step 1: Clone and Set Up Environment Variables

```bash
cd "The Lenny Growth Assistant"
cp .env.example .env
```

Your `.env` comes pre-configured with working local defaults:
* Default Database: Local SQLite (`./data/lenny_growth.db`)
* Default Provider: `ollama`; if the selected provider is unavailable, the app shows a retry/error response rather than silently switching models.

If you have cloud API keys, add them to `.env`:
```ini
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

---

### Step 2: Backend Setup & Transcript Ingestion

1. **Create and activate Python virtual environment:**
   ```bash
   python -m venv backend/venv
   # Windows:
   backend\venv\Scripts\activate
   # Linux/macOS:
   source backend/venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run database migrations:**
   ```bash
   # Windows:
   $env:PYTHONPATH="backend"
   alembic -c backend/alembic.ini upgrade head

   # Linux/macOS:
   PYTHONPATH=backend alembic -c backend/alembic.ini upgrade head
   ```

4. **Fetch the licensed starter corpus and build the index:**
   *(Raw transcripts are downloaded into a local-only ignored directory; neither the raw files nor the derived full-text index is committed.)*
   ```bash
   # Run from the project root
   python scripts/bootstrap_knowledge.py
   ```
   *The first run requires internet access to the official starter repository. The index is generated locally.*

5. **Start FastAPI Backend Server:**
   ```bash
   python -m app.main
   ```
   *Backend is running at [http://localhost:8000](http://localhost:8000).*  
   *Interactive OpenAPI Docs available at [http://localhost:8000/docs](http://localhost:8000/docs).*

---

### Step 3: Frontend Setup

Open a new terminal window:

```bash
cd frontend
npm install
npm run dev
```

*Frontend is running at [http://localhost:5173](http://localhost:5173).*

---

### Step 4: (Optional) Local Ollama Setup

To run models locally without any cloud API keys:
1. Download Ollama from [ollama.ai](https://ollama.ai).
2. In your terminal, pull and run Llama 3.2 (or Mistral):
   ```bash
   ollama run llama3.2
   ```
3. Ollama runs on `http://localhost:11434`. The Lenny Growth Assistant will automatically detect it!

---

## 🐳 Docker Compose Deployment (Full Stack with PostgreSQL)

To launch the combined React + FastAPI web service and PostgreSQL:

```bash
docker compose up --build
```

Services started:
* **PostgreSQL:** Port `5432`
* **Web app (React + FastAPI):** Port `8000`

The first container start downloads the permitted starter source and builds a runtime-only index. Set `DEFAULT_LLM_PROVIDER=openai` and a valid `OPENAI_API_KEY` in `.env` for a working cloud model; use local Ollama for the required offline demo.

---

## 🧪 Running Automated Tests

### Backend Pytest Suite (13 Tests)
Validates API endpoints, session isolation, RAG retriever, Ship 30 essay engine, artifact creation, and model providers:

```bash
# Windows:
$env:PYTHONPATH="backend"
backend\venv\Scripts\pytest backend\tests -v

# Linux/macOS:
PYTHONPATH=backend pytest backend\tests -v
```

### Frontend Vitest Suite
```bash
cd frontend
npm test
```

### Manual UI Test Plan
See [TEST_PLAN_MANUAL.md](TEST_PLAN_MANUAL.md) for 9 detailed end-to-end test scenarios.

---

## 📚 Educational Documentation & Architecture

* **[LEARNING_GUIDE.md](LEARNING_GUIDE.md):** Complete beginner guide explaining request lifecycles, files to study first, database schemas, and debug recipes.
* **[PRD.md](PRD.md):** Product Requirements Document including success metrics and user journeys.
* **[architecture.md](architecture.md):** System architecture, security sandbox specifications, and module contracts.
* **[design.md](design.md):** UI design system, color tokens, and responsive layout specifications.
* **[DEMO_GUIDE.md](DEMO_GUIDE.md):** 2–3 minute camera-on YouTube demo script aligned with the assignment.

---

## 🛠️ Troubleshooting

* **Backend cannot find module `app`:**
  Make sure you set `PYTHONPATH=backend` before running commands.
* **Ollama Connection Refused:**
  Ensure Ollama is started by running `ollama serve`. If Ollama is unavailable, the app returns a provider-unavailable message (and source citations when retrieval succeeded); choose a working model provider to generate a synthesis.
* **Database Migrations Error:**
  Ensure you pass the config flag `-c backend/alembic.ini` when running Alembic.


## ☁️ Deploy to Railway (single service + PostgreSQL)

The root `Dockerfile` builds the frontend and serves it from FastAPI, so the browser and API share one public origin. This avoids the Compose-only `backend:8000` proxy address in `frontend/nginx.conf`. The image contains application code and a runtime bootstrapper—not the licensed transcript files or generated text index. The bootstrap downloads the permitted starter corpus when the container starts; conversation data lives in PostgreSQL.

1. Create a **public GitHub repository** from this cleaned project directory. Do not copy `.env`; rotate any credential that was ever stored in the previous ZIP.
2. In Railway, create a project and add a **PostgreSQL** service.
3. Add a web service from the GitHub repository. Keep the repository root as the service root so Railway finds the root `Dockerfile` and `railway.json`.
4. In the web service variables, add `DATABASE_URL` as a reference to the PostgreSQL service's `DATABASE_URL`, then add `DEFAULT_LLM_PROVIDER=openai`, `OPENAI_API_KEY` (a newly generated key), `OPENAI_MODEL=gpt-4o-mini`, and `DEBUG=false`. Do not define `SYNC_DATABASE_URL`; the app derives a synchronous URL for migrations from `DATABASE_URL`.
5. Deploy, generate a public domain under Networking, then verify `/api/health` and `/docs`. Open the base domain to test the UI.

**Ollama note:** `OLLAMA_BASE_URL=http://localhost:11434` works only when the backend and Ollama are on the same machine/network namespace. It will not reach Ollama running on your Windows laptop from Railway. For the required demo, run Ollama locally and demonstrate the local provider; for a cloud demo use the OpenAI provider. A private Ollama service can be deployed separately, but that adds resource cost and more setup.

See [DEPLOYMENT_RAILWAY.md](DEPLOYMENT_RAILWAY.md) for the exact variables and smoke tests, and [AUDIT_REPORT.md](AUDIT_REPORT.md) for known assignment gaps that still need work before submission.

# System Architecture Document
## The Lenny Growth Assistant

**Status:** Approved  
**Author:** Senior Full-Stack AI Engineer & System Architect  
**Version:** 1.0.0  

---

## 1. High-Level Architectural Overview

The Lenny Growth Assistant is built as a clean, decoupled, layered web application. It is deliberately organized so that each layer has one clear responsibility.

```mermaid
graph TD
    subgraph Client["Frontend Client (React + TypeScript + Vite)"]
        UI_Nav["Sidebar Navigation & Sessions"]
        UI_Chat["Chat Workspace & Markdown Renderer"]
        UI_Artifacts["Artifact Viewer (Sandboxed Iframe)"]
        UI_Models["Provider / Model Selector"]
    end

    subgraph API_Gateway["FastAPI Application"]
        Router_Health["/api/health"]
        Router_Conv["/api/conversations"]
        Router_Chat["/api/chat"]
        Router_Skills["/api/skills"]
        Router_Artifacts["/api/artifacts"]
        Router_Models["/api/models"]
    end

    subgraph Business_Layer["Core Services & Agent Routing"]
        AgentRouter["Agent Router & Tool Dispatcher"]
        EssaySkill["Ship 30 for 30 Skill Engine"]
        ArtifactEngine["Artifact Generator & Validator"]
        RAGRetriever["RAG Transcript Retriever"]
    end

    subgraph Provider_Layer["Model Provider Abstraction"]
        BaseProvider["BaseLLMProvider Interface"]
        OllamaP["Ollama Provider (Local)"]
        OpenAIP["OpenAI Provider (Cloud)"]
        AnthropicP["Anthropic Provider (Cloud)"]
    end

    subgraph Storage_Layer["Storage & Indexing"]
        PostgresDB[("PostgreSQL / SQLite Database\nSessions, Messages, Artifacts")]
        VectorStore[("Vector Index\n50+ Transcripts & Metadata")]
    end

    Client -->|REST API Requests| API_Gateway
    API_Gateway --> Business_Layer
    Business_Layer --> Provider_Layer
    Business_Layer --> Storage_Layer
    Provider_Layer -->|HTTP / Ollama API| OllamaP
    Provider_Layer -->|HTTPS API| OpenAIP
    Provider_Layer -->|HTTPS API| AnthropicP
```

---

## 2. Backend Architecture and Module Organization

The backend is built with Python 3.11 and FastAPI. To make the codebase beginner-friendly, every domain is isolated in its own folder:

```
backend/
├── app/
│   ├── api/             # FastAPI API route controllers
│   │   ├── health.py        # System health & diagnostic endpoints
│   │   ├── conversations.py # Conversation lifecycle (CRUD)
│   │   ├── chat.py          # Chat generation & stream handling
│   │   ├── skills.py        # Dedicated agent skills (Ship 30 essay, etc.)
│   │   ├── artifacts.py     # Artifact creation, listing, retrieval
│   │   └── models.py        # Model list & active provider configuration
│   ├── core/            # Core settings, database connection, logging
│   │   ├── config.py        # Pydantic BaseSettings for .env variables
│   │   ├── database.py      # SQLAlchemy async/sync engine & session manager
│   │   └── logging.py       # Structured JSON/console logger
│   ├── models/          # Data schemas
│   │   ├── db_models.py     # SQLAlchemy ORM table definitions
│   │   └── schemas.py       # Pydantic request and response schemas
│   ├── providers/       # LLM provider abstraction layer
│   │   ├── base.py          # Abstract base provider class
│   │   ├── ollama_provider.py    # Local Ollama client
│   │   ├── openai_provider.py    # OpenAI cloud client
│   │   ├── anthropic_provider.py # Anthropic cloud client
│   │   └── router.py        # Provider factory and fallback resolver
│   ├── rag/             # Retrieval-Augmented Generation subsystem
│   │   ├── chunker.py       # Podcast transcript splitter
│   │   ├── embeddings.py    # Lightweight feature-hash vector generation for experiments
│   │   ├── vector_store.py  # Persisted feature-hash vectors and lexical index
│   │   └── retriever.py     # Top-k similarity retrieval with metadata enrichment
│   ├── agent/           # Agent tools and skill workflows
│   │   ├── tools.py         # Tool specifications and execution functions
│   │   ├── prompts.py       # Grounding and system prompts
│   │   ├── runner.py        # Tool-use agent loop and router
│   │   └── essay_skill.py   # Ship 30 for 30 essay generation engine
│   └── main.py          # FastAPI application entrypoint and middleware
```

---

## 3. Database Schema and Persistence

The database stores conversations, message turns, source citations, and generated artifacts.

### Entity-Relationship Diagram
```mermaid
erDiagram
    CONVERSATION ||--o{ MESSAGE : contains
    CONVERSATION ||--o{ ARTIFACT : generates

    CONVERSATION {
        string id PK "UUID"
        string title "Conversation title"
        string user_id "Anonymous / local user identifier"
        datetime created_at
        datetime updated_at
    }

    MESSAGE {
        string id PK "UUID"
        string conversation_id FK
        string role "user | assistant | system"
        text content "Message body"
        json sources "Array of source citations"
        string model_used "Model name used for turn"
        datetime created_at
    }

    ARTIFACT {
        string id PK "UUID"
        string conversation_id FK
        string title "Artifact title"
        string artifact_type "markdown | html"
        text content "Raw code / markdown / HTML"
        json metadata_info "Word count, summary, etc."
        datetime created_at
        datetime updated_at
    }
```

### PostgreSQL & Database Compatibility Strategy
1. **Primary Target:** PostgreSQL accessed via SQLAlchemy with `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lenny_growth`.
2. **Local Fallback:** On development machines without a running PostgreSQL daemon or Docker, the backend gracefully defaults to SQLite (`sqlite+aiosqlite:///data/lenny_growth.db`), ensuring zero friction for developers while maintaining full PostgreSQL support for Docker Compose deployments.
3. **Migrations:** Alembic manages schema versioning and schema migrations reproducibly.

---

## 4. Transcript Ingestion and RAG Subsystem

The application grounds its answers in genuine transcripts from Lenny’s Podcast:

1. **Source Data:** 50 real podcast Markdown transcripts with structured frontmatter (`title`, `guest`, `date`, `description`, `post_url`).
2. **Text Normalization:** Cleans speaker cues (`**Speaker** (00:00:00):`) and retains timestamps for exact provenance.
3. **Chunking Strategy:**
   * Chunk size: 500–700 words (approx. 700 tokens) with 100-word sliding overlap.
   * Chunks preserve the `episode_title`, `guest`, `date`, `source_url`, and `timestamp_range`.
4. **Embeddings & Vector Index:**
   * A persisted 512-dimensional feature-hash matrix is retained for reproducible ingestion and experimentation; it is not a pretrained semantic embedding model.
   * Current serving retrieval uses an IDF-weighted real-token overlap reranker over transcript/title/guest text to reduce false matches from feature-hash collisions.
   * Retrieval normalizes query-term coverage to a 0–1 relevance score, applies a threshold, and formats the top chunks with provenance metadata.
5. **Source Traceability:**
   Each retrieved chunk includes:
   * `title`: Episode name
   * `guest`: Interviewee
   * `url`: Direct link to Lenny's Newsletter article
   * `excerpt`: The exact spoken dialogue
   * `relevance_score`: IDF-weighted lexical query-term coverage (normalized 0–1)

---

## 5. Model Provider Abstraction

To ensure zero vendor lock-in, all model interactions pass through the `BaseLLMProvider` interface:

```python
class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass
```

### Supported Providers:
1. **Ollama (Local):** Connects to `http://localhost:11434/api/chat` using local models like `llama3.2`, `mistral`, or `qwen2.5`.
2. **OpenAI (Cloud):** Connects to OpenAI API using models like `gpt-4o` or `gpt-4o-mini`.
3. **Anthropic (Cloud):** Connects to Anthropic API using models like `claude-3-5-sonnet` or `claude-3-haiku`.
4. **Mock / Offline Provider:** If no remote or local LLM is active, a structured offline provider returns informative assistance and diagnostics, preventing unhandled runtime exceptions.

---

## 6. Agent Architecture and Skill Routing

Rather than giving an autonomous agent unrestricted filesystem or command-line permissions, the system implements a **Deterministic Tool-Use Router**:

1. **Query Classifier & Router:**
   * Evaluates user intent based on query text and context.
   * Routes to `PodcastRAGTool` for domain questions.
   * Routes to `Ship30EssayTool` for essay requests ("write an essay", "atomic essay", "ship 30 format").
   * Routes to `ArtifactGeneratorTool` for UI, HTML, or standalone Markdown specifications.
   * Routes to `GeneralAssistanceTool` for meta questions.
2. **Ship 30 for 30 Skill Engine:**
   * Follows the Dickie Bush & Nicolas Cole methodology.
   * Enforces 1-3-1 hook cadence, scannable subheadings, bullet lists, selective bolding, and a high-impact takeaway.
   * Grounded with transcript citations to ensure zero fabricated guest quotes.
   * Produces an essay of ~1,250 words.

---

## 7. Artifact Generation & Security Isolation

Generated artifacts (HTML/CSS components, dashboards, landing pages, Markdown briefs) present a potential Cross-Site Scripting (XSS) risk if executed directly in the main DOM.

### Isolation Architecture:
```
Main React Application (Origin: localhost:5173)
  │
  ├── React State (User conversation, session tokens, API keys)
  │
  └── <iframe
        sandbox="allow-scripts"
        srcDoc="<!DOCTYPE html><html>...untrusted model HTML...</html>"
      />
```

### Security Guarantees:
* The `sandbox="allow-scripts"` flag allows standard interactive HTML/JS widgets (e.g. calculators, charts) to operate internally.
* Noticeably **omits** `allow-same-origin`, `allow-top-navigation`, and `allow-modals`.
* Because `allow-same-origin` is omitted, the iframe runs in a unique opaque origin:
  1. The iframe **cannot** access `window.parent` or `window.top`.
  2. The iframe **cannot** read parent `localStorage`, `sessionStorage`, or cookies.
  3. The iframe **cannot** make credentialed requests on behalf of the host app.
  4. Script execution is entirely isolated inside the frame boundary.

---

## 8. Frontend Architecture

* **Framework:** React 18 with TypeScript and Vite.
* **Styling:** Tailwind CSS with custom theme variables (Deep navy `#0B1120`, soft slate `#F8FAFC`, violet accents `#7C3AED`, royal blue `#2563EB`).
* **Icons:** Lucide-React.
* **Markdown:** `react-markdown` with syntax highlighting and GitHub-flavored markdown (`remark-gfm`).
* **Component Structure:**
  * `Sidebar/`: Session list, search, new chat button, rename/delete modals.
  * `Chat/`: Message stream, user/assistant bubbles, citation cards, model selector bar, prompt input.
  * `ArtifactViewer/`: Collapsible right panel, Preview tab (sandboxed iframe), Code tab (syntax highlighting), copy button, download button.

---

## 9. Observability and Error Resilience

1. **Structured Logging:** All API requests, vector searches, and LLM calls log structured metadata (duration, token count, status code, provider).
2. **Sensitive Data Redaction:** API keys and raw authorization headers are never logged.
3. **Resilient Failure Handling:**
   * **Ollama Offline:** Warns the user with a friendly setup guide instead of a 500 crash.
   * **Missing Cloud Keys:** Returns clear guidance instructing the user to configure `.env`.
   * **Empty Retrieval:** Acknowledges lack of transcript evidence without hallucinating.
   * **Database Outage:** Reports specific database health status via `/api/health`.

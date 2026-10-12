# Project audit: The Lenny Growth Assistant

**Audit basis:** source and documentation in the provided ZIP, compared with the 12 October 2026 Forward Deployed Engineer take-home assignment. This is a code/file review plus unit tests, Python compile checks, and frontend TypeScript checking. Docker build and live Railway deployment remain unverified in this environment.

## Requirement-by-requirement summary

| Assignment requirement | Status | Evidence / caveat |
|---|---|---|
| FastAPI backend, clear API routes, validation, errors and health route | **Mostly present** | FastAPI routers and Pydantic schemas exist; health checks DB, model availability and index count. Production debugging defaults needed to be safer and are set to `DEBUG=false` in the container. |
| Agent layer using Anthropic Claude Agent SDK or Pi Coding Agent | **Missing / not compliant yet** | Provider adapters call OpenAI/Anthropic HTTP APIs directly. `AgentOrchestrator` classifies intent with keyword matching. Tool schemas in `backend/app/agent/tools.py` are defined but not executed through the required agent SDK/runtime. |
| Session isolation and PostgreSQL persistence | **Partially present** | SQLAlchemy models and PostgreSQL URL support exist; conversations carry `user_id`. The release copy normalizes Railway's `postgresql://` URL for asyncpg and infers a synchronous URL for its sync engine. No authentication or per-user authorization is implemented; this is a significant public-demo risk regardless of PRD scope. |
| Switchable cloud/local LLM provider | **Partially present** | Ollama, OpenAI and Anthropic adapters plus provider selection exist. `ChatRequest.model` overrides are passed through to provider calls in this release copy. |
| Local Ollama for demo | **Code present, not runtime-verified** | Ollama provider is implemented. It requires Ollama running on the same machine/network. Cloud Railway cannot reach your laptop's `localhost:11434`. Demonstrate this part locally. |
| Lenny transcript knowledge base, ingestion, indexing, provenance | **Present with quality caveat** | The transcript bootstrap script downloads the official starter corpus at runtime; raw transcripts and generated full-text index files are excluded from the public repository due to source terms. The persisted feature-hash vectors are not a pretrained semantic model; runtime retrieval now uses IDF-weighted lexical term overlap, with a regression test for off-topic abstention. Treat it as explainable lexical retrieval, not true semantic retrieval. |
| Grounded answers and source citations | **Partially present; needs hardening** | Retriever and citation schemas exist. Prompt grounding is present, but weak retrieval can supply irrelevant chunks; verify the answer abstains when evidence is insufficient. |
| Ship 30 for 30 skill (~1,250 words) | **Partially present; needs hardening** | Dedicated `essay_skill.py` exists. The release copy now raises an error when evidence is empty or a provider fails instead of substituting generic unsupported claims; run the live essay smoke test after deployment. |
| Markdown and HTML artifacts rendered in-app | **Mostly present** | Artifact endpoints and viewer tabs exist. Sandboxed iframe uses `sandbox="allow-scripts"` without `allow-same-origin`; the release copy adds a restrictive Content Security Policy to block external network requests, forms, frames and object content. |
| One-command startup and safe environment sample | **Partially present** | Compose exists for local runs; original repo had no `.gitignore`/`.dockerignore`. Release copy adds these and a root Dockerfile. |
| Structured logs, error resilience, health | **Partially present** | Basic logging and provider availability checks exist. Database startup fails loudly; no deployment runtime was available here to test actual logs/recovery. |
| README, PRD, design.md, architecture.md | **Present** | All four are in the ZIP. The original README had hard-coded local file URLs; these are removed in this release copy. |
| Tests | **Backend tests pass; deploy build unverified** | All 13 backend tests pass when the missing `aiosqlite` test dependency is provided. Python compile checks and frontend TypeScript type-check pass. Vitest could not start from the copied Windows `node_modules` because the Linux Rollup optional binary is missing. The full frontend test/build still needs a clean Linux `npm ci`; the root Dockerfile and GitHub Actions do this in their Linux build environments, but those results have not been observed here. |
| Public GitHub repository, agent transcripts/logs, 2–3 min YouTube demo | **Missing as deliverables** | No remote repository URL, no actual coding-agent logs, and no video are present. A placeholder `agent-transcripts/README.md` is only a reminder; record real attempts and corrections, do not fabricate logs. Publish the cleaned source and upload the required 2–3 minute camera-on video. |

## High-priority security findings

1. The original `.env` contains a non-empty OpenAI API key. Treat it as exposed and revoke/rotate it in the provider dashboard before any deployment. The exact value is intentionally not reproduced here.
2. The original ZIP includes `backend/venv`, `frontend/node_modules`, `frontend/dist`, `.pyc` caches, and local SQLite databases. These create a large, host-specific upload and may disclose chat data. They are removed from this release copy; the Docker image builds frontend dependencies cleanly.
3. Do not push the original ZIP or the original `.env` to a public repository. If the key has already been committed, removing it in a later commit is insufficient; revoke the key and clean Git history if needed.

## Changes made in this Railway-ready copy

- Added a root multi-stage Dockerfile to build the frontend on Linux and run frontend + FastAPI from one origin.
- Added the PostgreSQL sync driver needed when SQLAlchemy creates its Alembic-compatible sync engine on Railway.
- Added a restrictive CSP to the already sandboxed artifact iframe; it blocks external network connections, frames, forms, and object content while permitting inline artifact scripts/styles.
- Removed database exception details from the public health response.
- Passed chat model overrides into provider calls and changed Q&A/essay fallback behavior to abstain instead of inventing unsupported transcript claims.
- Changed runtime retrieval to IDF-weighted lexical term coverage and added an automated off-topic abstention regression test.
- Added static SPA serving in FastAPI; API and docs paths still return API responses/404s.
- Normalized Railway's `postgres://` / `postgresql://` URL for asyncpg and inferred a sync URL for Alembic.
- Made `.env` and data path resolution independent of whether local commands start from the repo root or `backend/`.
- Set the code-level default `DEBUG` to false.
- Added `.gitignore`, `.dockerignore`, `railway.json`, a Railway deployment guide, and a GitHub Actions workflow for backend/frontend checks.
- Removed secret-bearing `.env`, local dependency trees, generated frontend bundles, Python caches and SQLite databases from the clean copy.

## Additional public-deployment risk

The app currently has no authentication or per-user authorization. Conversation listing defaults to a shared `default_user`, and fetch/update/delete/artifact endpoints do not verify an authenticated owner. A public demo therefore exposes conversations and allows destructive actions by conversation ID. Do not store private data; before any production/internal use, add authentication, enforce ownership checks on every relevant endpoint, and implement request/rate limits. A public model-backed endpoint may incur API charges.

## Verification limits

- Backend: `PYTHONPATH=backend pytest backend/tests -q` passed all 13 tests after supplying `aiosqlite` from the archive’s existing vendored test environment; the temporary copy was removed afterward. There are 24 `datetime.utcnow()` deprecation warnings to clean up.
- Python compile checks pass. Frontend TypeScript type-check passed earlier; a full Linux npm build still needs verification using a clean `npm ci`.
- Docker is not installed in this execution environment. The GitHub and Railway integrations report as installed, but their action tools are not exposed to this current response session; therefore I have not created a remote repository, deployed a service, or claimed a live URL.


## Dataset distribution note

The included Lenny's Data license allows personal, non-commercial projects but prohibits redistribution of raw starter dataset files. The release package excludes source transcript Markdown and generated full-text chunks; `scripts/fetch_lenny_data.py` downloads the official starter corpus at run time, and `scripts/bootstrap_knowledge.py` builds a local-only index. See the [official source license](https://github.com/LennysNewsletter/lennys-newsletterpodcastdata/blob/main/LICENSE.md).

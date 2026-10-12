# Railway deployment guide

## Before publishing

- Rotate/revoke the OpenAI API key present in the original ZIP's `.env`. Do not reuse it.
- Publish only the cleaned project: `.env`, local databases, `backend/venv`, `frontend/node_modules`, caches, host-built `dist`, raw transcript files, and the derived full-text index are excluded.
- Create a new public repository or clean the old repository history if secrets were committed. Removing a key from the current tree does not remove it from Git history.

## Public-demo safety warning

The current application has **no authentication or per-user authorization**. Conversations and artifacts are not private: a visitor can list the default user's conversations, and endpoints allow retrieval, editing, or deletion by ID. A public deployment can also consume the configured model API quota. Do not use real customer data or private conversations, and set provider-side spend limits. For a production or genuinely internal deployment, implement authentication, authorize every conversation/artifact by user, and add rate limiting before exposing a public domain.

## Railway layout

- **PostgreSQL service:** persistent conversation, message, and artifact storage.
- **Web service:** build from this repo's root Dockerfile. It compiles the React UI and runs FastAPI as one same-origin service.
- **Knowledge data:** only bootstrap code ships in Git and the image. At runtime the service fetches the official starter corpus and creates its index in the container/volume. Raw transcripts and generated full-text chunks are never committed.

## Publish the clean source to GitHub

Create an **empty public repository** on GitHub (do not add a README or `.gitignore` there because this project already provides them). Extract this release ZIP, open PowerShell in the extracted project root, then run:

```powershell
git init
git add .
git status --short
# Inspect the staged file list before committing. It must not include .env,
# transcript Markdown files, data/index/metadata.json, or data/index/vectors.npy.
git commit -m "Prepare Lenny Growth Assistant demo"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/lenny-growth-assistant.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub account name and the URL with the empty repository you created. Only the cleaned source is included; runtime bootstrap code fetches the permitted public transcript starter set. The GitHub Actions quality workflow runs backend tests, frontend tests, and the frontend build on pushes and pull requests.

## Create and configure Railway services

1. In Railway, create a project and add a **PostgreSQL** service. Wait for it to finish provisioning.
2. Add a web service from the GitHub repository. Leave its root directory at the repository root (do not set it to `backend` or `frontend`) so Railway finds `Dockerfile` and `railway.json`.
3. In the web service’s Variables panel, set:

   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | Add a Railway reference to the PostgreSQL service’s `DATABASE_URL` (for example `${{Postgres.DATABASE_URL}}` if the service is named `Postgres`) |
   | `DEFAULT_LLM_PROVIDER` | `openai` |
   | `OPENAI_API_KEY` | A newly generated/rotated API key, stored only in Railway Variables |
   | `OPENAI_MODEL` | `gpt-4o-mini` |
   | `DEBUG` | `false` |
   | `APP_ENV` | `production` |

   Leave `SYNC_DATABASE_URL` unset. The database module transforms Railway's `postgresql://` URL into the asyncpg URL needed by FastAPI. Do not set `VITE_API_URL`; the frontend uses same-origin `/api` paths.

4. Deploy. Startup downloads the starter transcripts and builds the index before starting Uvicorn; the health check uses `/api/health`. Generate a public domain in the web service’s Networking settings.

## Smoke tests after deployment

1. Open `https://YOUR-DOMAIN/` and confirm the UI renders.
2. Open `https://YOUR-DOMAIN/api/health` and confirm the database reports `connected`, and `indexed_documents_count` is greater than zero. Provider status may show Ollama unavailable on Railway; that is expected unless you host a separate Ollama service.
3. Open `https://YOUR-DOMAIN/docs` and confirm FastAPI docs load.
4. In the UI, create a new conversation; ask a question that matches one of the available transcripts; confirm the answer includes citations. Ask a follow-up and verify it remains in that conversation. Create another conversation and verify the sessions are isolated.
5. Generate a Markdown essay and an HTML artifact, preview both, refresh the page, and confirm they persist. Inspect Railway Logs for provider/database failures.

## Troubleshooting

- **Database URL/driver error:** Ensure the web service references the PostgreSQL service's `DATABASE_URL`. Do not use a public external URL unless the service needs it.
- **Empty citations / zero indexed chunks:** Inspect Railway logs for the `bootstrap_knowledge.py` step and confirm outbound access to the official source repository. The data is fetched at runtime; do not commit raw transcripts or the derived full-text index to Git.
- **Ollama unavailable:** Expected on Railway if Ollama runs only on your laptop. Set `DEFAULT_LLM_PROVIDER=openai` and set a valid rotated key for the hosted deployment. Keep the local `.env` default as `ollama` for the required local demo.
- **Frontend assets return 404:** Confirm the deployment is built from the root `Dockerfile`, not the backend-only Dockerfile.
- **Build fails at npm ci:** Inspect the Railway build logs for package-lock errors. The root Dockerfile and GitHub Actions use `npm ci` on Linux to fetch correct platform-specific packages; do not upload Windows `node_modules`. The local extracted dependency folder is not a clean build environment.
- **Health check fails:** Open deployment logs, confirm the service binds to Railway's `$PORT`, and verify PostgreSQL is online.

## Important assignment gaps

The current source still needs an actual Claude Agent SDK or Pi Coding Agent runtime integration, real coding-agent transcript/log files (record your actual attempts; do not fabricate them), and a 2–3 minute camera-on demo video. See `AUDIT_REPORT.md`. A successful deployment alone does not complete these requirements.

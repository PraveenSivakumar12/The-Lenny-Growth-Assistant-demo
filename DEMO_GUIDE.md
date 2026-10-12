# Demo Video Guide — The Lenny Growth Assistant

**Required target: 2–3 minutes, with your camera enabled throughout.** The assessment specifically asks for a short YouTube video showing the local Ollama demo and one important technical trade-off. Record the live app; do not narrate features that you have not verified on screen.

## Before recording

- Start Ollama and download a model: `ollama run llama3.2`.
- Start the backend after transcript bootstrap: from the repo root, activate your virtual environment, set `PYTHONPATH=backend`, and run `python -m app.main`.
- Start the frontend separately with `cd frontend`, `npm install`, and `npm run dev`.
- Verify that the model selector shows Ollama and the health endpoint reports indexed chunks.
- Keep your camera tile visible. Do not expose API keys, `.env`, or private data on screen.

## Suggested 2:30 script

### 0:00–0:20 — Problem and product

Show the app and introduce the use case:

> “The Lenny Growth Assistant helps product and growth teams ask questions of Lenny’s Podcast transcripts, turn evidence into a structured essay, and preview generated artifacts in one workspace. It uses React and TypeScript on the frontend, FastAPI on the backend, and PostgreSQL for persisted conversations.”

### 0:20–0:55 — Grounded Q&A and citations

Select **Ollama / local model** in the UI. Ask a focused question that matches a transcript available in the index, then point out the source citations. Ask an unrelated question and show that the assistant declines to answer when the archive does not provide enough evidence. Do not claim a citation is exact unless you have opened and checked it.

### 0:55–1:25 — Ship 30 for 30 essay

Ask for an essay topic that matches the retrieved source. Show the Markdown result and its citations in the artifact viewer. Highlight the hook, headings, useful takeaway, and source grounding. If generation fails because the local model cannot produce a long answer, show the error honestly instead of switching silently to unsupported claims.

### 1:25–1:55 — Artifact viewer and safety

Request a small HTML/CSS artifact, such as a retention calculator. Show **Preview** and **Code** tabs. Explain that generated HTML runs inside a sandboxed iframe with a restrictive Content Security Policy; do not paste or execute untrusted generated code directly in the main application DOM.

### 1:55–2:30 — Local model and trade-off

Show the Ollama model selection and, if useful, a terminal with `ollama run llama3.2`. Explain the trade-off:

> “The local model avoids sending prompts to a cloud model provider but may be slower or less capable on this machine. Retrieval is intentionally lexical and explainable rather than a hosted embedding service, which lowers operational complexity but can miss semantically related passages. The public demo also needs authentication and per-user authorization before it can safely handle confidential users or data.”

Close by showing one test/check or the project documentation.

## Publish checklist

- Keep the recording between 2 and 3 minutes.
- Keep your camera enabled; ensure voice and screen are readable.
- Do not show `.env`, keys, credentials, or private data.
- Upload to YouTube and set the visibility that lets evaluators access it.
- Add the video URL to your final submission notes/README after upload.

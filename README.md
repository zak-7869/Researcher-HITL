# Researcher AI Platform

<img width="4243" height="9226" alt="diagram" src="https://github.com/user-attachments/assets/05bf989d-2755-4529-a0a4-cbf37c1b1e23" />


Runnable starter for a source-grounded research agent using LangGraph, Groq, Tavily, FastAPI, and Next.js.

## Quick start

Requirements: Python 3.11+, Node.js 20+, Groq API key, Tavily API key.

1. For local development, copy `backend/.env.example` to `backend/.env` and add both API keys. For Docker Compose, also copy the root `.env.example` to `.env` at the repository root.
2. Backend:
   ```bash
   cd backend
   python -m venv .venv
   # Windows: .venv\Scripts\Activate.ps1
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
3. Frontend, in another terminal:
   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   npm run dev
   ```
4. Open http://localhost:3000. API docs: http://localhost:8000/docs.

Or run `docker compose up --build` from the repository root after setting `.env`.

## What is implemented

- **Harness engineering:** input validation, bounded iteration budget, external-call timeouts/retries, request IDs, rate limiting, error handling.
- **Loop engineering:** plan → search → deterministic evidence evaluation → bounded search loop → report.
- **Context engineering:** structured LangGraph state, capped source snippets, normalized source evidence.
- **Tool design:** Tavily is the only enabled external tool; search results are treated as untrusted evidence.
- **Memory:** per-run records are currently in process memory; restarting the backend clears them. Add PostgreSQL checkpointing and shared run storage before multi-replica deployment.
- **Orchestration:** conditional LangGraph edges and a post-report review status.
- **Guardrails/permissions:** bounded topic length, 1–3 iterations, limited result count, CORS, per-process rate limit, no arbitrary shell/write/email tools.
- **Human in the loop:** generated reports stay `pending_review` until the review endpoint is used.
- **Evals:** deterministic evaluator and API/schema tests (`cd backend && pytest -q`).
- **Observability:** structured logs, request IDs, Prometheus metrics at `/metrics`; optional LangSmith env vars.

## API
- `GET /api/health`
- `POST /api/research` body: `{"topic":"AI agent evaluation methods","max_iterations":2}`
- `GET /api/runs/{run_id}`
- `POST /api/research/{run_id}/review` body: `{"decision":"approve","comment":""}`
- `GET /metrics`

## Production checklist
This starter is not a security-audited production deployment. Before public use, add OIDC/JWT authentication, role-based authorization, PostgreSQL-backed checkpoints/run storage, Redis rate limiting, HTTPS ingress, AWS Secrets Manager, tenant isolation, retention/deletion controls, durable audit events, and CI evaluation gates. Never commit `.env` or API keys. Use a shared database if running more than one backend replica.

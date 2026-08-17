# Design Compatibility Checker

Design Compatibility Checker is an AI-assisted application for evaluating how closely a UI design can be implemented using a target component library. You supply a UI design — a screenshot or a Figma file — and the application analyzes its visible structure and semantics, then evaluates that representation against a component library to produce a compatibility report answering:

1. How compatible is the design with the target component library?
2. Which existing components and composition patterns should be used?
3. Which areas require customization?
4. Which areas likely require custom implementation?
5. What implementation risks or accessibility considerations are visible from the supplied design?

Material UI is the first supported component library. The project originated as an n8n proof-of-concept (see [`prototype/n8n/`](prototype/n8n/)); this repository is a conventional migration of that validated pipeline into typed application code, with explicit contracts, tests, APIs, and a proper frontend, replacing n8n's runtime orchestration.

The full product and architecture specification lives in [`PROJECT_SPEC.md`](PROJECT_SPEC.md). The phased build-out is tracked in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md).

## Architecture

The core architectural principle is a strict boundary between implementation-neutral design understanding and library-specific compatibility matching:

```text
              IMPLEMENTATION-NEUTRAL

Screenshot ──→ Vision Analysis ──┐
                                  │
                                  ├──→ DesignStructure
                                  │
Figma ───────→ Figma Parser ─────┘
                                  ↓
                           SemanticAnalysis
                                  ↓
                             DesignSummary

──────────────────────────────────────────────

                 LIBRARY-SPECIFIC

                           Retrieval
                                  ↓
                      CompatibilityMatcher
                                  ↓
                    CompatibilityAssessment
```

Design understanding (vision analysis, Figma normalization, semantic analysis, summary projection) never has knowledge of Material UI or any other component library. Library-specific knowledge is only introduced at the retrieval/matching boundary, which is what will eventually let the same design be evaluated against different component libraries. See `PROJECT_SPEC.md` sections 2–4 for the full rationale.

## Repository structure

This is a monorepo with two independently deployable services plus shared project docs:

```text
design-compatibility-checker/
├── frontend/             # Next.js (App Router) + TypeScript UI
│   ├── app/              # Routes, pages, and API route handlers
│   ├── lib/              # Frontend-only helpers (e.g. env resolution)
│   └── tests/            # Vitest + Testing Library
│
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/routes/   # HTTP route handlers
│   │   ├── core/         # Centralized configuration (app/core/config.py)
│   │   └── schemas/      # Pydantic domain contracts (DesignStructure,
│   │                     # SemanticAnalysis, DesignSummary, CompatibilityAssessment)
│   └── tests/            # Pytest unit tests
│
├── prototype/n8n/        # Sanitized reference export of the original n8n workflow
│
├── compose.yml           # Podman/Docker Compose service definitions
├── .env.example          # Documented environment variables for both services
├── PROJECT_SPEC.md       # Full product & architecture specification
└── IMPLEMENTATION_PLAN.md  # Phase 1 PR-by-PR build plan
```

Service-level implementation details (routes, services, and clients not yet built) will keep growing under `backend/app/` as later PRs add the Figma/screenshot input paths, semantic analysis, summary projection, retrieval, and compatibility matching.

## Tech stack

| | |
|---|---|
| Frontend | Next.js 16 (App Router), React 19, TypeScript, ESLint, Prettier, Vitest + Testing Library |
| Backend | FastAPI, Pydantic v2 / pydantic-settings, Ruff, Pytest, [uv](https://docs.astral.sh/uv/) |
| Containers | Podman + `podman compose` (Docker-compatible; no Docker Desktop dependency) |
| CI | GitHub Actions — lint, format check, type check, tests, and build for both services |

## Getting started

### Prerequisites

- [Podman](https://podman.io/) with `podman compose` (or a Docker-compatible equivalent)
- Node.js `>=20.9.0` and [pnpm](https://pnpm.io/) `10.34.5` (pinned in `frontend/package.json`'s `packageManager` field) — only needed for running the frontend outside a container
- Python `>=3.12` and [uv](https://docs.astral.sh/uv/) — only needed for running the backend outside a container

### Environment configuration

Copy the example environment file and fill in any values you need (all AI provider keys are optional until the corresponding pipeline stage is implemented):

```bash
cp .env.example .env
```

See the comments in [`.env.example`](.env.example) for what each variable controls.

### Run everything with Podman Compose

```bash
podman compose up --build
```

This builds and starts both services with health checks — the frontend waits for the backend to report healthy before starting. Once up:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend health check: [http://localhost:8000/health](http://localhost:8000/health)

Stop everything with:

```bash
podman compose down
```

### Run services individually (for active development)

**Backend**

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
pnpm install
pnpm dev
```

By default the frontend talks to `http://localhost:8000` for both server-side and browser requests when run this way (see `frontend/lib/env.ts`).

## Quality checks

Run these before opening a pull request; they mirror the checks CI runs on every push.

**Backend** (from `backend/`):

```bash
uv run ruff check .        # lint
uv run ruff format --check .  # format check
uv run pytest               # tests
```

**Frontend** (from `frontend/`):

```bash
pnpm lint          # ESLint
pnpm format:check  # Prettier
pnpm typecheck     # tsc --noEmit
pnpm test          # Vitest
pnpm build         # production build
```

## Continuous integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs the backend and frontend quality checks above as separate jobs on every push and pull request.

## Project status

This project is being built as a sequence of focused pull requests (see [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) for the full plan and completion rules for each):

- [x] **PR 1 — Project Foundation**: monorepo, Next.js + FastAPI skeletons, centralized config, health endpoints, Podman/Compose setup, and CI.
- [x] **PR 2 — Domain Schemas**: the core Pydantic contracts (`DesignStructure`, `SemanticAnalysis`, `DesignSummary`, `CompatibilityAssessment`) with unit tests. No external model calls yet.
- [ ] **PR 3 — Figma Input Path**
- [ ] **PR 4 — Screenshot Input Path**
- [ ] **PR 5 — Semantic Analysis**
- [ ] **PR 6 — Summary Projection**
- [ ] **PR 7 — Material UI Retrieval**
- [ ] **PR 8 — Compatibility Matcher**
- [ ] **PR 9 — Analysis Orchestration**
- [ ] **PR 10 — Frontend Analysis Flow**
- [ ] **PR 11 — Quality Hardening**
- [ ] **PR 12 — Documentation & Phase 1 Completion**

No AI pipeline functionality (vision analysis, Figma parsing, semantic analysis, retrieval, or compatibility matching) is implemented yet — the domain contracts these stages will produce and consume are defined and tested, but nothing calls an external model or API yet.

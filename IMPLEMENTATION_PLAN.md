# Phase 1 — Implementation Plan

Source of truth: `PROJECT_SPEC.md`

Phase 1 goal:

> Migrate the existing n8n Material UI compatibility checker into a conventional Next.js + FastAPI application with Podman-first local development and GitHub Actions CI.

Each step below should normally be implemented as an individual pull request.

---

## PR 1 — Project Foundation

Establish:

* monorepo structure
* Next.js + TypeScript frontend
* FastAPI backend
* centralized configuration
* `.env.example`
* basic health endpoints
* Podman-compatible container definitions
* `compose.yml`
* baseline frontend/backend quality tooling
* initial GitHub Actions CI

No AI pipeline functionality yet.

---

## PR 2 — Domain Schemas

Implement and test the core Pydantic contracts:

* `DesignStructure`
* layout/group/element/separator models
* repeated structures
* relationships
* custom patterns
* `SemanticAnalysis`
* `DesignSummary`
* `CompatibilityAssessment`
* mapping/warning models

No external model calls.

---

## PR 3 — Figma Input Path

Implement:

```text
Figma URL
→ validation
→ file-key extraction
→ Figma client
→ Figma graph retrieval
→ normalization
→ DesignStructure
```

Mock the Figma API in automated tests.

Do not implement semantic analysis.

---

## PR 4 — Screenshot Input Path

Implement:

```text
Screenshot
→ upload validation
→ OpenAI vision analysis
→ validated DesignStructure
```

Support optional textual context.

Mock OpenAI in automated tests.

Do not perform Material UI matching.

---

## PR 5 — Semantic Analysis

Implement:

```text
DesignStructure
→ SemanticAnalyzer
→ SemanticAnalysis
```

Preserve implementation-neutral semantics.

Mock the model provider in tests.

Do not introduce Material UI knowledge into this stage.

---

## PR 6 — Summary Projection

Implement:

```text
DesignStructure
+
SemanticAnalysis
→
DesignSummary
```

This must be deterministic Python.

Add focused unit tests.

No LLM call is permitted in this transformation.

---

## PR 7 — Material UI Retrieval

Implement:

```text
DesignSummary
→ relevant retrieval query
→ Qdrant
→ relevant MUI context
```

Use the existing `mui_component_docs` collection where available.

Mock Qdrant in automated tests.

Do not migrate documentation ingestion.

---

## PR 8 — Compatibility Matcher

Implement:

```text
DesignSummary
+
MUI context
→
Claude
→
CompatibilityAssessment
```

Require validated structured output.

Mock Anthropic in automated tests.

---

## PR 9 — Analysis Orchestration

Connect the backend stages into complete analysis flows:

```text
Screenshot
→ analysis pipeline
→ CompatibilityAssessment
```

and:

```text
Figma
→ analysis pipeline
→ CompatibilityAssessment
```

Keep route handlers thin.

Add API/service orchestration tests.

---

## PR 10 — Frontend Analysis Flow

Implement:

* screenshot upload
* optional context
* Figma URL input
* submission
* loading states
* error states
* compatibility report
* uploaded screenshot display
* customization findings
* accessibility considerations
* risks/open questions

Do not introduce authentication or persistence.

---

## PR 11 — Quality Hardening

Review the complete Phase 1 implementation for:

* duplicated logic
* leaky abstractions
* weak typing
* insufficient validation
* missing deterministic tests
* Material UI coupling in generic layers
* provider logic leaking into routes
* secret/configuration issues
* Podman incompatibilities

Run the complete quality suite.

Do not introduce new product functionality.

---

## PR 12 — Documentation & Phase 1 Completion

Finalize:

* root README
* architecture documentation
* Podman setup
* environment configuration
* local development instructions
* testing instructions
* lint/format/typecheck instructions
* project origin/n8n prototype explanation

Perform the final Phase 1 verification against `PROJECT_SPEC.md`.

---

# PR Completion Rule

For every PR:

1. Read `PROJECT_SPEC.md`.
2. Read this implementation plan.
3. Inspect the current repository before modifying code.
4. Confirm the PR's intended scope.
5. Preserve existing conventions.
6. Implement only the current PR.
7. Add appropriate tests.
8. Run applicable quality checks.
9. Fix failures introduced by the PR.
10. Report exact validation commands and results.
11. Report deviations and remaining concerns.
12. Suggest branch name, commit message, and PR title.

Do not implement subsequent PRs early.

Do not commit, push, merge, deploy, or modify production infrastructure unless explicitly instructed.

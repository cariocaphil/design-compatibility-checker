# Design Compatibility Checker — Project Specification

## 1. Project Purpose

**Design Compatibility Checker** is an AI-assisted application for evaluating how closely a UI design can be implemented using a target component library.

The application analyzes a supplied UI design, derives an implementation-neutral representation of its visible structure and semantics, and then evaluates that representation against a component library.

The resulting report should answer:

1. How compatible is the design with the target component library?
2. Which existing components and composition patterns should be used?
3. Which areas require customization?
4. Which areas likely require custom implementation?
5. What implementation risks or accessibility considerations are visible from the supplied design?

The project originated as an n8n proof-of-concept targeting Material UI.

The conventional application should preserve the validated conceptual pipeline while replacing n8n runtime orchestration with explicit application code, typed contracts, tests, APIs, and a conventional frontend.

---

# 2. Long-Term Product Direction

The long-term architecture must support configurable component libraries.

Conceptually:

```text
Design
   ↓
Implementation-neutral design analysis
   ↓
Semantic representation
   ↓
Target component library
   ↓
Library-specific retrieval
   ↓
Compatibility matching
   ↓
Compatibility report
```

Material UI is the first supported library.

Future versions may support:

* Ant Design
* Chakra UI
* shadcn/ui
* other public component libraries
* organization-specific component libraries

The architecture should eventually allow the same design to be evaluated against different libraries.

However, do not prematurely implement those capabilities.

The first development phase establishes Material UI parity with the existing prototype.

---

# 3. Core Architectural Principle

The most important boundary in the application is:

```text
              IMPLEMENTATION-NEUTRAL

Screenshot ──→ Vision Analysis ──┐
                                │
                                ├──→ DesignStructure
                                │
Figma ───────→ Figma Parser ────┘
                                ↓
                         SemanticAnalysis
                                ↓
                           DesignSummary

────────────────────────────────────────────────

                 LIBRARY-SPECIFIC

                         Retrieval
                                ↓
                    CompatibilityMatcher
                                ↓
                  CompatibilityAssessment
```

Design understanding must remain independent from the target component library wherever practical.

The vision analyzer must not identify Material UI components.

The Figma normalizer must not identify Material UI components.

Semantic analysis must describe the purpose and composition of UI structures rather than prematurely mapping them to a specific implementation library.

Component-library knowledge enters the pipeline at the retrieval/matching boundary.

---

# 4. Runtime Pipeline

The target runtime pipeline is:

```text
                         INPUT

              ┌──────────┴──────────┐
              │                     │
         Screenshot             Figma URL
              │                     │
              ↓                     ↓
       Vision Analyzer          Figma API
              │                     │
              │                Figma Normalizer
              │                     │
              └──────────┬──────────┘
                         ↓
                  DesignStructure
                         ↓
                  SemanticAnalyzer
                         ↓
                  SemanticAnalysis
                         ↓
               DesignSummaryProjector
                         ↓
                    DesignSummary
                         ↓
                Library Retriever
                         ↓
                 Retrieved Context
                         ↓
              CompatibilityMatcher
                         ↓
            CompatibilityAssessment
                         ↓
                    Report UI
```

Do not collapse this pipeline into one large model call.

Each stage should have a clearly defined responsibility and contract.

---

# 5. Technology Stack

## Frontend

Use:

* Next.js
* TypeScript
* App Router
* ESLint
* Prettier

Use a lightweight frontend testing setup appropriate to the generated application.

## Backend

Use:

* Python
* FastAPI
* Pydantic v2
* pydantic-settings
* Ruff
* pytest
* pytest-asyncio where appropriate

## AI

Initial model responsibilities:

### Visual analysis

OpenAI vision-capable model.

Purpose:

```text
Screenshot → DesignStructure
```

### Semantic analysis

OpenAI model.

Purpose:

```text
DesignStructure → SemanticAnalysis
```

### Compatibility matching

Anthropic Claude.

Purpose:

```text
DesignSummary
+
retrieved component-library knowledge
→
CompatibilityAssessment
```

Model identifiers must be configuration values rather than being scattered as hard-coded constants.

## Retrieval

Use:

* Qdrant
* OpenAI embeddings

Material UI documentation is initially retrieved from the existing Material UI vector collection.

---

# 6. Local Development Environment

The primary local container runtime is **Podman**.

The developer environment is macOS.

Docker Desktop must not be required.

Use:

```text
Podman
podman compose
Compose-compatible compose.yml
OCI-compatible container images
```

The application should be runnable with:

```bash
podman compose up --build
```

and stopped with:

```bash
podman compose down
```

Container definitions should remain portable to standard OCI-compatible production infrastructure.

Avoid Docker-specific assumptions including:

* Docker socket mounting
* Docker Desktop integrations
* Docker-only Compose extensions
* Docker-daemon dependencies

---

# 7. Container Networking

Container-to-container communication must use Compose service names.

For example:

```text
frontend → http://backend:8000
```

Do not use `localhost` for communication between containers.

Browser requests from the host may use exposed localhost ports.

Where Next.js requires separate internal and browser-facing API addresses, use configuration conceptually equivalent to:

```env
INTERNAL_API_URL=http://backend:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

# 8. Repository Structure

Use a monorepo.

Target structure:

```text
design-compatibility-checker/

frontend/
  app/
  components/
  lib/
  types/
  tests/

backend/
  app/
    api/
      routes/

    core/
      config.py

    schemas/

    services/
      design_vision.py
      figma.py
      semantic_analysis.py
      summary_projection.py
      mui_retriever.py
      compatibility_matcher.py

    clients/
      openai.py
      anthropic.py
      qdrant.py
      figma.py

    main.py

  tests/

.github/
  workflows/

compose.yml
.env.example
.gitignore
PROJECT_SPEC.md
IMPLEMENTATION_PLAN.md
README.md
```

The exact structure may evolve where justified by the implementation.

Do not create abstractions solely to satisfy this example structure.

Preserve clear responsibility boundaries.

---

# 9. Backend Architecture

Routes must remain thin.

Route handlers should primarily:

1. validate HTTP-level input
2. call the appropriate application/service layer
3. translate known application failures into appropriate HTTP responses
4. return validated response models

Do not put:

* prompt construction
* model-provider logic
* Figma parsing
* Qdrant queries
* domain transformations

directly into route handlers.

External providers should be isolated behind clients/services.

Deterministic transformations should use normal Python code.

---

# 10. Common Design Representation

Both supported input paths must converge on a common representation:

```text
DesignStructure
```

Conceptually:

```text
Screenshot
   ↓
Vision Analyzer
   │
   ├──────────→ DesignStructure
   │
Figma
   ↓
Figma Normalizer
```

The downstream pipeline should not need to know whether `DesignStructure` originated from a screenshot or Figma.

Missing information should be represented explicitly rather than hallucinated.

---

# 11. DesignStructure

The implementation-neutral design representation should preserve the important concepts already validated in the n8n prototype.

It should include models conceptually corresponding to:

```text
DesignStructure

LayoutDescription
DesignGroup
DesignElement
Separator
RepeatedStructure
Relationship
CustomPattern
```

Important information includes:

### Layout

* overall structure
* regions
* spacing
* alignment
* responsive hints where visible

### Groups

* identifier
* group type
* children

### Elements

* identifier
* visual role
* visible text
* visible state
* interaction hint
* confidence

### Separators

* orientation
* continuity
* associated group
* associated label/icon
* confidence

### Repeated structures

* item type
* visible item count
* visible items
* shared styling
* interaction pattern
* state
* confidence

### Relationships

Relationships between visible structures.

### Custom patterns

Visually meaningful structures that cannot be represented cleanly by the preceding categories.

---

# 12. Screenshot Analysis

Screenshot input must support:

* PNG
* JPEG/JPG

The user may provide optional textual context.

The vision stage must analyze visible frontend structure only.

It must not map the design to:

* React components
* Material UI components
* implementation-specific code

It should identify:

* page layout
* groups
* atomic UI elements
* repeated structures
* separators
* visible states
* relationships

It must not speculate about hidden behavior.

Structured output should be validated using Pydantic.

Prefer provider-supported structured output over manual JSON cleanup where practical.

---

# 13. Figma Analysis

The Figma path should:

1. accept a Figma design URL
2. validate the URL
3. extract the file key
4. call the Figma API
5. normalize relevant Figma graph information into `DesignStructure`

Initial Figma extraction should remain deliberately limited.

Important data includes:

* frames
* text nodes
* groups
* auto-layout containers
* layout direction
* spacing
* alignment

Do not attempt to implement a complete Figma parser unless later requirements justify it.

---

# 14. Semantic Analysis

The `SemanticAnalyzer` transforms:

```text
DesignStructure
→
SemanticAnalysis
```

It should identify:

* grouping structures
* section separators
* interaction intent
* repeated UI patterns
* layout semantics
* visual hierarchy
* compositional patterns

It should reason about **why** visible structures exist, not merely enumerate them.

For important semantic patterns, preserve both:

* semantic purpose
* visually meaningful composition

Do not infer unsupported:

* CTAs
* submit buttons
* continuation buttons
* future workflow steps
* hidden actions
* confirmation flows
* sticky actions
* modal behavior

When behavior is ambiguous, preserve the ambiguity.

Do not invent behavior.

---

# 15. Semantic Models

Use explicit Pydantic models conceptually including:

```text
SemanticPattern
AmbiguousPattern
SemanticAnalysis
```

A semantic pattern should be able to represent:

* name
* type
* visual evidence
* purpose
* importance
* implementation implications
* confidence

Implementation implications must remain library-neutral at this stage.

Do not use fields such as:

```text
muiImplications
```

in the generic semantic representation.

Use an implementation-neutral concept such as:

```text
implementationImplications
```

if required.

---

# 16. Summary Projection

The transformation:

```text
DesignStructure
+
SemanticAnalysis
→
DesignSummary
```

must be deterministic application code.

It must not use an LLM.

Its purpose is to reduce the input to the information necessary for compatibility matching while preserving implementation-relevant structure.

It should retain relevant:

* layout
* groups
* elements
* separators
* repeated structures
* semantic patterns
* ambiguities

The projector must have focused unit tests.

---

# 17. Component-Library Retrieval

Retrieval is library-specific.

For the initial Material UI implementation, retrieval should use the existing Qdrant knowledge base where available.

Initial collection:

```text
mui_component_docs
```

Retrieval should validate relevant:

* component suitability
* variants
* props
* accessibility behavior
* layout constraints
* implementation feasibility
* composition patterns
* customization requirements

Retrieval should be targeted.

Do not retrieve large generic documentation dumps.

---

# 18. Compatibility Matching

The compatibility matcher evaluates:

```text
DesignSummary
+
Retrieved Library Context
→
CompatibilityAssessment
```

For the initial implementation, the target library is Material UI.

The matcher should determine:

1. overall compatibility
2. recommended components
3. recommended composition patterns
4. meaningful customization requirements
5. implementation risks
6. concrete accessibility implications where relevant

Prefer standard component-library composition before custom implementation.

Prefer fewer high-value findings over exhaustive output.

---

# 19. Compatibility Assessment Model

Use explicit structured output.

Conceptual models include:

```text
CompatibilityAssessment

CompatibilitySummary
LayoutMapping
ElementMapping
GroupMapping
SemanticImplementationMapping
CustomImplementationWarning
```

## Compatibility Score

Range:

```text
0–100
```

The score represents how closely the visible design can be reproduced using standard target-library components and composition patterns.

It must not represent application-logic complexity or unseen behavior.

## Confidence

Range:

```text
0–1
```

## Customization Levels

Allowed values:

```text
none
minor
medium
high
```

Customization effort refers to customization beyond standard component composition and ordinary theming.

It is not an estimate of total implementation effort.

## Warning Severity

Allowed values:

```text
low
medium
high
```

---

# 20. Compatibility Output Philosophy

The report should prioritize implementation signal.

Avoid exhaustive one-to-one mapping of obvious elements.

Prefer findings that help a frontend developer understand:

* what can be implemented natively
* what requires composition
* what requires styling/theming
* what requires meaningful customization
* what may require custom implementation

Repeated elements should be consolidated where possible.

Reasons should remain concise.

---

# 21. Accessibility

Accessibility findings must be grounded in visible design or concrete implementation consequences.

Do not invent generic accessibility warnings.

Relevant examples may include:

* decorative icon handling
* labelled or interrupted dividers
* keyboard semantics for composite controls
* focus implications of non-standard interaction patterns

Accessibility should remain part of compatibility assessment rather than becoming a generic accessibility audit.

A dedicated accessibility-analysis capability may be considered separately in a future phase.

---

# 22. Report UI

The frontend report should present at least:

## Summary

* compatibility score
* customization effort
* confidence
* concise overall assessment

## Recommended Implementation

Show:

* design area
* recommended component/component composition
* customization level

## Significant Customizations

Prioritize:

```text
medium
high
```

customization requirements.

## Accessibility Considerations

Show only concrete relevant findings.

## Risks and Open Questions

Show implementation warnings ordered by severity.

## Original Design

For screenshot analyses, show the submitted screenshot with the report.

---

# 23. Error Handling

The application must handle failures explicitly.

Representative failures include:

* unsupported image type
* missing image
* excessive upload size
* malformed Figma URL
* invalid Figma file key
* Figma API failure
* OpenAI failure
* Anthropic failure
* malformed structured model response
* Qdrant failure
* retrieval failure
* empty retrieval result

Frontend errors should be understandable to the user.

Backend logs should contain sufficient diagnostic context.

Do not expose raw internal stack traces or credentials.

---

# 24. Configuration and Secrets

Use `pydantic-settings` for centralized backend configuration.

Environment configuration should include concepts such as:

```env
OPENAI_API_KEY=
OPENAI_VISION_MODEL=
OPENAI_SEMANTIC_MODEL=

ANTHROPIC_API_KEY=
ANTHROPIC_MATCHER_MODEL=

FIGMA_ACCESS_TOKEN=

QDRANT_URL=
QDRANT_API_KEY=
QDRANT_COLLECTION=mui_component_docs
```

Provide:

```text
.env.example
```

with placeholders only.

Never commit:

* API keys
* tokens
* credentials
* authorization headers
* production secrets

Environment files containing actual secrets must be ignored by Git.

---

# 25. Security

Uploaded files must be validated.

Do not log:

* API keys
* access tokens
* authorization headers
* credentials

Do not return sensitive provider errors directly to clients.

The Figma token exposed in the original n8n prototype export must never be committed to the new repository.

All provider credentials must be environment-based.

---

# 26. Backend Quality Standards

Use Ruff for linting and formatting.

The backend should support local checks equivalent to:

```bash
ruff check .
ruff format --check .
pytest
```

Local automatic formatting should be available through:

```bash
ruff format .
```

Use `pyproject.toml` for Python project/tool configuration where practical.

---

# 27. Frontend Quality Standards

Configure:

* ESLint
* Prettier
* TypeScript type checking
* frontend tests

Provide package scripts conceptually equivalent to:

```text
lint
format
format:check
typecheck
test
build
```

Do not rely on the production build alone as the TypeScript quality gate.

---

# 28. Testing Strategy

Tests should emphasize deterministic behavior and application boundaries.

## Backend Unit Tests

Prioritize:

* Figma URL parsing
* Figma file-key extraction
* Figma normalization
* Pydantic validation
* summary projection
* compatibility-result validation
* score/confidence bounds

## Service Tests

Mock external services and test pipeline orchestration.

Do not make paid model calls in automated CI.

Mock where appropriate:

* OpenAI
* Anthropic
* Figma
* Qdrant

## API Tests

Cover successful and representative failure cases.

## Frontend Tests

Prioritize important behavior:

* input selection
* submission
* loading state
* error state
* report rendering

Avoid excessive low-value snapshot testing.

---

# 29. Continuous Integration

GitHub Actions CI must run on:

```text
push
pull_request
```

CI should mirror local quality checks.

## Backend

Run:

```text
Ruff lint
Ruff formatting check
pytest
```

## Frontend

Run:

```text
dependency installation
ESLint
Prettier formatting check
TypeScript type check
tests
production build
```

CI must fail when required quality checks fail.

External services must be mocked where appropriate.

Production credentials must not be required by CI.

---

# 30. Development Workflow

Development should proceed in small, coherent pull requests.

Each implementation PR should:

1. address one bounded architectural slice
2. preserve existing conventions
3. include appropriate tests
4. pass relevant local quality checks
5. avoid implementing later-phase scope
6. document meaningful deviations from this specification

Before implementation, Cursor should:

1. read `PROJECT_SPEC.md`
2. read `IMPLEMENTATION_PLAN.md`
3. inspect the current repository
4. identify relevant existing architecture and conventions
5. report the proposed files and changes
6. identify risks or ambiguities

Do not perform broad rewrites when a bounded change is sufficient.

---

# 31. Pull Request Validation

Before considering an implementation PR complete, run all applicable repository checks.

Backend checks should include, where applicable:

```bash
ruff check .
ruff format --check .
pytest
```

Frontend checks should include, where applicable:

```bash
pnpm lint
pnpm format:check
pnpm typecheck
pnpm test
pnpm build
```

Podman/container-related PRs should additionally validate the relevant Compose workflow.

Fix failures introduced by the PR.

If a check cannot be run, state explicitly:

* which check was not run
* why
* what remains unverified

---

# 32. Implementation Reports

After each implementation task, provide a concise report containing:

* files created
* files modified
* behavior implemented
* tests added or changed
* exact validation commands run
* results of those commands
* deviations from `PROJECT_SPEC.md`
* unresolved concerns
* suggested branch name
* suggested commit message
* suggested PR title

Do not claim that code was:

* committed
* pushed
* merged
* deployed

unless that action was explicitly requested and actually performed.

---

# 33. Phase 1 — Conventional Application + MUI Parity

The first phase migrates the existing n8n runtime into conventional application code.

Phase 1 must establish:

* Next.js frontend
* FastAPI backend
* Podman-first local development
* screenshot input
* Figma URL input
* common `DesignStructure`
* semantic analysis
* deterministic summary projection
* Material UI retrieval
* compatibility matching
* structured compatibility assessment
* report UI
* automated tests
* linting
* formatting
* type checking
* GitHub Actions CI
* project documentation

The primary success criterion is:

> Functional Material UI parity with the existing n8n proof-of-concept, expressed as maintainable, tested conventional application code.

---

# 34. Phase 1 Explicit Exclusions

Phase 1 does not include:

* production deployment
* continuous deployment
* Azure infrastructure
* user authentication
* persistent analysis history
* teams/workspaces
* billing
* multiple component libraries
* component-library selection
* Ant Design
* Chakra UI
* shadcn/ui
* cross-library comparison
* library recommendation
* generic component-library configuration
* library-management UI
* migration of the scheduled n8n ingestion workflow
* generic documentation ingestion

Do not implement these opportunistically while working on Phase 1.

---

# 35. Future Direction

After Material UI parity has been established, subsequent phases may introduce:

```text
Phase 2
Production deployment and CD

Phase 3
Component-library abstraction

Phase 4
Second component library

Phase 5
Generic component-library ingestion

Phase 6
Cross-library comparison/recommendation
```

These phases are directional rather than authorization to implement them.

Each later phase should receive its own bounded specification before implementation begins.

---

# 36. Guiding Engineering Principles

When making implementation decisions, prefer:

**Explicit contracts over loosely structured JSON.**

**Small services over giant orchestration functions.**

**Deterministic code over unnecessary model calls.**

**Implementation-neutral analysis over premature library coupling.**

**Provider isolation over API calls scattered through application code.**

**Focused retrieval over large context dumps.**

**Tests for deterministic logic over testing implementation details.**

**Small reviewable PRs over large generated changes.**

**Podman/OCI portability over Docker Desktop dependencies.**

**Existing repository conventions over speculative abstraction.**

**Working, validated increments over premature future-proofing.**

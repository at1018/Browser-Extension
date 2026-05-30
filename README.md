# AI Visual Copilot

AI Visual Copilot is a scalable SaaS platform that starts as a Chrome Extension and evolves into a full AI-enabled workflow engine for screenshot understanding, persona-aware actions, and multi-model orchestration.

## Vision

Same screenshot → different results.

The platform automatically detects screenshots, extracts visual and textual content, identifies user persona, routes requests through LangGraph workflows, selects the optimal AI model, and returns personalized tasks and responses.

## Phase 1 Deliverables

- Monorepo folder structure
- Product requirements documentation
- Architecture overview
- API specification
- Deployment planning
- Roadmap and implementation guidance

## Repository Layout

- `apps/` — host for future web or mobile applications
- `extension/` — Chrome Extension source and UI
- `backend/` — FastAPI backend, AI orchestration, and service modules
- `packages/shared-types/` — shared TypeScript interfaces and models
- `packages/shared-prompts/` — reusable prompts and prompt templates
- `packages/shared-utils/` — shared helper utilities
- `docs/` — product requirements, architecture, API, deployment, roadmap
- `infra/` — infrastructure definitions and cloud configuration
- `scripts/` — automation, scaffolding, migration, and deployment helpers

## Next Step

Proceed to Phase 2: implement the Chrome Extension scaffold with screenshot capture, popup UI, overlay UI, and background worker.

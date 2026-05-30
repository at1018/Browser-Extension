# Architecture Overview

## High-Level Architecture

AI Visual Copilot is built as a modular monorepo with separation of concerns across frontend, backend, shared packages, and infrastructure.

- `extension/` — Chrome Extension UI, screenshot capture, clipboard detection, overlay, popup.
- `backend/` — FastAPI services, AI orchestration, provider adapters, persona engine, intent detection, workflow manager.
- `packages/` — shared cross-service code, prompts, and type definitions.
- `docs/` — design, API, deployment, roadmap.
- `infra/` — cloud infrastructure and deployment definitions.

## Core Backend Layers

1. **API Layer**
   - Health API
   - Screenshot ingestion API
   - Analysis API
   - User/profile API
   - History and workflow API

2. **Vision & OCR Layer**
   - Tesseract OCR service
   - Vision provider adapters
   - Metadata extraction pipeline

3. **AI Provider Abstraction**
   - Base provider interface
   - OpenAI, Gemini, Claude, Bedrock, Ollama adapters
   - Common methods: `analyze_image()`, `generate_response()`, `classify_intent()`, `health_check()`

4. **Intent & Persona Engine**
   - `intent_detector.py`
   - Persona router and persona sub-engines
   - Role-specific actions and prompts

5. **LangGraph Workflow Manager**
   - Graph-based orchestration of agents
   - ScreenshotAgent → OCRAgent → VisionAgent → IntentAgent → PersonaAgent → ModelRouterAgent → Specialized Agent → ResponseAgent

6. **Data Layer**
   - Supabase / PostgreSQL persistence
   - tables: `users`, `screenshots`, `analysis_results`, `intent_history`, `persona_history`, `workflows`, `subscriptions`, `billing_events`, `activity_logs`

## Multi-Model Routing Strategy

- Use persona and intent to determine the optimal model.
- Prioritize cost and latency while preserving accuracy.
- Default fallback order: OpenAI → Claude → Gemini → Bedrock.
- Example mappings:
  - `error_bug`, `code` → Claude
  - `ui_design` → GPT-4o / Gemini Vision
  - `product` → Gemini
  - `chart_graph` → Claude

## Persona-Aware Workflows

Each persona has a dedicated workflow folder with:

- `actions.py` — persona-specific actions
- `prompts.py` — tailored prompt templates
- `workflow.py` — workflow orchestration and step sequencing

Supported personas:
- developer
- qa
- student
- designer
- shopper
- analyst

## Deployment and Observability

- Containerized backend with Docker
- GitHub Actions for CI/CD
- Supabase for auth, database, storage
- Stripe for billing
- OpenTelemetry and Sentry for monitoring and tracing

# Implementation Roadmap

## Phase 1 — Planning & Scaffolding

- Create monorepo structure
- Document product requirements
- Define architecture
- Specify API contracts
- Plan deployment and observability

## Phase 2 — Chrome Extension

- Build React + TypeScript + Tailwind extension UI
- Implement screenshot capture and paste detection
- Add popup and overlay flows
- Wire background worker for screenshot upload
- Document extension usage

## Phase 3 — FastAPI Backend

- Implement health, screenshot, analysis, user, and history APIs
- Add OpenAPI documentation
- Build provider abstraction layer skeleton
- Implement basic persona routing placeholder

## Phase 4 — OCR + Vision Layer

- Add Tesseract OCR pipeline
- Add vision provider adapters for GPT-4o, Gemini, and Claude
- Create structured extraction output

## Phase 5 — Multi-Model Providers

- Implement provider adapters for OpenAI, Gemini, Claude, Bedrock, Ollama
- Add provider tests and health checks

## Phase 6 — Intent Detection

- Implement intent classifier
- Add unit tests for intent detection

## Phase 7 — Persona Engine

- Build persona router and persona-specific workflows
- Implement developer, QA, student, designer, shopper, analyst engines

## Phase 8 — LangGraph Workflows

- Create specialized LangGraph agents
- Build graph orchestration and visualization
- Validate workflow runtime

## Phase 9 — Action Engine

- Implement persona-specific actions by category
- Add action service and execution logging

## Phase 10 — Supabase Integration

- Add authentication
- Persist data to PostgreSQL
- Implement storage for screenshots

## Phase 11 — Stripe Billing

- Add subscription plans and checkout flow
- Track usage and billing events

## Phase 12 — Observability

- Add OpenTelemetry, Sentry, metrics
- Add logs and trace correlation

## Phase 13 — Deployment

- Add Docker and GitHub Actions pipelines
- Deploy backend and extension assets
- Support cloud hosting options: Railway, AWS, Render

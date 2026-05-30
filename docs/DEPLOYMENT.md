# Deployment Plan

## Deployment Goals

- Containerize the backend
- Enable CI/CD with GitHub Actions
- Deploy frontend extension assets and backend services
- Use Supabase for auth, database, and storage
- Support Stripe billing integration
- Add observability and tracing

## Docker Strategy

- `backend/Dockerfile` for FastAPI service
- `extension` build artifacts served independently or via static host
- Local development using Docker Compose when needed

## GitHub Actions

- Workflow for linting, tests, build, and container validation
- Deploy backend container to preferred cloud provider
- Publish extension package or deploy extension assets to a static host

## Infrastructure

- `infra/` contains IaC definitions for:
  - Supabase project configuration
  - PostgreSQL schema migrations
  - Stripe webhook and environment setup
  - Optional AWS / Render / Railway deployment templates

## Environment Configuration

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `STRIPE_API_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `CLAUDE_API_KEY`
- `BEDROCK_ENDPOINT`
- `OLLAMA_API_URL`

## Deployment Workflow

1. Run local containerized backend and validate health.
2. Run automated tests and API schema checks.
3. Build extension and package manifest.
4. Deploy backend to cloud target.
5. Configure Supabase and Stripe secrets.
6. Enable monitoring and logging.

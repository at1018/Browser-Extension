# API Specification

## Authentication

- Supabase Auth with JWT tokens
- `Authorization: Bearer <token>` required for protected endpoints

## Endpoints

### GET /health

- Description: Service health check
- Response: `{ "status": "ok" }`

### POST /api/screenshots/upload

- Description: Upload screenshot image or submit screenshot metadata
- Request body:
  - `image_base64` (string)
  - `source` (string)
  - `meta` (object)
- Response: `{ "screenshot_id": "...", "status": "received" }`

### POST /api/screenshots/analyze

- Description: Analyze a screenshot using OCR and vision pipeline
- Request body:
  - `screenshot_id` (string)
  - `persona` (string)
  - `context` (object)
- Response:
  - `analysis_id` (string)
  - `intent` (string)
  - `persona` (string)
  - `results` (object)

### GET /api/users/me

- Description: Retrieve current user profile and persona settings
- Response: user profile, persona preferences, subscription status

### GET /api/history/screenshots

- Description: List screenshot history for a user
- Response: list of screenshot records with analysis summaries

### GET /api/history/analysis/{analysis_id}

- Description: Retrieve a detailed analysis result
- Response: structured analysis payload, intent logs, persona logs, model execution metadata

### POST /api/workflows/execute

- Description: Execute a defined LangGraph workflow for a screenshot
- Request body:
  - `workflow_id` (string)
  - `screenshot_id` (string)
  - `persona` (string)
  - `input` (object)
- Response:
  - `execution_id` (string)
  - `status` (string)
  - `output` (object)

### GET /api/subscriptions/plans

- Description: List available subscription plans
- Response: plan definitions and limits

### POST /api/billing/checkout

- Description: Create Stripe checkout session for subscription upgrade
- Request body:
  - `plan_id` (string)
  - `user_id` (string)
- Response:
  - `checkout_url` (string)

## Data Models

### Screenshot Record

- `id`
- `user_id`
- `source`
- `uploaded_at`
- `status`
- `analysis_summary`

### Analysis Result

- `id`
- `screenshot_id`
- `intent`
- `persona`
- `extracts`
- `model_metadata`
- `created_at`

### Workflow Execution

- `id`
- `workflow_id`
- `screenshot_id`
- `persona`
- `steps`
- `status`
- `output`
- `started_at`
- `completed_at`
